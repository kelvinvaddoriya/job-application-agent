#!/usr/bin/env python
"""Regenerate progress.html from the tracker CSVs.

The dashboard is a self-contained HTML file whose only data source is the
`const DATA = [...]` array and the "Updated DD.MM.YYYY" line in the masthead.
This script rewrites just those two spots, leaving all styling/JS untouched.

Usage:  python scripts/build_dashboard.py [--if-stale]

--if-stale rebuilds only when a tracker CSV is newer than progress.html, and
exits quietly when progress.html does not exist at all (the dashboard is
gitignored, so clones other than the user's - including the daily email-check
routine's checkout - have no dashboard to refresh). That makes the command
safe to run unconditionally from a git hook or a scheduled pull.

The row dicts keep the original spreadsheet column names ("Date Applied",
"Outcome Detail", ...) because the page's JS reads them by name; the ID that
joins the two CSVs is not part of the payload.
"""
import argparse
import csv
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "application" / "applications.csv"
OUTCOMES = ROOT / "application" / "outcomes.csv"
HTML = ROOT / "progress.html"

FIELDS = ["Date Applied", "Company", "Position", "Location", "Reference Code",
          "Status", "CV Used", "Cover Letter", "Portal", "Notes",
          "Outcome", "Outcome Detail"]


def read_csv(path, width):
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        data = list(csv.reader(f))[1:]
    return [(r + [""] * width)[:width] for r in data if any(x.strip() for x in r)]


def load_rows():
    outs = {r[0]: r for r in read_csv(OUTCOMES, 3)}
    rows = []
    for r in read_csv(APPS, 11):
        o = outs.get(r[0], ["", "", ""])
        rows.append(dict(zip(FIELDS, r[1:11] + [o[1], o[2]])))
    return rows


def is_stale():
    """True when progress.html is older than the tracker it was built from."""
    newest = max(p.stat().st_mtime for p in (APPS, OUTCOMES) if p.exists())
    return newest > HTML.stat().st_mtime


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--if-stale", action="store_true",
                    help="no-op unless a tracker CSV is newer than progress.html")
    args = ap.parse_args()

    if args.if_stale:
        if not HTML.exists():
            # No dashboard in this clone (gitignored) - nothing to refresh.
            return
        if not APPS.exists() or not is_stale():
            return

    data = load_rows()
    html = HTML.read_text(encoding="utf-8").splitlines(keepends=True)

    data_line = "const DATA = " + json.dumps(data, ensure_ascii=False) + ";\n"
    today = dt.date.today().strftime("%d.%m.%Y")

    replaced_data = replaced_date = False
    for i, line in enumerate(html):
        if line.lstrip().startswith("const DATA = ["):
            html[i] = data_line
            replaced_data = True
        elif "<b>Updated" in line:
            html[i] = re.sub(r"Updated \d{2}\.\d{2}\.\d{4}", f"Updated {today}", line)
            replaced_date = True

    if not replaced_data:
        raise SystemExit("ERROR: could not find `const DATA = [` line in progress.html")
    if not replaced_date:
        print("WARN: could not find masthead 'Updated' line; date not bumped")

    HTML.write_text("".join(html), encoding="utf-8")
    print(f"Wrote {len(data)} rows to {HTML.name}  (Updated {today})")


if __name__ == "__main__":
    main()
