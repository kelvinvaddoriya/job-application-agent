"""Build a tailored cover-letter .docx from the newest template.

Used by prompts/coverletter.md. Copies the language-matched template into the job's
package folder, replaces the recipient block, date, subject line and the five body
paragraphs, and prints the body word count (the 250-260 target) plus the output path.

    import sys; sys.path.insert(0, "scripts")
    from make_cover_letter import build
    build(pkg, "Firma GmbH
Stadt", "BEWERBUNG: <Rolle>", paras, city="Berlin")   # German
    build(pkg, "Company
City", "APPLICATION: <role>", paras, lang="en")  # English

Write the calling script with the Write tool (UTF-8) and run it with PYTHONUTF8=1 --
umlauts typed into a bash heredoc are read as cp1252 and mangle.
"""

import sys, shutil, os, json, datetime as dt

MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
             "August", "September", "Oktober", "November", "Dezember"]
from docx import Document
def build(pkg, company_lines, subject, paras, date=None, tmpl=None, lang="de", city=None):
    """`tmpl` is your own .docx letterhead for this language - pass it, or set
    JOBAGENT_LETTER_DE / JOBAGENT_LETTER_EN to its path. In practice that is the last
    letter you sent in that language; only the five body paragraphs get replaced."""
    if tmpl is None:
        tmpl = os.environ.get("JOBAGENT_LETTER_DE" if lang == "de" else "JOBAGENT_LETTER_EN")
    if not tmpl or not os.path.exists(tmpl):
        sys.exit("no %s letter template: pass tmpl= or set JOBAGENT_LETTER_%s to a .docx"
                 % (lang, lang.upper()))
    if date is None:
        today = dt.date.today()
        date = (today.strftime("%%d. %s %%Y" % MONTHS_DE[today.month - 1])
                if lang == "de" else today.strftime("%d %B %Y"))
        if city:
            date = city + ", " + date
    name = os.path.basename(tmpl)
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
