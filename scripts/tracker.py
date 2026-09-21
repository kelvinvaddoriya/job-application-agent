"""Tracker CLI for the two application CSVs.

Query and update the tracker WITHOUT loading its contents into the model
context.

STORAGE (moved off Tracking.xlsx on 2026-09-07): two CSVs, split by who
writes them, joined on a stable ID ("a0001", ...):

  application/applications.csv  ID | Date Applied | Company | Position |
        Location | Reference Code | Status | CV Used | Cover Letter | Portal |
        Notes          - written by local batch sessions (append, set Status)
  application/outcomes.csv      ID | Outcome | Outcome Detail
                       - written by the daily email-check routine

The split is the point: the routine and a local batch no longer write the same
file, so a git merge of the two is an ordinary text merge and needs no driver.
Both files are one physical line per record. The only overlap left is a local
`update --outcome` during an audit, which is rare and human-initiated.

Usage:
  python scripts/tracker.py check "Company"     dup + 90-day company-cap verdict
        (a Rejected/Ghosted row is closed: it frees its cap slot and waives
         the cap unless 2+ applications are still open - see is_closed)
  python scripts/tracker.py add --company X --position Y [--location --ref
        --status --cv --cl --portal --notes --date] [--allow-duplicate]
  python scripts/tracker.py update "Company" "position substring" [--ref ...]
        [--status --notes --cv --cl --portal --date --location
         --outcome --outcome-detail]
  python scripts/tracker.py queue               rows with status Found/Qualified
  python scripts/tracker.py stats               status counts
  python scripts/tracker.py emails [--status X]  every email-channel row +
        the Gmail sent-query that proves whether it actually went out

Statuses: Found, Qualified, Drafted, Submitted, Skipped, Blocked, NeedsUser.
Put the reason/confirmation in --notes.

`add` refuses a row whose company AND position already exist, naming the row
it collided with; re-applying after a rejection is legitimate, so override it
with --allow-duplicate once you have looked at that row.

EMAIL-ONLY APPLICATIONS: this script cannot see Gmail, so a sent email is
invisible to it. Two rules keep that gap closed (both added 2026-08-15 after
Clar AI / Next Intelligence / Hutter und Unger were each emailed twice):
  1. Record the channel as --portal "email:<recipient>" and, the moment the
     draft is handed to the user, set --status Submitted --outcome Awaiting.
     A handed-off draft is NOT NeedsUser - leaving it NeedsUser is what made
     a later backlog-drain rewrite and resend it.
  2. `check` prints an EMAIL GATE for any company with an email-channel row.
     Run the Gmail query it prints BEFORE writing a new draft.

Outcomes (from reading employer reply emails) - match existing values:
Rejected, Ghosted, Awaiting, In Progress, Interview, Offer. Put specifics
(dates, next steps) in --outcome-detail.

The interview warning is keyed off STATUS ONLY ("process"/"interview"), so
when a process ends, close --status in the same turn as --outcome or the
company stays blocked for every future batch (2026-08-22: three rows with a
recorded rejection were still warning).
"""
import argparse
import csv
import datetime as dt
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FILE = os.path.join(ROOT, "application", "applications.csv")
APP_HEADERS = ["ID", "Date Applied", "Company", "Position", "Location",
               "Reference Code", "Status", "CV Used", "Cover Letter",
               "Portal", "Notes"]
OUTCOME_HEADERS = ["ID", "Outcome", "Outcome Detail"]
SUFFIXES = {"gmbh", "ag", "se", "kg", "mbh", "co", "inc", "ltd", "pvt", "group", "holding"}
EMPLOYER_FACING = ("submitted", "applied", "in process", "drafted", "qualified", "needs")
EMAIL_RX = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]*[\w-]")
# A row is email-CHANNEL only if it says so: Portal "email:<addr>" (the current
# convention) or an explicit send-email marker in Notes. Matching any address
# anywhere pulled in 71 rows, nearly all of them ATS *confirmation senders*.
EMAIL_CHANNEL_RX = re.compile(
    r"send email|sent by email|email draft|e-?mail draft|gmail draft|"
    r"applied via email|bewerbung per e-?mail|per e-?mail bewerben", re.I)
# addresses that are never an application recipient, only a sender
NOT_RECIPIENT = ("noreply", "no-reply", "donotreply", "do-not-reply", "system@",
                 "notification@", "notifications@", "antwort@", "@myworkday.com",
                 "@successfactors.com", "@successfactors.eu", "@m.personio.com",
                 "@app.softgarden.io")
# Your own address(es), so `emails` does not read a self-addressed row as a
# recipient. Same JOBAGENT_EMAIL the rest of the project uses - one address
# everywhere is the rule (see README "One email, everywhere").
_OWN = [e for e in (os.environ.get("JOBAGENT_EMAIL", ""),
                    os.environ.get("JOBAGENT_EMAIL_FALLBACK", "")) if e]
OWN_RX = re.compile("|".join(re.escape(e) for e in _OWN) if _OWN else r"(?!)", re.I)


def norm(name):
    words = re.findall(r"[a-z0-9]+", str(name or "").lower())
    return " ".join(w for w in words if w not in SUFFIXES)


def recipients(r):
    """Employer address(es) this row was/would be applied to by email.

    The tracker has no Gmail access, so this is how an email-channel row is
    recognised at all - see the EMAIL-ONLY APPLICATIONS note in the docstring.
    Returns [] for portal applications, including ones whose Notes happen to
    quote the ATS address that sent the confirmation.
    """
    portal, notes = str(r[8] or ""), str(r[9] or "")
    if portal.lower().startswith("email:"):
        blob = portal
    elif EMAIL_CHANNEL_RX.search(notes) or EMAIL_CHANNEL_RX.search(portal):
        blob = portal + " " + notes
    else:
        return []
    return sorted({a for a in EMAIL_RX.findall(blob)
                   if not OWN_RX.search(a)
                   and not any(bad in a.lower() for bad in NOT_RECIPIENT)})


def gmail_query(addrs):
    inner = " OR ".join(f"to:{a}" for a in sorted(set(addrs)))
    return f"in:anywhere ({inner})" if len(set(addrs)) > 1 else f"in:anywhere {inner}"


def parse_date(v):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(str(v).strip(), fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def outcomes_path(app_path):
    return os.path.join(os.path.dirname(app_path), "outcomes.csv")


def read_csv(path, headers):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        data = list(csv.reader(f))
    if not data:
        return []
    if data[0][:1] == headers[:1]:
        data = data[1:]
    width = len(headers)
    return [(r + [""] * width)[:width] for r in data if any(x.strip() for x in r)]


def write_csv(path, headers, rows):
    # newline="" + \n keeps one physical line per record; .gitattributes pins
    # these files to LF so git's line merge maps 1:1 onto records.
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(headers)
            w.writerows(rows)
    except PermissionError:
        sys.exit(f"BLOCKED: {os.path.basename(path)} is open in Excel"
                 " - ask the user to close it.")


def load(path):
    """(ids, rows) where rows are the 12-wide tuples every command expects.

    Index 10/11 (Outcome, Outcome Detail) are joined in from outcomes.csv, so
    the split storage is invisible above this function - cmd_check still reads
    r[10] to discharge rejected rows from the 90-day cap.
    """
    apps = read_csv(path, APP_HEADERS)
    outs = {r[0]: r for r in read_csv(outcomes_path(path), OUTCOME_HEADERS)}
    ids = [r[0] for r in apps]
    rows = []
    for r in apps:
        o = outs.get(r[0], ["", "", ""])
        rows.append(r[1:11] + [o[1], o[2]])
    return ids, rows


def save(path, ids, rows):
    """Write both files back, each keeping only the columns it owns."""
    write_csv(path, APP_HEADERS, [[i] + r[:10] for i, r in zip(ids, rows)])
    kept = [[i, r[10], r[11]] for i, r in zip(ids, rows) if r[10] or r[11]]
    write_csv(outcomes_path(path), OUTCOME_HEADERS, kept)


def next_id(ids):
    n = max((int(i[1:]) for i in ids if re.fullmatch(r"a\d+", i)), default=0)
    return f"a{n + 1:04d}"


CLOSED_OUTCOMES = ("rejected", "ghosted")


def is_closed(r):
    """True if this row's process is over, so it no longer occupies a cap slot.

    the user's rule (2026-08-22): a rejection ends the company's process, so it
    neither consumes a 90-day cap slot nor keeps the company capped. Ghosted
    counts the same way (his call) - a no-reply application is dead in
    practice. Checks BOTH columns: 67 rows carry a terminal
    Outcome="Rejected"/"Ghosted" while Status is still the employer-facing
    value it had at submit time, and every one of those was counting against
    the cap.
    """
    return (str(r[5] or "").strip().lower().startswith(("reject", "ghost"))
            or str(r[10] or "").strip().lower() in CLOSED_OUTCOMES)


def clean(s):
    # keep tracker values ASCII-safe; en/em dashes have been mangled before
    return "" if s is None else str(s).replace("–", "-").replace("—", "-")


def cmd_check(args):
    target = norm(args.company)
    if not target:
        sys.exit("empty company name")
    today = dt.date.today()
    matches, recent, interview = [], 0, False
    closed, mailed = [], {}
    _, rows = load(args.file)
    for r in rows:
        rnorm = norm(r[1])
        if rnorm and (target in rnorm or rnorm in target):
            matches.append(r)
            for a in recipients(r):
                mailed.setdefault(a, []).append(r)
            status = str(r[5] or "").lower()
            d = parse_date(r[0])
            if is_closed(r):
                closed.append((d, r))
            elif any(status.startswith(k) for k in EMPLOYER_FACING):
                if d is None or (today - d).days <= 90:
                    recent += 1
            if "process" in status or "interview" in status:
                interview = True
    for r in matches:
        print(f"  row: {r[0]} | {r[1]} | {r[2]} | status={r[5]} | ref={r[4]}")
    recent_pkgs = 0
    # Companies/ (the pre-2026-07 layout) was retired 2026-09-07 to
    # ../Companies_archive_2026-09-07/. It only ever printed a provenance line -
    # it never fed recent_pkgs - and every application it stood for has a tracker
    # row. Application_Packages is the only folder source now.
    d = os.path.join(ROOT, "Application_Packages")
    if os.path.isdir(d):
        tokens = [t for t in target.split() if len(t) >= 3] or [target.replace(" ", "")]
        for name in os.listdir(d):
            if any(t in norm(name).replace(" ", "") for t in tokens):
                age = (today - dt.date.fromtimestamp(
                    os.path.getmtime(os.path.join(d, name)))).days
                print(f"  folder: Application_Packages/{name} ({age}d old)")
                if age <= 90:
                    recent_pkgs += 1
    if mailed:
        print("EMAIL GATE: this company has been applied to by email before.")
        for a, rs in sorted(mailed.items()):
            when = ", ".join(str(parse_date(x[0]) or "?") for x in rs)
            print(f"  {a} ({when})")
        print(f"  Gmail-search BEFORE drafting: {gmail_query(mailed)}")
        print("  A sent message there means this role may already be applied to -"
              " the tracker cannot see Gmail.")
    if interview:
        print("WARNING: active interview process at this company - ask the user before applying.")
    # Cap waiver (the user, 2026-08-22): a rejection/ghosting ends the process,
    # so it lifts the 90-day cap for that company - UNLESS 2+ applications are
    # still genuinely open, which is the spam case the cap exists to prevent.
    # The waiver also clears a folder-driven cap: the Application_Packages
    # matcher is fuzzy (Siemens Energy matched Arteus_Energy and SFC_Energy).
    cap = max(recent, recent_pkgs)
    waived = bool(closed) and recent < 2
    if waived:
        when = max((d for d, _ in closed if d), default=None)
        print(f"CAP WAIVED: {len(closed)} closed application(s) at this company"
              f"{f' (latest {when})' if when else ''} - a rejection/ghosting ends"
              f" the process, so the 90-day cap does not apply."
              f" Still open <=90d: {recent}.")
    print(f"tracker rows: {len(matches)} | open employer-facing <=90d: {recent}"
          f" (+{recent_pkgs} pkg folders) | "
          f"verdict: {'OK' if waived or cap < 2 else 'CAP_REACHED'}")


def cmd_add(args):
    ids, rows = load(args.file)
    company, position = norm(args.company), str(args.position).strip().lower()
    if not args.allow_duplicate:
        for i, r in zip(ids, rows):
            if norm(r[1]) == company and str(r[2] or "").strip().lower() == position:
                sys.exit(f"DUPLICATE: {i} already holds {r[1]} | {r[2]}"
                         f" (date={r[0]}, status={r[5]}, outcome={r[10] or '-'}).\n"
                         "Re-applying after a rejection is fine - look at that row,"
                         " then re-run with --allow-duplicate.")
    rid = next_id(ids)
    ids.append(rid)
    rows.append([clean(x) for x in [
        args.date or dt.date.today().isoformat(), args.company, args.position,
        args.location, args.ref, args.status, args.cv, args.cl, args.portal,
        args.notes]] + ["", ""])
    save(args.file, ids, rows)
    print(f"added {rid}: {args.company} | {args.position} | {args.status}")


def cmd_update(args):
    ids, rows = load(args.file)
    target = norm(args.company)
    hits = []
    for i, r in zip(ids, rows):
        if target in norm(r[1]) and args.position.lower() in str(r[2] or "").lower():
            if args.ref and args.ref not in str(r[4] or ""):
                continue
            # --id wins outright: the only way to hit one of two rows whose
            # refs are substrings of each other (e.g. 4427580026 vs
            # linkedin_4427580026), which --ref alone can never separate.
            if args.id and i != args.id:
                continue
            hits.append((i, r))
    if not hits:
        sys.exit("no matching row - use 'add' or check spelling")
    if len(hits) > 1:
        for i, r in hits:
            print(f"  {i}: {r[1]} | {r[2]} | ref={r[4]} | status={r[5]}")
        sys.exit("ambiguous - disambiguate with --ref or --id")
    rid, row = hits[0]
    updates = {0: args.date, 1: args.newcompany, 3: args.location,
               4: args.newref, 5: args.status,
               6: args.cv, 7: args.cl, 8: args.portal, 9: args.notes,
               10: args.outcome, 11: args.outcome_detail}
    for col, val in updates.items():
        if val is not None:
            row[col] = clean(val)
    save(args.file, ids, rows)
    print(f"updated {rid}: status={args.status}")


def cmd_queue(args):
    wanted = (args.status.lower(),) if args.status else ("found", "qualified")
    n = 0
    _, rows = load(args.file)
    for r in rows:
        if str(r[5] or "").lower().startswith(wanted):
            d = parse_date(r[0])
            print(f"  {d or '?'} | {r[5]} | {r[1]} | {r[2]} | {r[4]}")
            if args.verbose:
                print(f"      portal: {r[8] or '-'}")
                print(f"      notes:  {r[9] or '-'}")
            n += 1
    print(f"{n} queued")


def cmd_emails(args):
    """Every email-channel row, plus one Gmail query that verifies them all.

    Run the printed query with the Gmail MCP and compare: a row with no sent
    message was never actually sent, and a row with two is a duplicate.
    """
    wanted = args.status.lower() if args.status else None
    hits, addrs = [], []
    _, rows = load(args.file)
    for r in rows:
        to = recipients(r)
        if not to:
            continue
        if wanted and not str(r[5] or "").lower().startswith(wanted):
            continue
        hits.append((parse_date(r[0]), to[0], r))
        addrs.extend(to)
    for d, a, r in sorted(hits, key=lambda h: (h[0] is None, h[0])):
        print(f"  {d or '?'} | {r[5]} | {a} | {r[1]} | {r[2]}")
    print(f"{len(hits)} email-channel rows, {len(set(addrs))} addresses")
    if hits:
        recent = [a for d, a, _ in hits if d and (dt.date.today() - d).days <= args.days]
        if recent:
            print(f"\nGmail query (last {args.days}d, {len(set(recent))} addresses):")
            print(f"  {gmail_query(recent)}")
        print("Compare sent-message count per address: 0 = never sent, 2+ = duplicate.")


def cmd_stats(args):
    from collections import Counter
    _, rows = load(args.file)
    c = Counter(str(r[5]) for r in rows)
    for k, v in c.most_common():
        print(f"  {v:3d}  {k}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", default=DEFAULT_FILE,
                   help="applications.csv (outcomes.csv is its sibling)")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check")
    c.add_argument("company")

    for name in ("add", "update"):
        s = sub.add_parser(name)
        if name == "add":
            s.add_argument("--company", required=True)
            s.add_argument("--position", required=True)
            s.add_argument("--status", default="Found")
            s.add_argument("--allow-duplicate", dest="allow_duplicate",
                           action="store_true",
                           help="add even though company+position already exists")
        else:
            s.add_argument("company")
            s.add_argument("position")
            s.add_argument("--ref", help="match filter when ambiguous")
            s.add_argument("--id",
                           help="exact row ID (printed by the 'ambiguous' "
                                "error); use when refs overlap")
            s.add_argument("--newref", help="set Reference Code")
            s.add_argument("--newcompany",
                           help="rename Company (use the real employer name so "
                                "`check` can find the row later)")
            s.add_argument("--status")
            s.add_argument("--outcome", help="Rejected/Ghosted/Awaiting/In Progress/Interview/Offer")
            s.add_argument("--outcome-detail", dest="outcome_detail", help="free-text detail for Outcome")
        s.add_argument("--location")
        s.add_argument("--cv")
        s.add_argument("--cl")
        s.add_argument("--portal")
        s.add_argument("--notes")
        s.add_argument("--date")
        if name == "add":
            s.add_argument("--ref")

    q = sub.add_parser("queue")
    q.add_argument("--status", help="filter by status prefix (default: Found/Qualified)")
    q.add_argument("--verbose", "-v", action="store_true",
                   help="also print Portal (job URL) and Notes for each row")

    e = sub.add_parser("emails")
    e.add_argument("--status", help="filter by status prefix")
    e.add_argument("--days", type=int, default=120,
                   help="age cutoff for the generated Gmail query (default 120)")
    sub.add_parser("stats")

    args = p.parse_args()
    {"check": cmd_check, "add": cmd_add, "update": cmd_update,
     "queue": cmd_queue, "emails": cmd_emails, "stats": cmd_stats}[args.cmd](args)


if __name__ == "__main__":
    main()
