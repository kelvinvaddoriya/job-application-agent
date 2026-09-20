"""Create an application package folder: job_posting.txt, the language-matched CV, and supporting documents.

    python scripts/mkpkg.py <Company_Role> <posting.txt | URL | -> <en|de> [--docs transcript,immat,zeugnis,aufenthalt,degree,school] [--max-cv-kb 450]

- `-` keeps an existing job_posting.txt (e.g. one written by `ats_probe.py --save`).
- en -> application/CV/Ai/CV_<Name>.pdf, de -> Lebenslauf_<Name>.pdf. Pass --cv-dir Embedded for
  embedded roles. Never leave a designed and a generated CV side by side; this script only copies the designed one.
- --max-cv-kb recompresses the CV photo (pypdf + Pillow) when a portal caps upload size (Micron/Eightfold: 488 KB).
  The compressed file keeps the normal CV name, so the package still holds exactly one CV.
Prints the folder and its files. The cover letter is a separate step (scripts/make_cover_letter.py).
"""
import argparse, html, os, re, shutil, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = {"transcript": "TranscriptofRecords_<Name>.pdf", "immat": "Immatriculation_<Name>.pdf",
        "zeugnis": "Arbeitszeugnisse_<Name>.pdf", "aufenthalt": "Aufenthaltstitel_<Name>.pdf",
        "degree": "B_Tech_Degree_<Name>.pdf", "school": "HighSchoolReport_<Name>.pdf"}


def compress_cv(path, max_kb):
    from pypdf import PdfWriter  # Pillow is needed for image re-encoding
    if os.path.getsize(path) <= max_kb * 1024:
        return
    w = PdfWriter(clone_from=path)
    for page in w.pages:
        for img in page.images:
            im = img.image.convert("RGB")
            im.thumbnail((300, 300))
            img.replace(im, quality=70)
        page.compress_content_streams()
    w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    tmp = path + ".tmp"
    w.write(tmp)
    os.replace(tmp, path)
    print(f"CV compressed to {os.path.getsize(path) // 1024} KB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name"); ap.add_argument("src"); ap.add_argument("lang", choices=["en", "de"])
    ap.add_argument("--docs", default=""); ap.add_argument("--cv-dir", default="Ai"); ap.add_argument("--max-cv-kb", type=int)
    a = ap.parse_args()
    pkg = os.path.join(ROOT, "Application_Packages", a.name)
    os.makedirs(pkg, exist_ok=True)
    if a.src != "-":
        if a.src.startswith("http"):
            h = urllib.request.urlopen(urllib.request.Request(a.src, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read().decode("utf-8", "replace")
            text = a.src + "\n\n" + re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", h))))
        else:
            text = open(a.src, encoding="utf-8").read()
        open(os.path.join(pkg, "job_posting.txt"), "w", encoding="utf-8").write(text)
    cv = "CV_<Name>.pdf" if a.lang == "en" else "Lebenslauf_<Name>.pdf"
    dst = os.path.join(pkg, cv)
    src = os.path.join(ROOT, "application", "CV", a.cv_dir, cv)
    if not os.path.exists(src):  # Embedded/ names its files *_<Name>.pdf
        src = src.replace("_the user_", "_the user_M_")
    shutil.copy(src, dst)
    if a.max_cv_kb:
        compress_cv(dst, a.max_cv_kb)
    for d in filter(None, a.docs.split(",")):
        shutil.copy(os.path.join(ROOT, "Other Docs", DOCS[d]), pkg)
    print(pkg); print(sorted(os.listdir(pkg)))


if __name__ == "__main__":
    main()
