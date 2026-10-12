# STATE = PREPARE (Cover Letter)

Generate a tailored, single-page cover letter PDF for one specific job. Facts come only from `application/resume.md`; role requirements come from `job_posting.txt` in the package folder. Never invent experiences, responsibilities, achievements, or technologies.

## Content rules (mandatory)

- **Language = posting language.** German posting → German letter, English → English. Never mix.
- **Body 250–260 words in English, 210–235 in German (German words run longer and 250 spills onto page 2), exactly five paragraphs.** No bullet points, no numbered lists, no headings inside the letter.
  1. **Hook** — a thought-provoking question or statement about the field, connected to my motivation, why this company, why this role. Banned openers: "I am writing to apply…", "With great interest…", "I was excited to see…".
  2. **Main experience** — one significant experience: context, the challenge, what I built, what I learned. Show implementation *and* understanding; don't just list technologies.
  3. **Additional experience** — a second relevant project: impact, engineering decisions, relevance to this role; tools mentioned only inside the narrative.
  4. **Personal fit** — how I work (analytical thinking, ownership, curiosity, collaboration), backed by examples or reasoning, tied to the role. No empty claims ("hardworking", "team player").
  5. **Closing** — earliest start date, duration if applicable, enthusiasm for an interview. Polite and professional.
- Map the posting's top requirements to real resume projects — "In project X, I built Y" beats "you need X, I have X". No reused paragraphs across applications, no filler, varied sentence structure, confident but not exaggerated tone.

## Template

Start from the newest existing .docx letter in `Application_Packages/` matching the posting
language — i.e. the last letter you sent in that language. On the first run there is none: build
one .docx per language by hand (header, contact block, fonts, layout) and every later letter is
a copy of it with the five body paragraphs replaced.

Copy it into the job's package folder, then edit with Python + python-docx (installed): update the date, recipient company/address block, subject line, and replace the five body paragraphs. Keep the header, contact block, fonts, and layout untouched.

`scripts/make_cover_letter.py` does exactly this in one call (`build(pkg, recipient, subject, paras, lang="de"|"en")`)
and prints the body word count. It takes the letterhead from `JOBAGENT_LETTER_DE` / `JOBAGENT_LETTER_EN`
(or an explicit `tmpl=`), dates it today, and names the output after the template — so it fails loudly
rather than writing a letter from the wrong language's template. Write the calling script with the Write tool and run it with `PYTHONUTF8=1` —
umlauts typed into a bash heredoc are read as cp1252 and mangle.

**If the CV for this job is a tailored LaTeX one** (`make_tailored_cv.py`), set the letter in the same
design instead: add a `LETTERS` entry under the job's slug in `application/cv_data.py` and run
`PYTHONUTF8=1 python scripts/make_cover_letter_tex.py --job <slug> --compile`. It prints the word
count, `--wordcount` checks every letter against the language's range, and it writes the PDF
directly, so the docx conversion below does not apply.

File names (always inside `Application_Packages/<Company>_<Role>/`):
- English: `Cover_Letter_<Name>.docx` → `.pdf`
- German: `Anschreiben_<Name>.docx` → `.pdf`

## docx → PDF conversion (must be PDF/A)

```powershell
powershell -File scripts/docx2pdfa.ps1 -Docx "<absolute path to .docx>"
```

It writes the `.pdf` beside the `.docx` and prints `<path> <bytes>`. It uses Word COM
`ExportAsFixedFormat` with PDF/A (`UseISO19005_1`) — plain `SaveAs` produces ~7 KB PDFs that
StepStone (min 8 KB) rejects, while PDF/A embeds fonts (~200 KB). Never hand-roll the COM call.

## QA before use

- PDF is exactly one page and ≥ 100 KB (PDF/A check).
- Body is 250–260 words (English) or 210–235 (German) in the correct language, five paragraphs.
- Company name, role title, and date are correct — no leftover text from the template job.
- Every claim traces back to `application/resume.md`.
- If the form has no cover-letter upload but has a motivation/message field, paste the letter body there instead and note in the tracker that no PDF was uploaded.
