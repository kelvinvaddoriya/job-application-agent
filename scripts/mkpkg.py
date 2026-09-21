"""Create an application package folder: job_posting.txt, the language-matched CV, and supporting documents.

    python scripts/mkpkg.py <Company_Role> <posting.txt | URL | -> <en|de> [--docs transcript,immat,zeugnis,aufenthalt,degree,school] [--max-cv-kb 450]

- `-` keeps an existing job_posting.txt (e.g. one written by `ats_probe.py --save`).
- Copies the language-matched CV out of application/CV/<--cv-dir>/ (default `primary`): the single
  CV_*.pdf for en, Lebenslauf_*.pdf for de. Pass --cv-dir secondary for your other role class. Never leave a designed and a generated CV side by side; this script only copies the designed one.
- --max-cv-kb recompresses the CV photo (pypdf + Pillow) when a portal caps upload size (Micron/Eightfold: 488 KB).
  The compressed file keeps the normal CV name, so the package still holds exactly one CV.
Prints the folder and its files. The cover letter is a separate step (scripts/make_cover_letter.py).
"""
import argparse, html, os, re, shutil, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Map --docs keys to YOUR filenames in "Other Docs/". Add, rename or delete rows freely;
# keep the keys short, they are what you type at `mkpkg.py --docs transcript,immat`.
DOCS = {"transcript": "TranscriptOfRecords.pdf", "immat": "EnrollmentCertificate.pdf",
        "zeugnis": "References.pdf", "permit": "WorkPermit.pdf",
        "degree": "DegreeCertificate.pdf", "school": "SchoolReport.pdf"}


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
    ap.add_argument("--docs", default=""); ap.add_argument("--cv-dir", default="primary"); ap.add_argument("--max-cv-kb", type=int)
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
    # Whatever you named your CVs, as long as the English one starts CV_ and the
    # German one Lebenslauf_. One match per language per folder, or this raises.
    stem = "CV_" if a.lang == "en" else "Lebenslauf_"
    cv_dir = os.path.join(ROOT, "application", "CV", a.cv_dir)
    hits = sorted(f for f in os.listdir(cv_dir) if f.startswith(stem) and f.endswith(".pdf"))
    if len(hits) != 1:
        sys.exit("expected exactly one %s*.pdf in %s, found %s" % (stem, cv_dir, hits or "none"))
    dst = os.path.join(pkg, hits[0])
    shutil.copy(os.path.join(cv_dir, hits[0]), dst)
    if a.max_cv_kb:
        compress_cv(dst, a.max_cv_kb)
    for d in filter(None, a.docs.split(",")):
        shutil.copy(os.path.join(ROOT, "Other Docs", DOCS[d]), pkg)
    print(pkg); print(sorted(os.listdir(pkg)))


if __name__ == "__main__":
    main()
