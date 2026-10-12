# -*- coding: utf-8 -*-
"""Build a per-job tailored CV as LaTeX, then compile it with pdflatex.

Use this only when a job is worth a tailored CV. For everything else the designed
PDFs in application/CV/ are the default.

All content lives in application/cv_data.py, which is gitignored: copy
application/cv_data.example.py and fill it in from application/resume.md, which
stays the only source of truth about the candidate. This script does not invent
content -- it *selects and orders* it: each entry in JOBS picks a language, a
headline, a profile paragraph, which projects to show and in what order, and which
skill groups and certificates are worth the space for that posting.

    PYTHONUTF8=1 python scripts/make_tailored_cv.py --job <slug> [--compile]
    PYTHONUTF8=1 python scripts/make_tailored_cv.py --list     jobs already defined
    PYTHONUTF8=1 python scripts/make_tailored_cv.py --keys     what a new JOBS entry can select from
    ... --data application/cv_data.example.py     try it on the shipped example

Output lands in Application_Packages/<JOBS[slug]["folder"]>/ as CV_<FILE_STEM>.pdf
(en) or Lebenslauf_<FILE_STEM>.pdf (de). Give FILE_STEM the same tail as your
designed CV's filename and the tailored PDF overwrites the copy mkpkg.py put
there, so a package never holds both.

A German posting gets a German CV (lang="de"). Umlauts round-trip correctly through
pdflatex with inputenc utf8, so write them properly; only fall back to an ASCII
spelling or the English word if a specific string actually breaks.

The data file's strings are LaTeX: write \\& for &, -- for a dash, \\texttt{..} for
code. Only the short plain fields (contact, link labels, stack, org) are escaped
for you.

No photo, by design.

Never name the target employer in the CV -- not in the headline, not in the profile,
not in the file name, and not by naming one of their internal projects. Tailoring
means selecting and ordering your *own* work so it lines up with what the posting
asks for, and describing the domain in public terms (a standard, a law, a
technique), never addressing the company. Naming the employer is a cover-letter
move; coverletter.md is where it belongs.

--compile needs pdflatex (MiKTeX or TeX Live): taken from PATH, else from MiKTeX's
per-user install folder on Windows, which does not put itself on PATH.
"""
import argparse
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent
DATA_FILE = REPO / "application" / "cv_data.py"

HEADINGS = {
    "profile": {"en": "Profile", "de": "Profil"},
    "projects": {"en": "Selected Projects", "de": "Ausgewählte Projekte"},
    "experience": {"en": "Experience", "de": "Berufserfahrung"},
    "education": {"en": "Education", "de": "Ausbildung"},
    "skills": {"en": "Technical Skills", "de": "Kenntnisse"},
    "certs": {"en": "Certifications", "de": "Zertifikate"},
    "langs": {"en": "Languages \\& Availability", "de": "Sprachen \\& Verfügbarkeit"},
}

PREAMBLE = r"""\documentclass[10.5pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[%(babel)s]{babel}
\usepackage{csquotes}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[a4paper,top=1.4cm,bottom=1.3cm,left=1.6cm,right=1.6cm]{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{microtype}
\usepackage{needspace}
\usepackage{etoolbox}

\definecolor{accent}{HTML}{1F3B63}
\definecolor{muted}{HTML}{444444}

\hypersetup{colorlinks=true,urlcolor=accent,linkcolor=accent,
  pdftitle={%(pdftitle)s},
  pdfauthor={%(author)s}}

\setlength{\parindent}{0pt}
\pagestyle{empty}

\titleformat{\section}{\normalsize\bfseries\color{accent}}{}{0pt}{}[\vspace{-0.9em}\rule{\textwidth}{0.7pt}]
\titlespacing*{\section}{0pt}{1.05em}{0.55em}

\setlist[itemize]{leftmargin=1.05em,itemsep=0.12em,topsep=0.18em,parsep=0pt,label=\textcolor{accent}{\textbullet}}

\newcommand{\entry}[2]{\vspace{0.15em}\textbf{#1}\hfill{\small\textcolor{muted}{#2}}\par}
\newcommand{\sub}[1]{{\small\textcolor{muted}{#1}}\par\vspace{0.1em}}
\newcommand{\skillrow}[2]{\textbf{#1:} #2\par\vspace{0.18em}}
%% A section heading must never be orphaned at the foot of a page.
\pretocmd{\section}{\Needspace*{4\baselineskip}}{}{}
"""


def load_data(path=None):
    """The candidate's CV content as a namespace: d.NAME, d.PROJECTS, d.JOBS, ..."""
    path = Path(path or DATA_FILE)
    if not path.exists():
        sys.exit("no CV data at %s -- copy application/cv_data.example.py to "
                 "application/cv_data.py and fill it in from application/resume.md" % path)
    return SimpleNamespace(**runpy.run_path(str(path)))


def esc(s):
    """Escape LaTeX specials that survive in plain data fields."""
    for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")):
        s = s.replace(a, b)
    return s


def pick(value, lang):
    """Entries are either a {'en':..,'de':..} mapping or a single shared string."""
    return value[lang] if isinstance(value, dict) else value


def stem(d, lang, de="Lebenslauf_", en="CV_"):
    # No job slug in the stem: it carries the employer name, which must not appear
    # on the CV. The package folder already keeps one job's files apart.
    return (de if lang == "de" else en) + d.FILE_STEM


def build_tex(slug, d):
    job = d.JOBS[slug]
    lang = job.get("lang", "en")
    H = lambda k: HEADINGS[k][lang]

    out = [PREAMBLE % {
        "babel": "ngerman" if lang == "de" else "english",
        "pdftitle": ("Lebenslauf -- " if lang == "de" else "Curriculum Vitae -- ") + d.NAME,
        "author": d.NAME,
    }]
    out.append(r"\begin{document}")
    out.append("")

    # Header
    contact = list(d.CONTACT) + [d.ADDRESS[lang]]
    if lang == "de" and getattr(d, "DOB_DE", None):
        contact.append(d.DOB_DE)
    out.append(r"{\LARGE\bfseries\color{accent} " + d.NAME + r"}\par\vspace{0.25em}")
    out.append(r"{\small\textcolor{muted}{" + job["headline"] + r"}}\par\vspace{0.4em}")
    out.append(r"{\small " + r" $\cdot$ ".join(esc(c) for c in contact) + r"}\par\vspace{0.15em}")
    out.append(r"{\small " + r" $\cdot$ ".join(
        r"\href{%s}{%s}" % (url, esc(label)) for label, url in d.LINKS) + r"}")
    out.append("")

    out.append(r"\section{%s}" % H("profile"))
    out.append(job["profile"])
    out.append("")

    # Projects first -- strongest evidence for a thesis application
    out.append(r"\section{%s}" % H("projects"))
    for key in job["projects"]:
        p = d.PROJECTS[key]
        out.append(r"\Needspace*{5\baselineskip}")
        out.append(r"\entry{%s}{%s}" % (pick(p["title"], lang), pick(p["dates"], lang)))
        out.append(r"\sub{%s}" % esc(pick(p["stack"], lang)))
        out.append(r"\begin{itemize}")
        for b in pick(p["bullets"], lang):
            out.append(r"  \item " + b)
        out.append(r"\end{itemize}")
    out.append("")

    out.append(r"\section{%s}" % H("experience"))
    for key in job["experience"]:
        e = d.EXPERIENCE[key]
        out.append(r"\Needspace*{5\baselineskip}")
        out.append(r"\entry{%s}{%s}" % (pick(e["role"], lang), pick(e["dates"], lang)))
        out.append(r"\sub{%s}" % esc(pick(e["org"], lang)))
        out.append(r"\begin{itemize}")
        for b in pick(e["bullets"], lang):
            out.append(r"  \item " + b)
        out.append(r"\end{itemize}")
    out.append("")

    out.append(r"\section{%s}" % H("education"))
    for ed in d.EDUCATION:
        out.append(r"\Needspace*{4\baselineskip}")
        out.append(r"\entry{%s}{%s}" % (pick(ed["degree"], lang), pick(ed["dates"], lang)))
        out.append(r"\sub{%s}" % esc(pick(ed["org"], lang)))
        out.append(r"{\small " + pick(ed["note"], lang) + r"}\par")
    out.append("")

    out.append(r"\section{%s}" % H("skills"))
    for key in job["skills"]:
        label, content = d.SKILL_GROUPS[key]
        out.append(r"\skillrow{%s}{%s}" % (pick(label, lang), content))
    out.append("")

    out.append(r"\section{%s}" % H("certs"))
    out.append(r"\begin{itemize}")
    for key in job["certs"]:
        out.append(r"  \item " + pick(d.CERTS[key], lang))
    out.append(r"\end{itemize}")
    out.append("")

    out.append(r"\section{%s}" % H("langs"))
    out.append(d.LANGUAGES[lang] + r"\par\vspace{0.25em}")
    out.append(d.AVAILABILITY[lang])

    out.append(r"\end{document}")
    return "\n".join(out) + "\n"


# Invisible formatting characters that ride along in LLM-written prose. They
# survive into the PDF text layer, where an ATS parser reads them as noise in
# the middle of a word - the same class of defect as the cp1252 umlaut mangling
# in prompts/application.md, and invisible for exactly the same reason.
#
# Strip the .tex before pdflatex, never the finished PDF: a compiled PDF would
# have to be re-distilled to reach its text layer, which risks the file for no
# gain. Clean source in, clean PDF out.
#
# Deliberately NOT stripped: U+00A0 and U+202F. They render as real spaces and
# German typography uses them, so dropping them would move text on the page.
# These are not marks; they are punctuation.
# Written as code points, never as literal characters or escapes: a cleaner run
# over this repo would decode and strip those, silently emptying the table.
ZERO_WIDTH = dict.fromkeys([
    0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x00AD,
    0x200E, 0x200F, 0x061C, 0x180E,
    0x2061, 0x2062, 0x2063, 0x2064,
])


def strip_marks(text):
    """Drop zero-width/invisible characters. Cannot change rendering or word count."""
    return text.translate(ZERO_WIDTH)


def pdflatex():
    exe = shutil.which("pdflatex")
    if not exe:
        miktex = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"
        exe = str(miktex) if miktex.exists() else None
    if not exe:
        sys.exit("pdflatex not found -- install MiKTeX or TeX Live (only --compile needs it)")
    return exe


def compile_pdf(tex_path):
    exe = pdflatex()
    for _ in range(2):  # twice, so hyperref settles
        r = subprocess.run(
            [exe, "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(tex_path.parent), str(tex_path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode != 0:
            log = tex_path.with_suffix(".log")
            tail = log.read_text(encoding="utf-8", errors="replace")[-3000:] if log.exists() else r.stdout[-3000:]
            sys.exit("pdflatex failed:\n" + tail)
    for ext in (".aux", ".log", ".out"):
        tex_path.with_suffix(ext).unlink(missing_ok=True)
    return tex_path.with_suffix(".pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", help="job slug (see --list)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--keys", action="store_true", help="print the project/experience/skill/cert keys")
    ap.add_argument("--lang", choices=("en", "de"),
                    help="override the job's language (default: the job's own setting)")
    ap.add_argument("--compile", action="store_true", help="run pdflatex after writing the .tex")
    ap.add_argument("--data", help="CV data file (default: application/cv_data.py)")
    a = ap.parse_args()
    d = load_data(a.data)

    if a.keys:  # so a new JOBS entry can be written without reading the whole data file
        for group in ("PROJECTS", "EXPERIENCE", "SKILL_GROUPS", "CERTS"):
            print("%-13s %s" % (group, " ".join(getattr(d, group))))
        return
    if a.list or not a.job:
        for slug, j in d.JOBS.items():
            print("%-38s [%s] -> %s" % (slug, j.get("lang", "en"), j["folder"]))
        return
    if a.job not in d.JOBS:
        sys.exit("unknown job %r -- use --list" % a.job)
    if a.lang:
        d.JOBS[a.job]["lang"] = a.lang

    lang = d.JOBS[a.job].get("lang", "en")
    pkg = REPO / "Application_Packages" / d.JOBS[a.job]["folder"]
    pkg.mkdir(parents=True, exist_ok=True)
    tex = pkg / (stem(d, lang) + ".tex")
    tex.write_text(strip_marks(build_tex(a.job, d)), encoding="utf-8")
    print("wrote", tex.relative_to(REPO), "[%s]" % lang)
    if a.compile:
        pdf = compile_pdf(tex)
        print("built", pdf.relative_to(REPO), "(%.0f KB)" % (pdf.stat().st_size / 1024))


if __name__ == "__main__":
    main()
