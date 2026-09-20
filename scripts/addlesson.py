"""File one dated lesson into a knowledge file, in the layout CLAUDE.md prescribes.

    python scripts/addlesson.py feedback "Workday" "TRUMPF" "LinkedIn listed SS27 reqs that are not on the board ..."
    python scripts/addlesson.py login "SuccessFactors" "General" "The first Sign In click is often swallowed ..."
    python scripts/addlesson.py feedback "General" "Search and sources" "..."    # cross-portal topic

`feedback` = application/feedback.md, `login` = application/howtologin.md. The bullet is appended at the end of
`### <Portal> — <Company>`; the `###` (and the `## <Portal>`) is created in alphabetical position only if missing,
so there is never a second section for the same portal. `--date` overrides today's date.
"""
import argparse, datetime, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {"feedback": "application/feedback.md", "login": "application/howtologin.md"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", choices=FILES); ap.add_argument("portal"); ap.add_argument("company"); ap.add_argument("text")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    path = os.path.join(ROOT, FILES[a.file])
    L = open(path, encoding="utf-8").read().split("\n")
    h2, h3 = f"## {a.portal}", f"### {a.portal} — {a.company}"
    bullet = f"- ({a.date}) {a.text.strip()}"
    h2s = [(i, l) for i, l in enumerate(L) if l.startswith("## ")]
    if h2 not in L:
        names = [(i, l[3:]) for i, l in h2s if not l[3:].startswith(("General", "Archive"))]
        pos = next((i for i, n in names if n.lower() > a.portal.lower()), None)
        if pos is None:
            pos = next((i for i, l in h2s if l.startswith("## Archive")), len(L))
        L[pos:pos] = [h2, "", h3, "", bullet, ""]
    else:
        i2 = L.index(h2)
        end2 = next((i for i, l in h2s if i > i2), len(L))
        if h3 in L[i2:end2]:
            i3 = L.index(h3, i2)
            end3 = next((i for i in range(i3 + 1, len(L)) if re.match(r"^#{2,3} ", L[i])), len(L))
            while end3 > i3 and not L[end3 - 1].strip():
                end3 -= 1
            L[end3:end3] = ["", bullet]
        else:
            key = lambda s: (not s.endswith("— General"), s.lower())
            subs = [(i, L[i]) for i in range(i2, end2) if L[i].startswith("### ")]
            pos = next((i for i, l in subs if key(l) > key(h3)), end2)
            L[pos:pos] = [h3, "", bullet, ""]
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print(f"filed under {h3} in {FILES[a.file]}")


if __name__ == "__main__":
    main()
