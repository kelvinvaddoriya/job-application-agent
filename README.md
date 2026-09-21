# job-application-agent

An autonomous job-application pipeline for a coding agent (built for [Claude Code](https://claude.ai/code),
but the prompts are plain Markdown and port to any agent that can run a shell and drive a browser).

It searches job boards, screens postings against your resume, builds a per-job document package,
fills and submits the application form, verifies the submission, and logs the result — one job at a
time, tracked in a CSV you can merge in git.

The interesting part is not the automation. It is **`application/feedback.md`**: ~50 applicant
tracking systems (Workday, SuccessFactors, Personio, Greenhouse, Lever, Ashby, SmartRecruiters,
StepStone, XING, softgarden, Taleo, iCIMS, d.vinci, concludis, umantis, …), each with the selectors,
traps and dead ends that a few hundred real submissions turned up. That file is why this works on
the second try instead of the twentieth.

Built around the German/EU student market (Werkstudent, Praktikum, Masterarbeit), so the language
handling and several portals are German-centric. The pipeline itself is market-agnostic.

---

## What it actually does

```
SEARCH → EVALUATE → PREPARE → APPLY → VERIFY → LOG → NEXT_JOB
```

| State | What happens | Prompt |
|---|---|---|
| SEARCH | Sweep LinkedIn's guest API and public ATS boards without a browser, dedupe against the tracker, screen language requirements | `prompts/search.md` |
| EVALUATE | Score 0–10 against your resume, check the per-company cap, pick CV language and variant | `prompts/evaluator.md` |
| PREPARE | Build `Application_Packages/<Company>_<Role>/`: posting, CV, supporting docs, cover letter | `prompts/coverletter.md` |
| APPLY | Drive the form in the browser, JS-first, using the portal's known quirks | `prompts/application.md` |
| VERIFY | Confirmation page or confirmation email — portal "sent" screens lie | `prompts/application.md` |
| LOG | One `tracker.py update` call, plus any new lesson filed by `addlesson.py` | — |

Design constraints that shaped everything:

- **Token budget is the real limit.** A session has to cover 30+ applications, so nothing is read
  end-to-end. Knowledge files are sliced by heading (`section.py`), the tracker never enters
  context (`tracker.py`), discovery runs in Python and only survivors reach the conversation, and
  page state is read with JS rather than screenshots (~3 screenshots per job).
- **The agent never crosses a trust line.** It does not type passwords, create accounts, use SSO,
  or solve a CAPTCHA. It fills everything up to that line and hands off.
- **Every answer is true.** A missing fact is `NeedsUser`, never a guess.

---

## Folder structure

```
job-application-agent/
├── CLAUDE.md                  # agent contract: pipeline, where knowledge lives, token rules
├── prompts/                   # one file per pipeline state — the actual procedures
│   ├── search.md
│   ├── evaluator.md
│   ├── coverletter.md
│   └── application.md
├── application/
│   ├── resume.md              # TEMPLATE — fill this in first. Only source of candidate facts
│   ├── feedback.md            # portal knowledge base (not login). Read by section, never whole
│   ├── howtologin.md          # login walls, sessions, autofill. Read by section, never whole
│   ├── applications.csv       # tracker: what you applied to (written by batch sessions)
│   ├── outcomes.csv           # tracker: what came back (written by the email routine)
│   └── CV/
│       ├── primary/           # your designed CVs, EN + DE  (contents gitignored)
│       └── secondary/         # a second variant for a different role class
├── Other Docs/                # transcripts, certificates, references  (gitignored)
├── Application_Packages/      # one folder per job, built by mkpkg.py  (gitignored)
├── scripts/                   # every script the prompts call — see scripts/README.md
└── tests/
    └── bh_selftest.py         # 60+ assertions for the browser helpers, against a local fixture
```

**Rule of the repo: each fact has exactly one home.** A lesson about a portal goes in `feedback.md`
*or* `howtologin.md`, never both; tracker state lives in the CSVs and is only ever touched through
`tracker.py`. This was learned the hard way — the same lesson written in three places is how the
project bloated past its context budget the first time.

---

## Scripts

| Script | Used for |
|---|---|
| `tracker.py` | The only way to read or write the tracker: `check`, `add`, `update`, `queue`, `stats`, `emails` |
| `section.py` | Prints one `##`/`###` section of a knowledge file (`--list` shows every heading) |
| `addlesson.py` | Files a dated lesson under the right portal/company heading |
| `li_jobs.py` | LinkedIn guest-API sweep: `search` → `filter` (tracker dedupe) → `screen` (language gate) |
| `ats_probe.py` | Public ATS APIs: find which ATS hosts a company, read a posting without a browser |
| `mkpkg.py` | Creates an `Application_Packages/<Company_Role>/` folder: posting, CV, docs, optional size cap |
| `make_cover_letter.py` | Fills a .docx cover-letter template with five tailored paragraphs |
| `docx2pdfa.ps1` | Converts .docx → PDF/A via Word COM (the format portals accept; plain SaveAs is rejected) |
| `bh_helpers.py` | Browser form helpers: `keep_rendering`, `form_snapshot`, `safe_click/fill/select`, uploads, shadow DOM |
| `creds.py` | At a login wall: does Chrome hold a saved password for this portal, and what that proves |
| `jstr.py` | Encodes non-ASCII text into a JS expression that survives the harness |
| `xing_apply.py` | Drives a XING "Easy apply" wizard end to end |
| `build_dashboard.py` | Rebuilds `progress.html` from the tracker CSVs |
| `setup_hooks.py` | Run once per clone: git hooks that rebuild the dashboard after a pull or commit |
| `daily_pull.ps1`, `setup_daily_pull_task.ps1` | Windows scheduled task for the morning tracker pull |

---

## Setup

### 1. Requirements

- Python 3.10+ (`:=` and `match`-era syntax is used)
- `pip install python-docx pypdf Pillow` — only for the document scripts
- A coding agent that can run shell commands and drive a browser (Claude Code + a browser tool)
- Windows only for `docx2pdfa.ps1` (Word COM) and the scheduled-task scripts; everything else is
  cross-platform

### 2. Fill in your resume

```bash
cp application/resume.md application/resume.md.bak   # keep the template around
$EDITOR application/resume.md
```

This is the step people skip and then wonder why applications come out generic. Every claim in
every cover letter traces back to a line in this file, and a field with no answer here stops the
batch with `NeedsUser` rather than being invented.

### 3. Add your documents

- `application/CV/primary/` — your designed CV, one per language. The English one must start
  `CV_`, the German one `Lebenslauf_`; the rest of the filename is yours
- `application/CV/secondary/` — a second variant if you apply into two different role classes. Say
  which is which in `prompts/evaluator.md`; drop it if you only have one
- `Other Docs/` — transcript, enrollment certificate, references; map the filenames in the `DOCS`
  dict at the top of `scripts/mkpkg.py`

All three folders are gitignored. **Keep them that way** — this repo is meant to be public, your
paperwork is not.

### 4. Initialize

```bash
python scripts/setup_hooks.py
```

Installs the post-merge/post-commit hooks that rebuild `progress.html`. Hooks live in `.git/`, so
this runs once per clone.

The two tracker CSVs ship with just their header row; `tracker.py add` fills them.

### 5. Optional: the daily email check

`outcomes.csv` is designed to be written by a separate scheduled agent that sweeps your inbox for
replies, classifies each one (Offer > Interview > Rejection > Update > Acknowledged), and pushes
only that file. The split by writer is what makes it merge cleanly with your local batches.

That routine is not included — it needs mailbox access, so it is yours to set up. The contract it
must honour: read `application/applications.csv`, write **only** `application/outcomes.csv` through
`tracker.py update --outcome`, never create rows, never force-push.

### 6. Run a batch

Point your agent at the repo and say so. It reads `CLAUDE.md`, which routes it through the prompts.

For a large batch, run it in two phases with a context clear in between:

1. **Phase A** — SEARCH + EVALUATE the whole batch, filling the tracker with `Qualified` rows. Cheap;
   worth delegating to a smaller model.
2. `/clear`, then **Phase B** — APPLY drains `tracker.py queue` in cycles of 10.

All state lives in the tracker and the package folders, so clearing context between cycles is always
safe.

---

## Configuration

There is deliberately almost none — the prompts are the configuration, and they are meant to be
edited. The things you will actually want to change:

| Where | What |
|---|---|
| `prompts/search.md` | Keywords, role terms, target market, hard rejects |
| `prompts/evaluator.md` | The 0–10 scoring weights, the apply threshold, the per-company cap |
| `scripts/li_jobs.py` → `DEFAULT_KW`, `BAD_TITLE`, `TECH` | The discovery sweep's keyword and filter regexes |
| `scripts/mkpkg.py` → `DOCS` | Your supporting-document filenames |
| `prompts/coverletter.md` | Letter structure, length, banned openers, template paths |
| `JOBAGENT_OWN_EMAIL` env var | Regex matching your own email local-part, so `tracker.py emails` does not read a self-addressed row as a recipient |

---

## The knowledge files

`feedback.md` and `howtologin.md` are the project's memory, and they only stay useful if they stay
sliceable. Both use the same layout:

```
## <Portal>
### <Portal> — General      ← holds for every employer on that ATS
### <Portal> — <Company>    ← one tenant
```

Read one section, never the file:

```bash
python scripts/section.py application/feedback.md "General"          # once per batch
python scripts/section.py application/feedback.md "Workday"          # whole portal
python scripts/section.py application/feedback.md "Workday — Airbus" # one employer
python scripts/section.py application/feedback.md --list             # every heading
```

Write with the script, so the lesson lands in the right place:

```bash
python scripts/addlesson.py feedback "Personio" "General" "Guest apply needs no account; ..."
python scripts/addlesson.py login "Workday" "Siemens" "Tenant has a real account wall; ..."
```

The shipped copy is the **generalized** knowledge: cross-portal rules plus each ATS's
`— General` section. The company-specific sections from the private repo it came from were stripped.
Yours will accumulate as you run.

---

## What is not here

- **CV and cover-letter generators.** The originals were LaTeX/docx builders with one person's
  entire resume hardcoded into them. `make_cover_letter.py` (fill a .docx template) and
  `docx2pdfa.ps1` (the PDF/A conversion that portals actually accept) are included because they
  are generic; the tailored-CV builders are not.
- **The email-check routine** — see step 5.
- **Credentials of any kind.** `creds.py` reads Chrome's password stores for *origins and usernames
  only*; it never reads, decrypts or prints an encrypted password, and the agent never types one.

---

## Notes

Several rules in here look arbitrary until they bite you. A sample from the file:

- Portal "application sent" screens lie. Verify against your inbox, every batch.
- `Input.insertText` concatenates onto the existing value; it does not replace it.
- A stuck-disabled submit button is almost always `document.hidden === true`, not a missing field.
- Ashby's date fields are MM/DD/YYYY, so `01.09.2026` silently means 9 January.
- Uploading three files back to back silently drops two. One at a time, verify by filename in the
  page text.

Each one cost a failed application to learn.

## License

MIT — see `LICENSE`.
