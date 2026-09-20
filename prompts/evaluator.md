# STATE = EVALUATE

Score each found job, decide whether to apply, and select documents. `application/resume.md` is the only source of candidate facts — never assume a skill or experience that is not in it.

## Scoring (0–10)

- +3 strong resume match (actual responsibilities align with resume skills — read the description, not just the title)
- +2 role type is Working Student / Internship / Thesis
- +2 AI / ML / LLM / Python-backend relevance
- +1 posted within 7 days
- +1 English or English+German friendly
- +1 official company application channel (own site or company ATS)

Apply at **7 or higher**. 5–6 is borderline: qualify only if the batch has open slots. Below 5 → `Skipped`, notes "not relevant". Hard rejects from search.md apply regardless of score.

## Language and document selection

- Posting in German → German documents: `Lebenslauf_<Name>.pdf` + Anschreiben. German-only postings only if B1 is explicitly acceptable.
- Posting in English → English documents: `CV_<Name>.pdf` + cover letter.
- CV variant: `application/CV/Ai/` is the default for all AI / software / backend / cloud / mobile roles. `application/CV/Embedded/` only for embedded-systems roles.
- Supporting documents (when the form asks) live in `Other Docs/` and are listed in `application/resume.md` § Supporting Documents; `mkpkg.py --docs transcript,immat` copies them in.

## Company cap

Maximum 2 **still-open** employer-facing applications per company in any rolling 90-day window. `python scripts/tracker.py check "<Company>"` gives the verdict (covers tracker rows, package folders, company folders, and active-interview warnings). `CAP_REACHED` → `Skipped`, notes "company cap". Interview warning → ask the user first.

**A closed application does not occupy a cap slot** (the user's rule, 2026-08-22). A row counts as closed when `Status` starts with `Rejected`/`Ghosted` **or** `Outcome` is `Rejected`/`Ghosted` — both columns are checked, because a row often keeps its submit-time Status after a terminal Outcome lands. Consequences:

- A rejection or ghosting ends the company's process, so it **waives the cap** for that company — `check` prints `CAP WAIVED: … Still open <=90d: N` and the verdict is `OK`. Re-applying to a company that rejected you is fine; re-applying to the *same role* you were rejected for is still a hard skip (CROWN, 2026-08-19).
- The waiver does **not** apply when 2+ applications are still genuinely open — that is the spam case the cap exists for, so `CAP_REACHED` stands.
- The waiver also clears a **folder-driven** cap: `check` counts matching `Application_Packages/` folders as a fallback for unlogged applications, and that matcher is fuzzy.

**The cap verdict is not a dedupe verdict.** Because a rejection waives the cap, `OK` no longer implies "no prior application to this role" — read the `row:` lines and diff the position text for every job. See `application/feedback.md` → `### 2. Dedupe` under `## General`, the most-repeated failure in the project.

## Gate before PREPARE

- ✓ score ≥ 7 (or approved borderline)
- ✓ language requirement satisfiable (English, or German ≤ B1 accepted)
- ✓ CV variant and language chosen
- ✓ cover letter needed? (upload slot or motivation field)
- ✓ supporting documents the form requires identified
- ✓ not already applied (diff the position text, not just the verdict), cap OK or waived, no interview warning

Only continue if every check passes. Set the tracker row to `Qualified` (`tracker.py update`), then STATE = PREPARE (`prompts/coverletter.md` if a letter is needed, then `prompts/application.md`).
