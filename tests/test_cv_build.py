"""Check the CV / cover-letter generators against the shipped example data.

    PYTHONUTF8=1 python tests/test_cv_build.py

No pdflatex and no Word needed: this asserts on the generated .tex, which is where
a wrong selection, a lost umlaut or a broken escape would show.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import make_cover_letter_tex as letter  # noqa: E402
from make_tailored_cv import build_tex, esc, load_data, stem  # noqa: E402

d = load_data(ROOT / "application" / "cv_data.example.py")

assert esc("50% R&D #1 a_b") == r"50\% R\&D \#1 a\_b", esc("50% R&D #1 a_b")

en = build_tex("example_ml_thesis", d)
assert r"\usepackage[english]{babel}" in en and r"\section{Selected Projects}" in en
assert en.index("DocSearch") < en.index("SensorBoard"), "projects must follow the job's order"
assert "Embedded \\& Hardware" not in en, "a skill group the job did not select leaked in"
assert d.DOB_DE not in en, "date of birth belongs on the German CV only"
assert en.rstrip().endswith(r"\end{document}")

de = build_tex("example_embedded_werkstudent", d)
assert r"\usepackage[ngerman]{babel}" in de and r"\section{Ausgewählte Projekte}" in de
assert de.index("SensorBoard") < de.index("DocSearch")
assert d.DOB_DE in de and "Deutschland" in de and "über SPI" in de

for slug, job in d.JOBS.items():  # the employer is never named on the CV
    employer = job["folder"].split("_")[0]
    assert employer not in build_tex(slug, d), "%s names its employer" % slug

assert stem(d, "en") == "CV_Jane_Doe" and stem(d, "de") == "Lebenslauf_Jane_Doe"

tex = letter.build_tex("example_ml_thesis", d)
assert tex.count(r"\par") >= 5 and "Dear Ms Mustermann," in tex and d.CONTACT[0] in tex
n, (lo, hi) = letter.wordcount("example_ml_thesis", d), letter.WORDS["en"]
assert lo <= n <= hi, "example letter is %d words, wants %d-%d" % (n, lo, hi)
assert len(d.LETTERS["example_ml_thesis"]["paragraphs"]) == 5

print("OK: %d CV job(s), %d letter(s) built from the example data" % (len(d.JOBS), len(d.LETTERS)))
