# STATE = SEARCH

Find Working Student / Internship / Master Thesis roles in Germany that match the resume. `application/resume.md` is the only source of truth on the candidate — never assume skills not in it. Load your browser tooling before any web interaction (see README, "The browser layer").

## Cheapest sources first

Order discovery by token cost, not habit:

1. **Structured APIs / feeds (near-free):**
   - LinkedIn guest API: `python scripts/li_jobs.py search` → `filter` (drops tracker refs and same-position rows) → `screen <ids> --req` (language gate + flags from the full posting). Then resolve apply routes in the logged-in browser with `li_apply_routes(ids)` from `scripts/bh_helpers.py` — one page load per job, no clicking.
   - Employer ATS boards: `python scripts/ats_probe.py boards <slug,...>`, and `personio` / `workday` / `smartrecruiters` subcommands to read a posting (and Personio's required form fields) without a browser. A LinkedIn req missing from the tenant's Workday board is not live — look for its twin.
   - arbeitnow: `curl "https://www.arbeitnow.com/api/job-board-api?search=<kw>"` returns JSON — filter with a small Python script; only survivors enter the conversation.
2. **Boards with strong pre-filters:** XING search, last-24h + Student filter (proven productive). StepStone logged-in — its "Passt hervorragend / weniger" badge is computed against the user's CV: skip "weniger" listings without opening them.
3. **Company career pages / ATS boards:** open only to verify finalists.

A role counts as *found* only when verified live on an official source (company career page or ATS page). Search-engine results and job-board reposts are discovery hints only.

## Keywords

Role terms: Werkstudent, Working Student, Intern / Internship, Praktikum / Praktikant, Master Thesis / Masterarbeit / Abschlussarbeit / Thesis, Student Assistant.
**Thesis quota (user feedback 2026-07-14): every batch must include dedicated thesis searches** — run at least one search pass with thesis-only terms (`Masterarbeit KI`, `Abschlussarbeit Machine Learning`, `Master Thesis AI/LLM`, `Thesis Computer Vision`); aim for ≥ 3 thesis roles per 10 found. Thesis postings often live under "Abschlussarbeit" on German boards and company career pages, not under student-job filters — don't rely on Student/Werkstudent filters to surface them.
Tech terms (from resume): AI, Machine Learning, LLM, Generative AI, RAG, Agents, NLP, Computer Vision, Python, Backend, FastAPI, Data, AWS / Cloud. Secondary: Android / Kotlin, iOS / Swift, Full Stack. Embedded only when it includes software or AI.
Hidden-AI titles: Software Engineer Intern (AI team), ML Infrastructure, GenAI Engineer, AI Solutions, Platform Engineer, Innovation Intern, Research Software Engineer — judge by the description, never only the title.

## Filters (apply during search, before EVALUATE)

- **German postings: check the language line FIRST** — German C1 / C2 / "fließend" / "sehr gut" mandatory → reject immediately (~half of German AI postings die here; don't read the rest first). German-only postings are acceptable only if B1 is explicitly acceptable.
- Freshness: ≤ 7 days preferred; older → mark OLD and deprioritize; unknown date → say so, never guess.
- Hard rejects: Senior / Staff / Principal / Lead / Manager / Director / Architect titles, PhD required, > 2 years mandatory experience, full-time-permanent only, security clearance, citizenship restrictions.
- Actual responsibilities must align with resume skills — "AI" in the title alone is not a match.

## Dedupe

Before recording a find: `python scripts/tracker.py check "<Company>"` — it reports prior tracker rows, package/company folders, the 90-day company cap, and active-interview warnings. A company that rejected or ghosted the user is **not** capped — closed applications free their slot and print `CAP WAIVED` (see evaluator.md § Company cap). Never re-apply to the same role (same ATS ID, canonical URL, or title+location repost).

## Recording

Every verified find: `python scripts/tracker.py add --company X --position Y --location L --ref <ATS-ID-or-URL> --portal <site> --notes "<posting date>; <lang>; <one-line fit>"` (status defaults to `Found`). Irrelevant/stale/duplicate: record only if it cost real effort, as `--status Skipped --notes "<reason>"`.
Chat: one line per job. No tables, no per-job field dumps — the tracker is the record.

Work in cycles of 10 verified roles, then move to STATE = EVALUATE (`prompts/evaluator.md`).

## Offloading (recommended for big batches)

Run the SEARCH cycle in a **Haiku subagent**: pass it this file's rules plus the keyword list; it browses, verifies, runs `tracker.py check`/`add`, and returns only the one-line-per-job list. Search is high-volume/low-judgment — Haiku tokens cost a fraction of the main model's. Keep EVALUATE and APPLY in the main session.
