"""Print one section of a knowledge file, so a session never has to read the whole file.

    python scripts/section.py application/feedback.md "General"
    python scripts/section.py application/feedback.md "Workday"            # whole portal, all companies
    python scripts/section.py application/feedback.md "Workday — Airbus"   # one company
    python scripts/section.py application/howtologin.md --list             # every section heading

Matching is case-insensitive on the heading text; "-" may be typed for "—". A `##` section runs until
the next `##`, a `###` section until the next `##` or `###`. If nothing matches exactly, headings that
contain the query are listed instead.
"""
import re
import sys


def norm(s):
    return re.sub(r"\s+", " ", s.replace("—", "-")).strip().lower()


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    path, query = sys.argv[1], sys.argv[2]
    sys.stdout.reconfigure(encoding="utf-8")
    lines = open(path, encoding="utf-8").read().split("\n")
    heads = [(i, len(m.group(1)), m.group(2)) for i, l in enumerate(lines) if (m := re.match(r"^(#{2,3}) (.+)$", l))]
    if query == "--list":
        for _, lvl, text in heads:
            print(("  " if lvl == 3 else "") + text)
        return
    hits = [(i, lvl) for i, lvl, text in heads if norm(text) == norm(query)]
    if not hits:
        near = [text for _, _, text in heads if norm(query) in norm(text)]
        sys.exit("no section named %r%s" % (query, (" — did you mean:\n  " + "\n  ".join(near)) if near else ""))
    for start, lvl in hits:
        end = next((i for i, l, _ in heads if i > start and l <= lvl), len(lines))
        print("\n".join(lines[start:end]).rstrip())


if __name__ == "__main__":
    main()
