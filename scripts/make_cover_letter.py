"""Build a tailored cover-letter .docx from the newest template.

Used by prompts/coverletter.md. Copies the language-matched template into the job's
package folder, replaces the recipient block, date, subject line and the five body
paragraphs, and prints the body word count (the 250-260 target) plus the output path.

    import sys; sys.path.insert(0, "scripts")
    from make_cover_letter import build
    build(pkg, "Firma GmbH
Stadt", "BEWERBUNG: <Rolle>", paras)          # German
    build(pkg, "Company
City", "APPLICATION: <role>", paras, lang="en")  # English

Write the calling script with the Write tool (UTF-8) and run it with PYTHONUTF8=1 --
umlauts typed into a bash heredoc are read as cp1252 and mangle.
"""

import sys, shutil, os, json
from docx import Document
def build(pkg, company_lines, subject, paras, date="<your city>, 30. August 2026", tmpl=None, lang="de"):
    if tmpl is None:
        tmpl = ("Application_Packages/Kostal_Werkstudent_KI_Entwicklung/Anschreiben_<Name>.docx"
                if lang=="de" else
                "Application_Packages/appliedAI_Working_Student_Agentic_AI/Cover_Letter_<Name>.docx")
    name = "Anschreiben_<Name>.docx" if lang=="de" else "Cover_Letter_<Name>.docx"
    dst = os.path.join(pkg, name)
    shutil.copy(tmpl, dst)
    d = Document(dst)
    ps = d.paragraphs
    def setp(p, text):
        for r in p.runs[1:]:
            r._element.getparent().remove(r._element)
        if p.runs: p.runs[0].text = text
        else: p.add_run(text)
    setp(ps[1], company_lines)
    setp(ps[2], date)
    setp(ps[3], subject)
    for i, t in enumerate(paras):
        setp(ps[4+i], t)
    d.save(dst)
    wc = sum(len(t.split()) for t in paras)
    print("words:", wc, "->", dst)
    return dst
