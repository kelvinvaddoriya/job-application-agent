"""Saved-password registry for login walls.

Answers ONE question before any login attempt: does Chrome hold a saved
credential for this portal, and what does a hit actually prove?

Reads Chrome's password DBs directly (every profile, both the device store
`Login Data` and the Google-account store `Login Data For Account`). It reads
ONLY origin_url / username_value / usage timestamps. The encrypted
password_value column is never read, never decrypted, never printed.

Usage:
  python scripts/creds.py check <job-url|host>   verdict for one portal
  python scripts/creds.py list [--ats] [--grep X]  saved hosts
  python scripts/creds.py note <host> --status has_account|no_account|
        password_rejected|mfa|account_wall|guest_path [--note "..."] [--source gmail]
  python scripts/creds.py notes                 the manual overlay
  python scripts/creds.py profiles              which Chrome profile to attach to

TWO STORES, and the difference is why this file exists: on 2026-08-30 a batch
concluded "Chrome holds no ATS credentials at all (15 saved origins)" and wrote
three NeedsUser rows off it. That count came from the DEVICE store, which holds
9 rows. The ACCOUNT store holds 632, including ~35 Workday tenants. Never count
origins by hand - let this script pick the stores.

WHAT A HIT PROVES depends on the portal's URL shape:
  * PER-TENANT host (workday `<co>.wd3.myworkdayjobs.com`, umantis
    `recruitingapp-NNNN`, softgarden `<co>.softgarden.io`, csod, taleo):
    a hit is strong evidence of a real account on THAT tenant.
  * SHARED host (SuccessFactors / SAP `career5.successfactors.eu`,
    `career55.sapsf.eu` ... where the tenant is a `?company=` param): every
    employer shares one host, so Chrome will happily fill a credential saved
    for a different company. A hit proves nothing until you submit the login
    and read the result (Funke and SIGNAL IDUNA both autofilled, both failed).

IDENTITY PRECEDENCE (the user, 2026-08-31): there are two addresses, one letter
apart. ALWAYS try you@example.com first. Only fall back to
you.alt@example.com when the primary is actually rejected - not on a
hunch, and not because the fallback is the one Chrome saved for that host.
`check` orders and labels the saved identities accordingly.

AUTOFILL MECHANICS (do not re-derive these): it does NOT fire on page load, and
`input.value` reads empty from JS until the user interacts with the page. Open
the login page, scrollIntoView the PASSWORD input and COORDINATE-CLICK that (the
password field is far more reliable than the email field - verified 2026-09-06 on
Draeger / LEMKEN / MAHLE / HOERBIGER / FC Bayern, where it filled both boxes first
try), then click Sign In. Only an on-screen empty box in a screenshot means "no credential" - and
this script answers that faster than a screenshot does.

A "no" here is not a NeedsUser verdict on its own: Gmail acknowledgements
(`from:myworkday.com`, `system@successfactors.eu`) enumerate tenants the user has
an account on regardless of what Chrome saved. `check` prints that query for you.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES_FILE = os.path.join(ROOT, "application", "credentials_notes.json")
CHROME = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data")
STORES = ["Login Data", "Login Data For Account"]

# Hosts where one hostname serves many employers -> a saved credential there may
# belong to a different tenant entirely.
SHARED_HOST_RX = re.compile(r"successfactors\.(eu|com)$|sapsf\.(eu|com)$|p78quickapply\.com$")

# Platform suffixes: every company gets its own subdomain, so "same registrable
# domain" says nothing about the employer. Never list these as related hosts.
PLATFORM_SUFFIXES = ("myworkdayjobs.com", "successfactors.eu", "successfactors.com",
                     "sapsf.eu", "sapsf.com", "taleo.net", "csod.com", "softgarden.io",
                     "umantis.com", "ashbyhq.com", "icims.com", "dvinci-hr.com",
                     "greenhouse.io", "lever.co", "smartrecruiters.com", "personio.de")

# Identity precedence (the user, 2026-08-31): ALWAYS try the primary first; only
# fall back to the second address if the primary is rejected or unknown there.
# The two differ by one letter and are easy to mix up.
PRIMARY_EMAIL = "you@example.com"
FALLBACK_EMAIL = "you.alt@example.com"
IDENTITY_ORDER = [PRIMARY_EMAIL, FALLBACK_EMAIL]


def identity_rank(user):
    u = (user or "").lower()
    return (IDENTITY_ORDER.index(u), u) if u in IDENTITY_ORDER else (len(IDENTITY_ORDER), u)


def identity_label(user):
    u = (user or "").lower()
    if u == PRIMARY_EMAIL:
        return "PRIMARY - try this first"
    if u == FALLBACK_EMAIL:
        return "fallback - only if the primary is rejected"
    return "other identity"


ATS_KEYS = ("myworkdayjobs", "successfactors", "sapsf", "taleo", "csod", "avature",
            "greenhouse", "lever.co", "ashbyhq", "smartrecruiters", "personio",
            "softgarden", "dvinci", "join.com", "stepstone", "umantis", "concludis",
            "rexx", "icims", "phenom", "eightfold", "jobvite", "brassring", "workday",
            "jobs.", "career", "karriere", "recruit", "bewerb", "talent")


def chrome_epoch(v):
    """Chrome timestamps are microseconds since 1601-01-01."""
    if not v:
        return None
    try:
        return (dt.datetime(1601, 1, 1) + dt.timedelta(microseconds=v)).date().isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def profiles():
    if not os.path.isdir(CHROME):
        return []
    return [n for n in sorted(os.listdir(CHROME))
            if n == "Default" or n.startswith("Profile ")]


def read_logins():
    """Every saved login as dicts. The password column is never touched."""
    rows = []
    tmpdir = tempfile.mkdtemp(prefix="creds_")
    try:
        for prof in profiles():
            for store in STORES:
                src = os.path.join(CHROME, prof, store)
                if not os.path.exists(src):
                    continue
                dst = os.path.join(tmpdir, ("%s_%s.db" % (prof, store)).replace(" ", "_"))
                con = None
                try:
                    shutil.copy2(src, dst)
                    con = sqlite3.connect(dst)
                except (OSError, sqlite3.Error):
                    try:  # Chrome is holding the file open
                        con = sqlite3.connect("file:%s?immutable=1" % src, uri=True)
                    except sqlite3.Error:
                        continue
                try:
                    cur = con.execute(
                        "select origin_url, username_value, times_used, "
                        "date_last_used, date_created from logins")
                    for url, user, used, last, created in cur:
                        host = re.sub(r"^https?://", "", url or "").split("/")[0].lower()
                        if not host:
                            continue
                        rows.append({
                            "host": host,
                            "username": user or "",
                            "profile": prof,
                            "store": "account" if "Account" in store else "device",
                            "times_used": used or 0,
                            "last_used": chrome_epoch(last),
                            "created": chrome_epoch(created),
                        })
                except sqlite3.Error:
                    pass
                finally:
                    if con is not None:
                        con.close()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return rows


def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def host_of(target):
    t = re.sub(r"^https?://", "", target.strip())
    return t.split("/")[0].split("?")[0].lower()


def tenant_of(target):
    """Notes key. On shared hosts the tenant lives in `?company=`, so
    `career5.successfactors.eu?company=funkeservi` is a different account from
    `?company=idunaverei` even though Chrome saves one credential for both."""
    host = host_of(target)
    m = re.search(r"[?&]company=([^&#]+)", target, re.I)
    if m and SHARED_HOST_RX.search(host):
        return "%s?company=%s" % (host, m.group(1).lower())
    return host


def strip_www(h):
    return h[4:] if h.startswith("www.") else h


def registrable(host):
    parts = host.split(".")
    if len(parts) > 2 and parts[-2] in ("co", "com"):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def is_platform(host):
    return any(host.endswith(s) for s in PLATFORM_SUFFIXES)


def is_ats(host):
    return any(k in host for k in ATS_KEYS)


GENERIC_LABELS = ("www", "jobs", "job", "career", "careers", "karriere", "apply",
                  "recruiting", "recruitment", "bewerbung", "erecruitment", "talent",
                  "login", "my", "de", "en")


def company_label(host):
    """Best guess at the employer token in a host, for a Gmail search."""
    for part in host.split("."):
        if part not in GENERIC_LABELS and not re.fullmatch(r"wd\d+|career\d+", part):
            return part
    return host.split(".")[0]


def cmd_check(args):
    host = host_of(args.target)
    rows = read_logins()
    notes = load_notes()
    exact = [r for r in rows if strip_www(r["host"]) == strip_www(host)]
    shared = bool(SHARED_HOST_RX.search(host))

    print("HOST: %s" % host)
    if exact:
        users = sorted({r["username"] for r in exact if r["username"]}, key=identity_rank)
        stores = sorted({r["store"] for r in exact})
        last = max([r["last_used"] for r in exact if r["last_used"]] or [None])
        print("SAVED: yes  (%d entr%s, store=%s, last used %s)"
              % (len(exact), "y" if len(exact) == 1 else "ies",
                 "+".join(stores), last or "never"))
        for u in users:
            print("  username: %-30s (%s)" % (u, identity_label(u)))
        if PRIMARY_EMAIL not in [u.lower() for u in users]:
            print("  ! the PRIMARY address is NOT saved here. Still try %s first; "
                  "use %s only if it is rejected." % (PRIMARY_EMAIL, users[0]))
        if shared:
            print("VERDICT: WEAK. Every employer shares this hostname (the tenant is a "
                  "?company= param), so the saved credential may belong to a different "
                  "company. Submit the login and READ THE RESULT before concluding an "
                  "account exists.")
        else:
            print("VERDICT: STRONG. Per-tenant hostname - a saved credential here means "
                  "a real account on this tenant. Do not write NeedsUser for a login wall.")
        print("HOW: open the login page, scrollIntoView the PASSWORD input and "
              "COORDINATE-CLICK that (autofill never fires on load; the password field "
              "is far more reliable than the email field), then click Sign In. "
              "input.value reads empty from JS even when the field is filled. "
              "NOTE: a filled box is NOT proof the credential works - on shared "
              "SuccessFactors hosts it is usually another tenant's, and 8/8 logins "
              "failed this way on 2026-09-06.")
    else:
        print("SAVED: no entry for this host.")
        print("VERDICT: no saved credential -- but that is NOT a NeedsUser verdict yet.")
        print("  1. Gmail proves accounts Chrome never saved:")
        print('     search_threads: from:myworkday.com OR from:system@successfactors.eu "%s"'
              % company_label(host))
        print("  2. Look for a guest path: Workday `<job-url>/apply` -> 'Apply Manually', "
              "Taleo 'Apply as Guest'.")

    if not exact and not is_platform(host):
        sib = sorted({r["host"] for r in rows
                      if registrable(r["host"]) == registrable(host)})
        if sib:
            print("RELATED hosts saved (%d): %s" % (len(sib), ", ".join(sib[:8])))

    tenant = tenant_of(args.target)
    n = notes.get(tenant) or notes.get(strip_www(host)) or notes.get(host)
    if n:
        print("NOTE [%s] %s (source: %s): %s"
              % (n.get("status"), n.get("date", ""), n.get("source", "manual"),
                 n.get("note", "")))
    elif shared and tenant == host:
        print("HINT: no tenant recorded. Pass the full URL (with ?company=) so the "
              "note lands on the right employer, not the shared host.")


def cmd_list(args):
    rows = read_logins()
    by_host = {}
    for r in rows:
        by_host.setdefault(r["host"], []).append(r)
    hosts = sorted(by_host)
    if args.ats:
        hosts = [h for h in hosts if is_ats(h)]
    if args.grep:
        g = args.grep.lower()
        hosts = [h for h in hosts if g in h]
    notes = load_notes()
    for h in hosts:
        rs = by_host[h]
        users = sorted({r["username"] for r in rs if r["username"]}, key=identity_rank)
        last = max([r["last_used"] for r in rs if r["last_used"]] or [None])
        kind = "SHARED" if SHARED_HOST_RX.search(h) else "tenant"
        mark = " [%s]" % notes[h]["status"] if h in notes else ""
        print("%-52s %-7s %-10s %s%s"
              % (h, kind, last or "-", ", ".join(users) or "-", mark))
    print("\n%d host(s) shown of %d saved." % (len(hosts), len(by_host)))


def cmd_profiles(args):
    """Which Chrome profile actually holds the credentials.

    The harness attaches to whatever Chrome is already running and does NOT
    select a profile. Attach to the wrong one and autofill can never fire, on
    any portal, with no error - it just looks like every site logged you out.
    """
    try:
        state = json.load(open(os.path.join(CHROME, "Local State"), encoding="utf-8"))
        info = state.get("profile", {}).get("info_cache", {})
        last = state.get("profile", {}).get("last_used", "Default")
    except (OSError, ValueError):
        info, last = {}, "Default"
    rows = read_logins()
    best, best_n = None, -1
    for prof in profiles():
        rs = [r for r in rows if r["profile"] == prof]
        ats = sorted({r["host"] for r in rs if is_ats(r["host"])})
        acct = len([r for r in rs if r["store"] == "account"])
        if len(ats) > best_n:
            best, best_n = prof, len(ats)
        print("%-11s %-22s %4d saved (%d account / %d device)  %3d ATS host(s)%s"
              % (prof, repr(info.get(prof, {}).get("name", "?")), len(rs), acct,
                 len(rs) - acct, len(ats), "  <- last used" if prof == last else ""))
    if best:
        print("\nUSE THIS PROFILE: %s (%s) - it holds %d of the ATS credentials."
              % (best, info.get(best, {}).get("name", "?"), best_n))
        print("Before a batch, confirm the attached Chrome is that profile "
              "(chrome://version -> Profile Path). The harness does no profile "
              "selection, so attaching to the other one makes every login fail "
              "silently and looks exactly like 'no saved password'.")


def cmd_note(args):
    notes = load_notes()
    host = tenant_of(args.host)
    notes[host] = {"status": args.status,
                   "note": args.note or "",
                   "source": args.source or "manual",
                   "date": args.date or dt.date.today().isoformat()}
    save_notes(notes)
    print("noted %s: %s" % (host, args.status))


def cmd_notes(args):
    notes = load_notes()
    for h, n in sorted(notes.items()):
        print("%-52s %-17s %-10s %s"
              % (h, n["status"], n.get("date", ""), n.get("note", "")))
    print("\n%d note(s)." % len(notes))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="verdict for one portal URL or host")
    c.add_argument("target")
    c.set_defaults(func=cmd_check)

    l = sub.add_parser("list", help="saved hosts")
    l.add_argument("--ats", action="store_true", help="only career/ATS hosts")
    l.add_argument("--grep")
    l.set_defaults(func=cmd_list)

    n = sub.add_parser("note", help="record a manual verdict for a host")
    n.add_argument("host")
    n.add_argument("--status", required=True,
                   choices=["has_account", "no_account", "password_rejected",
                            "mfa", "account_wall", "guest_path"])
    n.add_argument("--note")
    n.add_argument("--source")
    n.add_argument("--date")
    n.set_defaults(func=cmd_note)

    ns = sub.add_parser("notes", help="print the manual overlay")
    ns.set_defaults(func=cmd_notes)

    pr = sub.add_parser("profiles", help="which Chrome profile holds the credentials")
    pr.set_defaults(func=cmd_profiles)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
