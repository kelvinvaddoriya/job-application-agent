# -*- coding: utf-8 -*-
"""Build a one-page tailored cover letter as LaTeX, matched to the CV design.

This is the LaTeX sibling of scripts/make_cover_letter.py (docx + Word COM).
It exists because scripts/make_tailored_cv.py produces LaTeX CVs, and a letter
set in the same face, accent colour and margins reads as one package.

The letters live in LETTERS in application/cv_data.py (see cv_data.example.py),
keyed by the same slug as the job's JOBS entry, which names the package folder.
The sender block is built from NAME / ADDRESS / CONTACT in that file.

Rules enforced from prompts/coverletter.md:
  - language follows the posting language
  - body is exactly five paragraphs, 250-260 words (English) or 210-235 (German)
  - every claim traces back to application/resume.md

    PYTHONUTF8=1 python scripts/make_cover_letter_tex.py --job <slug> [--compile]
    PYTHONUTF8=1 python scripts/make_cover_letter_tex.py --wordcount
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_tailored_cv import REPO, compile_pdf, esc, load_data, stem, strip_marks  # noqa: E402

WORDS = {"en": (250, 260), "de": (210, 235)}  # coverletter.md: German runs longer per word

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[%(babel)s]{babel}
\usepackage{csquotes}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[a4paper,top=1.6cm,bottom=1.5cm,left=1.6cm,right=1.6cm]{geometry}
\usepackage{xcolor}
\usepackage{microtype}
\usepackage{setspace}

\definecolor{accent}{HTML}{1F3B63}
\definecolor{muted}{HTML}{444444}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.62em}
\pagestyle{empty}
\linespread{1.04}
"""


def build_tex(slug, d):
    L = d.LETTERS[slug]
    sender = [d.ADDRESS[L["lang"]]] + list(d.CONTACT)
    out = [PREAMBLE % {"babel": "ngerman" if L["lang"] == "de" else "english"}]
    out.append(r"\begin{document}")
    out.append(r"{\LARGE\bfseries\color{accent} " + d.NAME + r"}\par")
    out.append(r"{\small\textcolor{muted}{%s}}\par" % r" $\cdot$ ".join(esc(s) for s in sender))
    out.append(r"\vspace{0.3em}{\color{accent}\rule{\textwidth}{0.8pt}}\par")
    out.append(r"\vspace{1.1em}")
    out.append(r"{\small " + r"\\".join(L["recipient"]) + r"}\par")
    out.append(r"\vspace{1.1em}")
    out.append(r"\hfill{\small " + L["date"] + r"}\par")
    out.append(r"\vspace{0.5em}")
    out.append(r"{\bfseries " + L["subject"] + r"}\par")
    out.append(r"\vspace{0.7em}")
    out.append(L["greeting"] + r"\par")
    for p in L["paragraphs"]:
        out.append(p + r"\par")
    out.append(r"\vspace{0.5em}")
    out.append(L["closing"] + r"\par")
    out.append(r"\vspace{1.6em}")
    out.append(d.NAME)
    out.append(r"\end{document}")
    return "\n".join(out) + "\n"


def wordcount(slug, d):
    body = " ".join(d.LETTERS[slug]["paragraphs"])
    body = body.replace("\\enquote{", "").replace("}", "")
    return len(re.findall(r"[\wÄÖÜäöüß-]+", body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job")
    ap.add_argument("--compile", action="store_true")
    ap.add_argument("--wordcount", action="store_true")
    ap.add_argument("--data", help="CV data file (default: application/cv_data.py)")
    a = ap.parse_args()
    d = load_data(a.data)

    if a.wordcount:
        for slug, L in d.LETTERS.items():
            n, (lo, hi) = wordcount(slug, d), WORDS[L["lang"]]
            print("%s %-34s %d words (%s wants %d-%d), %d paragraphs"
                  % ("OK " if lo <= n <= hi else "OUT", slug, n, L["lang"], lo, hi, len(L["paragraphs"])))
        return
    if not a.job or a.job not in d.LETTERS:
        sys.exit("use --job <slug> (%s) or --wordcount" % ", ".join(d.LETTERS))

    L = d.LETTERS[a.job]
    pkg = REPO / "Application_Packages" / d.JOBS[a.job]["folder"]
    pkg.mkdir(parents=True, exist_ok=True)
    tex = pkg / ((L.get("filename") or stem(d, L["lang"], "Anschreiben_", "Cover_Letter_")) + ".tex")
    tex.write_text(strip_marks(build_tex(a.job, d)), encoding="utf-8")
    print("wrote", tex.relative_to(REPO), "(%d words)" % wordcount(a.job, d))
    if a.compile:
        pdf = compile_pdf(tex)
        print("built", pdf.relative_to(REPO), "(%.0f KB)" % (pdf.stat().st_size / 1024))


if __name__ == "__main__":
    main()
