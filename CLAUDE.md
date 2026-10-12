You are an autonomous job application assistant.

Pipeline: SEARCH → EVALUATE → PREPARE → APPLY → VERIFY → LOG → NEXT_JOB.

Always follow these steps.

1. Read prompts/search.md for job search.
2. Read prompts/evaluator.md when evaluating jobs.
3. Read prompts/application.md before applying.
4. Read prompts/coverletter.md only if a cover letter is needed.
5. Read application/resume.md only when factual information is required.
6. Read the `## General` section of application/feedback.md before starting a batch (`python scripts/section.py application/feedback.md "General"`) — never the whole file.

Never read unnecessary files. Never re-read a file already in context.

## Where knowledge lives (keep it there)

Each fact has exactly one home. Writing it in a second place is how this project bloated before.

| File | Holds | Read |
|---|---|---|
| `prompts/*.md` | the procedure for one pipeline state | entering that state |
| `application/feedback.md` | every lesson that is not about logging in: `## General` (cross-portal rules), `## General — detail` (topics), then one `## <Portal>` per portal with `### <Portal> — General` / `### <Portal> — <Company>` | `## General` once per batch; one portal or company section when on that portal |
| `application/howtologin.md` | login lessons only (guest vs. account wall, sign-in, passwords/autofill, magic links, sessions, SSO), same portal → company layout | one section at a login wall |
| `application/resume.md` | the only source of candidate facts | when a fact is needed |
| `application/*.csv` | all tracker state | never — go through `tracker.py` |
| `scripts/tracker.py` | the tracker's rules and its CLI | never — call it |
| `scripts/section.py` | prints one `##`/`###` section of a knowledge file | never — call it |
| `scripts/li_jobs.py` · `scripts/ats_probe.py` | browserless discovery: LinkedIn guest sweep + tracker dedupe + language screen; public ATS APIs (Personio/Workday/SmartRecruiters/…) | never — call it |
| `application/cv_data.py` | gitignored CV content for the generators: the resume.md facts in rendered wording, plus one `JOBS` / `LETTERS` entry per tailored job (template: `cv_data.example.py`) | never whole — `make_tailored_cv.py --keys` / `--list`, then edit the one entry |
| `scripts/make_tailored_cv.py` · `scripts/make_cover_letter_tex.py` · `scripts/make_combined_cv.py` | generators over `cv_data.py`: per-job LaTeX CV, matching LaTeX letter, plain .docx CV | never — call it |
| `scripts/mkpkg.py` · `scripts/addlesson.py` | build a package folder (CV, docs, optional size cap); file a dated lesson into the right `###` | never — call it |
| `scripts/bh_helpers.py` | browser form helpers (`li_apply_routes`, `pick_option`, `upload`, shadow-DOM `deep_*`) — `exec()` it in the heredoc | its docstring, once |
| `scripts/creds.py` | which portals have a saved password, and what a hit proves | never — call it |
| `application/accounts.md` | generated, gitignored table of portals with an account (company / portal / email) | when the user asks which accounts exist — never for a login decision |

**Filing a lesson** (both knowledge files use the same layout):
- Login-related → `howtologin.md`; everything else → `feedback.md`. Never both.
- Portal-specific → `## <Portal>`, under `### <Portal> — General` (every tenant) or `### <Portal> — <Company>`
  (one employer). Employer-owned ATS → `## Own-site forms`. Cross-portal → `### General — <topic>`.
- Append a `(YYYY-MM-DD)` bullet, newest last, to the existing `###`; create a `###` only if it is missing,
  and **never** a second `## <Portal>` or a dated heading. Fix a stale bullet in place instead of contradicting it.
- A batch report or tally belongs in the tracker, not in a file.

## Token discipline (the session budget must cover 30+ applications)

- **Never read `application/feedback.md` or `application/howtologin.md` end-to-end.** Identify the ATS from the URL, then print only its section: `python scripts/section.py <file> "<Portal>"`, or just the employer: `"<Portal> — <Company>"` (`--list` shows every heading). Each portal has exactly one `##`; companies are `###` under it.
- **Browser work is JS-first.** Extract page state (fields, labels, validation errors, upload confirmations) with `js()`. Screenshot only when JS extraction fails twice, or to capture the final confirmation page. Budget ≈ 3 screenshots per job.
- **Login walls: ask `creds.py`, never a screenshot.** `python scripts/creds.py check <job-url>` reads Chrome's saved-password stores (origins and usernames only — never the encrypted password) and returns a verdict *plus* what that verdict is worth: STRONG on a per-tenant hostname (Workday/Taleo/csod/softgarden/umantis), WEAK on a shared one (SuccessFactors, where every employer shares one host and the tenant is a `?company=` param). **Never write `NeedsUser` for a login wall without running it** — that inference has been wrong roughly half the time. `creds.py note <url> --status ... [--company "<Name>"]` records what a login attempt actually proved, so the next batch does not re-derive it — **and every `note` regenerates `application/accounts.md`**, so creating an account during a batch keeps that table current with no extra step. Never hand-edit `accounts.md`; `python scripts/creds.py accounts` rebuilds it, `--verify` self-checks it.
- **Tracker via script, never in context.** Query and update the tracker with `python scripts/tracker.py` (check / add / update / queue / emails / stats — see its docstring once). Never read or edit the CSVs directly, and never print them whole.
- **The tracker is two CSVs, split by writer — still `git pull` before a batch.** `application/applications.csv` (local batches: append rows, set Status) and `application/outcomes.csv` (an optional daily email-check routine: Outcome columns), joined on a stable `ID`. The split is why there is no merge driver: the two writers never touch the same file, and git merges both as text. `.gitattributes` pins them to LF, one physical line per record — never reformat, re-sort, or re-quote them, which would turn a one-line change into a whole-file conflict. **Run `python scripts/setup_hooks.py` once per clone** for the post-merge/post-commit hooks that rebuild `progress.html`; they live in `.git/`, which is never cloned.
- **The dashboard is local-only and rebuilt by hook.** `progress.html` embeds the whole tracker, so it is gitignored. The hooks run `python scripts/build_dashboard.py --if-stale` after any pull or commit that moves a tracker CSV; the same command is a cheap no-op to run by hand if the dashboard ever looks behind.
- **Email applications: the tracker cannot see your inbox.** Before drafting one, run `tracker.py check` and execute the EMAIL GATE query it prints. After handing the draft to the user, log it `--status Submitted --outcome Awaiting --portal "email:<recipient>"` — never `NeedsUser`, which makes a later batch resend it. End a batch with `tracker.py emails` to catch handoffs that were never actually sent.
- **Chat output: one line per job** (`Company — Role — status`). Everything else goes into the tracker, not chat.
- Work one job end-to-end, then the next. No parallel half-done forms.

## Session plan for large batches

1. Phase A — SEARCH + EVALUATE the whole batch first (cheap), filling the tracker with `Qualified` rows.
2. Suggest the user run `/clear`, then Phase B — APPLY drains the queue (`tracker.py queue`) in cycles of 10. All state lives in the tracker and package folders, so `/clear` between cycles is always safe and keeps context small.
3. Phase A may be delegated to a cheaper model's subagent (see search.md) to save budget.
