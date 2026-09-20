# STATE = APPLY → VERIFY → LOG

Package, submit, and track one qualified job at a time.

## Submission rule

**Auto-submit within a user-approved batch**; outside an approved batch, prepare drafts only. Always stop (never work around) at: MFA, CAPTCHA, payment, phone/SMS verification, suspicious redirects. Login walls: run `python scripts/creds.py check <job-url>` FIRST — it says whether Chrome holds a credential for that host and whether a hit is trustworthy; then read the portal's login section with `python scripts/section.py application/howtologin.md "<Portal>"` (or `"<Portal> — <Company>"`) — if it documents a working path (standard credentials, magic link, quick-apply account), follow it; otherwise record the blocker and move on. Never use SSO / "Sign in with Google" even if the browser is signed in — email + password only (this overrides the browser-harness skill's SSO note).

## Browser efficiency (strict)

- **Helpers:** `exec(open("scripts/bh_helpers.py", encoding="utf-8").read())` (absolute path if the harness runs elsewhere) at the top of a heredoc gives `pick_option` (Workday/Eightfold/SF comboboxes), `upload` (setFileInputFiles by JS expression), `set_text`, `deep_inputs/deep_set/deep_choose/deep_text` (shadow-DOM forms such as SmartRecruiters oneclick), `dismiss_dialog`, `snap`. Use them instead of re-writing the same JS.
- **JS-first.** Read form structure, required markers, validation errors, and upload state via `js()`. Coordinate-click from an existing screenshot; do not screenshot before every click. Budget ≈ 3 screenshots per job: when stuck, optional pre-submit check on complex forms, and the final confirmation.
- **Known quirks first.** The portal's section in `feedback.md` has proven selectors and traps — read it (only it: `python scripts/section.py application/feedback.md "<Portal>"`, or `"<Portal> — <Company>"`) before trial-and-error on the form.
- **German text into a field:** base64-encode the UTF-8 string in Python, then in JS
  `new TextDecoder().decode(Uint8Array.from(atob(B64), c=>c.charCodeAt(0)))` and write it with the
  native value-setter. This is the reliable path — heredocs are read as cp1252, `\uXXXX` gets
  pre-decoded by the harness, and raw umlauts mangle. `String.fromCharCode(252)` also works;
  `scripts/jstr.py` builds such an expression. Always read the value back before submitting.
  Avoid backslashes in JS **regex literals** entirely (`\.`, `\s`, `\n` → "missing /" SyntaxError):
  use `includes()`/`split()` and do regex work in Python. Matching German text inside `js()` fails
  for the same reason — match an ASCII substring (`'berpr'`). (Text read *from* pages is fine.)
- Uploads: direct file-input APIs / CDP `setFileInputFiles`, never native pickers. Verify by filename text on the page, not `input.files` (AJAX inputs clear themselves).

## Package (before touching the form)

Steps 1–3 and 5 in one call: `python scripts/mkpkg.py <Company_Job_Title> <posting.txt|URL|-> <en|de> [--docs transcript,immat,...] [--max-cv-kb N]`
(`-` keeps a job_posting.txt already saved by `ats_probe.py --save`; `--max-cv-kb` for portals with an upload cap).

1. Create `Application_Packages/<Company>_<Job_Title>/` (underscores, no spaces).
2. Save the full job description as `job_posting.txt` in it.
3. Copy the selected CV from `application/CV/Ai/` (or `Embedded/`) into it — the designed CV
   is the default. A German posting gets the German CV (`Lebenslauf_*.pdf`). If you tailor a CV
   for a job, never leave both the designed and the tailored copy in one package folder.
   **The CV never names the employer** — not in the headline, profile, file name, or by
   naming one of their internal projects. Tailoring means selecting and ordering the user's
   own work to match the posting and describing the domain in public terms (a standard, a
   law, a technique). Naming the company is a cover-letter move only.
4. Generate the cover letter in it per `prompts/coverletter.md` (if needed).
5. Copy required supporting documents from `Other Docs/` into it.

Upload **only** files from this package folder — never from `application/CV/` or another package.

## Fill and submit

- Facts only from `application/resume.md` (name, address, phone, languages, education, availability). Unknown optional fields stay blank; never guess legal/eligibility answers — missing required fact → status `NeedsUser`, notes "missing fact: <what>", move on.
- Availability, eligibility and standing answers come from `application/resume.md` § Standing Answers — never from memory of a previous job.
- If the ATS parsed the CV into profile fields, re-check every parsed field (truncated employers, stale addresses, empty rows are common).
- Form QA before submit: required fields filled truthfully · consents checked only as needed · each upload package-local and visible exactly once · correct role, company, and account.
- Validation errors: fix the simple causes (dropdowns, date format, numeric-only salary, file type/size, missing consent) and retry max 2–3 times, then `Blocked` with the reason. Do not spend the batch reverse-engineering one form.

## Email-only applications

1. **`python scripts/tracker.py check "<Company>"` and run the EMAIL GATE query it prints** — the tracker cannot see Gmail, and a sent message to that address means the role may already be applied to.
2. Verify the recipient on an official source, then write `<application_id>_email_draft.txt` in the package folder (To / Subject in posting language / Attachments = package-local filenames / tailored body).
3. **Also create the draft in Gmail** (Gmail MCP `create_draft`; the tool cannot attach files). **Never send automatically.** In chat, explicitly name the documents the user must attach (e.g. "attach Lebenslauf_….pdf + Anschreiben_….pdf from the package folder").
4. **Log the handoff as `Submitted`, never `NeedsUser`** — a `NeedsUser` row reads as unsent forever, so the next backlog drain rewrites the draft and sends it again:

```
--status Submitted --outcome Awaiting --portal "email:<recipient>" \
  --notes "EMAIL HANDOFF <date> to <recipient> (Gmail draft <id>) - unconfirmed"
```

5. End the batch with `tracker.py emails`, which closes the loop the other way: a handoff the user never sent shows up as zero sent messages.

## Verify

Confirmation required: confirmation text/page or confirmation email. Save `confirmation.png` in the package folder (this is a budgeted screenshot). No confirmation observed → status stays `Drafted` or `Blocked`, never `Submitted` (email handoffs are the one exception — see above; they are verified by `tracker.py emails` instead). **At the end of every batch: check Gmail for per-company confirmation emails** — portal "sent" UIs lie (XING has silently failed after showing success); a missing or failure email means not submitted.

## Log

After every job, one call: `python scripts/tracker.py update "<Company>" "<position substring>" --status <Submitted|Drafted|Skipped|Blocked|NeedsUser> --cv <file> --cl <file> --portal <site> --date <YYYY-MM-DD> --notes "<reason/confirmation>"` (row was created during SEARCH; use `add` only if missing).

- New lesson → `python scripts/addlesson.py <feedback|login> "<Portal>" "<Company|General>" "<text>"` — one `(YYYY-MM-DD)` bullet, appended to the right `###` (see the "How to write" block at the top of each file):
  - about getting authenticated (account wall, guest vs. account, password, magic link, session, SSO, autofill) → `application/howtologin.md`;
  - anything else about a portal → `application/feedback.md`, `## <Portal>` → `### <Portal> — General` or `### <Portal> — <Company>`;
  - cross-portal → `application/feedback.md`, `### General — <topic>`.
  Add a `###` only if it does not exist yet; never a second `## <Portal>`. No batch reports or tallies.

Chat: one line. Then STATE = NEXT_JOB: next `Qualified` row (`tracker.py queue`), or back to SEARCH when the batch is done.

## End of batch

When the batch is done (queue empty or user-approved count reached): `list_tabs()`, `close_tab()` every tab opened during this batch, keep exactly one tab open (the last one is fine). This avoids a fresh remote-debugging permission prompt on the next batch.
