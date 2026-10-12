# Feedback — lessons by portal (generalized)

Every lesson that is **not** about logging in. Login walls, accounts, passwords, SSO, sessions and
saved-password autofill live in `application/howtologin.md`, which is organised the same way.

This is the distilled, portal-level knowledge base shipped with the project: cross-portal rules plus
one section per ATS. Company-specific lessons from the original private repo were stripped — yours
will accumulate here as you run batches.

**How to read (never end-to-end):**
- Once per batch, read `## General` only: `python scripts/section.py application/feedback.md "General"`.
- On a portal, read that portal: `python scripts/section.py application/feedback.md "Workday"`.
- `python scripts/section.py application/feedback.md --list` prints every section.

**How to write:** `python scripts/addlesson.py feedback "<Portal>" "<Company|General>" "<text>"`.
- One home per lesson. Authentication (account wall, password, magic link, session, SSO, autofill)
  → `howtologin.md`. Everything else → here. Never both.
- Portal lesson → `## <Portal>`, under `### <Portal> — General` if it holds for every tenant, else
  `### <Portal> — <Company>`. Never a second `## <Portal>`.
- An employer's own ATS → `## Own-site forms` / `### Own-site forms — <Company>`.
- Cross-portal lesson → `### General — <topic>`. Only a rule that must be read every batch goes into `## General`.
- Start each new bullet with `(YYYY-MM-DD)`, append newest last, fix stale bullets in place.
- No batch reports or tallies — the tracker is the record.

## General

Cross-portal rules. **This section is the once-per-batch read** — it stops at `## General — detail`.

### 1. Hard rules

- Never invent experience, skills, or facts not in `application/resume.md`. A missing required
  fact — a grade on a scale you have no equivalent for, a profile URL, a reference — is
  `NeedsUser` or `Skipped`, never a guess. Profile URLs (LinkedIn, GitHub, portfolio) are
  verifiable facts and may be used **as written in `resume.md` § Candidate**; never reconstruct
  one from a handle, and never submit a URL you have not seen resolve.

- Never enter or set passwords, never create accounts, never use SSO / "Sign in with Google".

- Never solve a bot-check: captchas, arithmetic security queries, image challenges, Greenhouse's
  emailed 8-character code. **Exception — honeypots:** a hidden / 0-size / `visibility:hidden` field
  is left EMPTY, which the agent may do. Tell them apart with `getComputedStyle` +
  `getBoundingClientRect`, never by the field's name (levigo's "captcha" was a honeypot).

- Upload only files from the job's own `Application_Packages/` folder.

- **One email address, on every platform.** Every portal profile, every account, every
  email-only application uses the single address in `resume.md` — and it must be the mailbox
  the agent can actually read. A portal registered under a second address still works, but its
  confirmations land where VERIFY cannot see them, so the batch-end sweep silently skips it and
  a submitted application looks unsent. If you find a portal profile on another address, fix
  the profile; do not work around it per-application.

- **Answer every eligibility and language question truthfully, from `resume.md` § Languages and
  § Work Authorization.** Never round a language level up: on a 4-level scale with no rung for
  your actual CEFR level, pick the one *below*, never the one above. A truthful answer that looks
  like a disadvantage is often a soft warning rather than a hard gate — submit anyway and let the
  employer decide. A question `resume.md` does not answer is `NeedsUser`, not a guess.

- Re-applying to a company that rejected you is fine. Re-applying to **the same role** you were
  rejected for is a hard skip, even when the employer reposts it.

- A tracker CSV cannot be written while open in Excel. Ask the user to close it; never kill Excel.

### 2. Dedupe — the most-repeated failure in this file

This is where batches go wrong most often, and it has gone wrong in both directions.

- **`tracker.py check`'s `verdict:` line answers the cap question only.** Since a rejection waives
  the 90-day cap, `OK` no longer implies "no prior application to this role". **Read the `row:`
  lines and diff the POSITION text for every job, every time**, and re-run right before APPLY — a
  sibling session may have submitted it since SEARCH. Skipping this sent a duplicate to OTTO FUCHS
  for a role already rejected; doing it caught 5 duplicates in a single later batch.

- **Never truncate `check` output.** Piping through `head` hid the matching rows for Otto GmbH and
  waved through two duplicates. Grep for the ref if you must narrow it.

- Roles are re-listed under new XING/StepStone ids constantly, so **ref-matching alone does not
  dedupe** — the position text is the real key.

- **Employers hide behind other names**: alternate legal names (CROWN Gabelstapler = Crown
  Equipment), group brands (SCOUTASTIC = just-add-ai/STI, ITA Consulting = LetMeShip),
  and aggregator bylines (a "meinestadt.de" or "DS Media" card is someone else's posting).
  Check the group brand and the apply URL's domain, not just the company name.

- **Generic tokens produce noisy `CAP_REACHED`** (Energy, Systems, Solutions, DATA, software):
  `Siemens Energy` matched `Arteus_Energy`; ABEL matched LEONI *Kabel*. The `(+N pkg folders)`
  figure is a hint that something may be unlogged, not a count of applications.

- **A `Skipped` row is a decision the agent recorded, not an observation of the employer's system.**
  MTU's portal said "already applied" against a row marked Skipped. For the same ATS id, check Gmail.

- The tracker cannot see Gmail. For any email-only application, run the EMAIL GATE that
  `check` prints before drafting (see `prompts/application.md`).

- **Dedupe on the COMPANY NAME from the StepStone slug, never on a location token.** Checking
  `tracker.py check "Brueggen"` returned 0 rows and waved through a job the user had already applied
  to in July; StepStone itself caught it, rendering `apply-now-section` as a disabled
  **"Schon beworben"**. The slug carries the employer (`...-Brueggen-Autohaus-W-Schouren-OHG--14189496`) —
  parse the segment before the numeric id and check *that*. An empty `apply-now-section` or a
  "Schon beworben" button is the employer's own duplicate check; treat it as authoritative.

- Cheap safety net: after assembling the batch, diff every queued ref against the whole
  Reference Code column in one pass.

### 3. SEARCH — sources

**No source stays dead.** Nearly every "X is exhausted" verdict in the history was later reversed,
and the cause was usually an extraction bug or a changed URL parameter, not an empty pool
(XING thesis "dead pool" = a virtualized-card bug; StepStone's "dry" thesis pool = `ag=age_7`
silently returning zero). **Re-test before writing a source off.**

- **Broaden past "KI" titles.** AI-titled German student roles are the most C1-gated segment there
  is; plain *Werkstudent/Praktikum Softwareentwicklung / Informatik / Data / Testautomatisierung*
  roles carry far fewer language gates and have supplied the bulk of several 10/10 batches.

- Fetch full postings once to disk and grep them in Python — never page them through context.

- Realistic ceiling is ~3–5 fresh qualified roles per day; a same-day second search round rarely pays.

### 4. EVALUATE — what actually kills candidates

**The German language gate kills 60–75% of technically-good candidates.** It is the dominant filter,
and it hides:

- It lives on the **employer page**, not the aggregator — XING/StepStone/LinkedIn reposts routinely
  drop the level. Always open the employer/ATS posting and grep for Deutsch/German before packaging,
  **even for rows already marked Qualified**.

- It can live in the **ATS form itself** as a required select ("Sprichst du Deutsch auf C1 Niveau?"),
  invisible until you are deep in the application. Scan required selects before investing.

- **Reject on sight:** C1, C2, "sehr gute", "fließend", "verhandlungssicher", "sichere", "exzellente",
  "Deutschkenntnisse ab B2", "muttersprachliches Niveau", "Native-level", "Fluent in German".

- **Acceptable:** "gute Deutsch- und/oder Englischkenntnisse" (no level named), "English C1 required;
  German is a plus", and postings that explicitly name A2 / B1 / B2-as-a-plus. Worth actively
  searching for postings that name a LOW German level rather than only filtering for English-only.

- "sehr gut" is not always about language — read the word after it ("sehr gute *Python*-Kenntnisse").

Then read the **requirements block, not the title**:

- An untitled "Abschlussarbeit" or "Student für eine Masterarbeit" must be opened before qualifying —
  many are BWL market-research, mechanical, or strategy theses ("programmierst du nicht selbst").

- Check the **degree level**: several theses are Bachelor-only, which a Master's student holding a
  B.Tech cannot write.

- Check the **start date** (postings advertise long-past dates) and whether a Praktikum is **paid**.

- Check the **location** against <your city> for on-site roles.

- Follow the apply link far enough to see a real apply control — aggregators with none
  (Südzucker, EVOBYTE class) burn a whole slot.

- **Verify the apply route is alive during EVALUATE, not at APPLY.** 3 of 10 queued rows died at
  packaging time on 2026-09-09: OKAPI's StepStone card said "vor 3 Tagen" but its Personio target
  was a 404 and the board no longer listed the role; GIZEH rendered an **empty `apply-now-section`**
  (posting withdrawn) with nothing on the employer board either. One `js()` on the posting that reads
  the apply control's existence and, for routers, follows `Unternehmenswebsite` once, costs far less
  than a package folder plus a tracker row.

- Check the apply href for `successfactors` / `workday` before investing: one `js()` call saves the
  entire packaging step.

- **A clean language line is not a reason to apply to a role that does not fit.** Skipping a bad fit
  is correct; so is surfacing a fit gap to the user rather than papering over it or inventing a
  qualification.

### 5. APPLY — channel classes

Yield is decided almost entirely by which channel the role lives on. Classify first, then invest.

- **Converts unaided:** Personio guest (the single most reliable), StepStone inline smart-apply,
  XING quick-apply, LinkedIn EasyApply, Recruitee, Lever, JOIN, Ashby, concludis/rexx, d.vinci,
  SmartRecruiters oneclick, Breezy, Factorial, HRlab, Prescreen, guidecom, and small-employer
  own-site guest forms.

- **Credential / identity walls — prep and hand off:** SuccessFactors (career5/55/74), Avature,
  Taleo, umantis (now auto-registers with a required `Passwort*`), iCIMS and Workday **per tenant**.
  Do not write Workday off wholesale: classify by clicking Apply and counting steps plus
  `input[type=password].length` — some tenants run a 5-step guest flow with no password at all, and
  "account wall" verdicts read off a `/login` page have been wrong four times. Open the job's own
  `/apply` URL and look for "Manuell bewerben" first.

- **Bot-check walls — fill everything, hand off the same day:** Greenhouse (emailed 8-char code),
  reCAPTCHA v2, arithmetic security queries, image captchas, BambooHR, CHECK24 (its
  Vermittlungsvertrag is a placement contract, which is the user's call, not a data consent).
  Check whether the **logged-in** path skips the gate first — anti-bot gates usually target
  anonymous traffic only (Porsche's arithmetic query vanished after sign-in).

- Cap form-fighting at ~3–4 submit attempts, then fall back to email or a handoff and move on.

- Before the final submit, scan the page **text** for `*` markers and diff them against what you
  filled — required fields without a `required` attribute have silently eaten submits.
  After any failed submit or POST bounce, **re-upload every file**.

### 6. Tooling — browser and encoding

- **Input method is per-ATS, not global.** `fill_input` (real key events) enables StepStone
  smart-apply but no-ops on Workday and Ashby; focus + `Input.insertText` works there and on date
  fields; the native value-setter works for plain text and selects but leaves React unconvinced on
  many forms. **Read every value back after a fill batch** — `fill_input` has typed into the
  previously focused input.

- **The native setter concatenates onto typed text**, it does not replace it (doubled values
  survived to Workday's Review page). Click, Ctrl+A, Delete, assert `.value.length === 0`, insert once.

- **German text and JS regex literals** have their own recipe — see `prompts/application.md`
  § Browser efficiency. The lesson behind it: every "the form rejected my input" report in this
  file's history was an encoding or event-semantics problem, not a broken form.

- **Date formats:** Ashby and react-datepicker are MM/DD/YYYY — "01.09.2026" silently means 9 January.

- **Uploads:** verify by filename in the page text, never `input.files` (AJAX inputs clear
  themselves). Upload one file at a time — three back-to-back `setFileInputFiles` calls silently
  dropped two and an application went out incomplete.

- **A submit with no error, no URL change and no confirmation** is an overlay or an out-of-viewport
  rect, not a broken form: hit-test with `document.elementFromPoint` and try a JS `.click()` second.
  Consent/cookie overlays have swallowed submits on every engine in this file.

- **When input seems wedged, check `js("document.hidden")` FIRST** — a background tab makes Chrome
  refuse `Input.*` and screenshots while `Runtime.evaluate` keeps working. Try `Page.bringToFront`
  once. Second suspect: two `browser_harness.daemon` processes fighting over the socket. A *browser*
  restart fixes it, a daemon restart does not — but **do not fight it**: JS-only paths
  (`el.click()`, full pointer-event sequences, `DOM.setFileInputFiles`) have carried entire batches.

- **`document.hidden === true` is the single most common cause of "the submit button is stuck
  disabled".** It hit StepStone smart-apply, Workday and Ashby-style forms alike on 2026-09-09, and
  in every case the button's `.disabled` flipped `true -> false` the instant the tab became visible.
  `Page.bringToFront` alone is NOT reliable — when another tab keeps stealing the active target it
  silently no-ops. The move that always worked: `Browser.getWindowForTarget` ->
  `setWindowBounds(windowState="minimized")` -> `setWindowBounds(windowState="normal")`, then re-read
  `document.hidden`. Do this BEFORE concluding a required field is missing.

- **While `document.hidden` is true, `Input.dispatchMouseEvent` is dead but `Input.insertText` still
  works** — JS `el.focus()` + `el.setSelectionRange(0, el.value.length)` + `Input.insertText` filled
  Workday's text fields when coordinate clicks could not even move focus. Ctrl+A as a key event does
  NOT select in that state; use `setSelectionRange`, or the insert concatenates onto the old value
  (`<postcode2>` + `<postcode>` = `<postcode2><postcode>`).

- **When a foreign tab keeps grabbing the daemon's active target, put `switch_tab` + `bringToFront`
  at the top of EVERY call** and do the whole step in one script. Reading `location.href` from what
  you assume is your tab is how a "failed" submit gets logged: mid-batch the daemon jumped to an
  unrelated `127.0.0.1:5173` tab three times.

- **`goto_url` hits the daemon's ACTIVE tab, not the last one you opened** — `switch_tab` first, or
  it destroys a parked form. Never bulk-close tabs while handoffs are parked.

### 7. VERIFY — Gmail is the authority, the portal is not

- **Portal "sent" pages lie**, repeatedly and in both languages. XING has shown a full success screen
  and mailed "your application didn't arrive" six minutes later. Never close a batch without the
  Gmail sweep.

- **Portals that send no confirmation mail** (the on-page thank-you + `confirmation.png` is the
  proof): HELLA/csod, softgarden, Rohde & Schwarz, q23, several own-site forms.

- **A portal whose profile email is not your `JOBAGENT_EMAIL` is invisible to this check.**
  Its confirmations land in a mailbox the agent cannot read, so the batch-end sweep silently
  passes over it. Fix the portal's profile email; until then, verify that portal on its own
  success page instead, and note it here.

- **After a handoff comes back "done", verify each one against Gmail AND the tab's URL** before
  writing `Submitted`. One in three has come back done-but-not-sent (a reverted CHECK24 form, an
  umantis security-token failure) — and a parked form that still shows every value can still be dead.

### 8. Handoffs and the NeedsUser backlog

**The proven division of labour:** the agent does search, dedupe, packaging, cover letters and the
entire form; the user crosses the credential line and clicks submit. Plan batches around this rather
than discovering it per job — a 17-row backlog drained 17→0 this way, and draining a backlog has
been higher yield per token than the fresh search that opened the same session.

- **Prefill-then-handoff only pays if cleared within ~a week.** After that the row is usually worth
  re-applying rather than resuming (dead reqs, expired tokens).

- **Parked tabs do not survive a Chrome restart**, and durability must be judged by whether the
  *submit* succeeds, never by whether the fields still look filled. Park each handoff in its own
  `new_tab` and record enough in the tracker notes to refill from scratch.

- **Re-test the recorded blocker before treating a `NeedsUser` row as stuck.** ~30% of a backlog is
  stale rather than blocked, and several "automation-proof" and "account wall" verdicts were simply
  wrong when retried — the note describes what the agent saw once, not what is true now.

- `NeedsUser` rows older than ~1 week get a **Gmail check before a browser retry** — one sat three
  weeks as phantom backlog while the user had finished, been asked for documents, and been rejected.

- When re-opening a handoff, read the URL and page state first: a row can be further along than its
  note says (umantis puts screening questions *after* account creation).

### 9. Tracker hygiene

- **Always pass `--status` on every `update`** — without it, Status is wiped to None.

- **When an interview process ends, close `--status` in the same turn as `--outcome`.** The interview
  warning keys off Status alone, so a recorded rejection in Outcome does not lift it and the company
  stays blocked for every future batch.

- **When the user mentions an interview or a call, update the row that turn.** Phone-stage outcomes
  never reach Gmail, so the daily email routine cannot catch them — the tracker is the only record.

- Rows are job applications only. Personal/admin mail gets flagged in chat, never added as a row.

- `git pull` before a batch: the daily email-check routine writes Outcome columns on its own
  schedule. Since 2026-09-07 it writes `outcomes.csv` while batches write `applications.csv`,
  so the two no longer collide; a conflict now means both sides edited the same file, and each
  side still holds work the other has never seen. Merge the lines, never pick a side.

### General — Browser tooling

- (2026-09-18) document.hidden / stuck-disabled submit buttons now have a one-call fix: keep_rendering() in bh_helpers (CDP Emulation.setFocusEmulationEnabled, ported from browser-use/jev-ultrafast). It makes a background tab report visible+focused and keeps rAF running, persists across browser-harness calls while the daemon lives, and replaces the minimize/restore window trick in section 6. Pair it with form_snapshot() (one call: every control incl. shadow DOM, required flags, ids, errors) and safe_click/safe_fill/safe_select (hit-tested, refuse to click through overlays, read-back verified). Self-test: browser-harness < tests/bh_selftest.py (63 checks).

- (2026-09-25) NEVER verify a German-language upload by grepping the page text for 'Lebenslauf' or 'Anschreiben' - those are the FORM'S OWN FIELD LABELS and match whether or not a file attached. An Erbe/Persis submit died with chrome-error ERR_FILE_NOT_FOUND because the package folder had never been built (its XING ld+json fetch had 410'd earlier in the batch), the upload silently set a nonexistent path, and the 'Lebenslauf in page text' check passed on the label. Verify with the FULL filename ('Lebenslauf_<Name>'), and on widgets that never render a filename (Persis) fall back to input.files[0].name - which is legitimate here because Persis is not an AJAX input that clears itself. Also: os.path.exists the file in the same heredoc before calling upload().

- (2026-09-25) End-of-batch tab cleanup silently closed a parked handoff that WAS in the keep-list: the KINEXON Greenhouse tab matched the keep substring 'greenhouse.io/embed/job_app?for=kinexon' yet was gone afterwards, and the loop's own 'kept' printout never listed it while the remaining-tab count (5) disagreed with the kept count (3). Never trust the keep filter - after closing tabs, re-run list_tabs() and assert each parked handoff URL is still present, because a closed park means the next session must refill the whole form. Cheap mitigation that worked: every parked form here was reproducible in one pass from the tracker note, so write the full field list into the note at park time rather than relying on the tab surviving.

### General — Search and sources

- (2026-09-14) **Two LinkedIn guest-API sweeps (18 + 18 keywords, r259200 then r604800) + full-posting language screen in Python** produced 10 submits in one batch after two earlier batches the same day; routes resolved from the logged-in page's Apply href. Company-cap/dedupe in the filter must index `tracker.load()` rows as 0 Date, 1 Company, 2 Position, 4 Reference Code.

- (2026-09-23) XING thesis pool is deep but mostly already-worked: of 12 fresh Abschlussarbeit/Masterarbeit cards, 4 were language-gated (sehr gute Deutsch: Syneco, Pan Dacom, Senacor, OPTIMA), 3 were exact duplicates already Submitted under the same xing ref (ABB 157050784, Funke 156659662, UVC 157483959 via arbeitnow), 1 was a role the user was already REJECTED for, and 3 DLR theses died on the company cap. Extraction note: while logged OUT, a XING job page renders its 'Similar jobs' block into innerText ahead of the posting, so scraping the first lines yields the WRONG company and title (cost several calls). Read script[type=application/ld+json] instead - it gives hiringOrganization.name, title, datePosted and the full description in one js() call, which is also the cheapest language screen.

- (2026-09-24) The li_jobs.py language screen flags any 'sehr gute Deutsch' hit as BAD, but the surrounding conjunction decides: Siemens' Masterarbeit ML Roaming Assistant reads 'Sehr gute Deutsch- ODER Englischkenntnisse', which strong English satisfies, while Mercedes' 'Sichere Deutsch- UND Englischkenntnisse' is a real gate. Always read the screen's context line, never the BAD/ok verdict alone - an OR clause is the cheapest source of qualified German-language postings there is. Thesis pools on 2026-09-24: LinkedIn (2 sweeps, 27 thesis keywords, 2000+ cards) yielded 8 thesis cards of which every one was capped, already applied, or language-gated; StepStone's thesis keyword searches returned 4 hits (ams OSRAM, Bitnamic, intension, Eisenmann) all dead on language, 'Schon beworben' or Bachelor-only; arbeitnow returned zero. XING was the only live thesis source (13 fresh ids >= 157500000 from 5 keyword sweeps, 5 survived dedupe) - read script[type=application/ld+json] per posting for company/title/datePosted/description in one js() call.

- (2026-09-24) Second search round the same day DID pay, against the rule of thumb - 22 verified finds. What worked: a 14-day LinkedIn guest sweep with 12 thesis keywords (424 cards, 12 new) plus a 10-day sweep with 14 broad Werkstudent/Praktikum keywords (224 new cards) - the BROAD sweep carried the batch, the thesis sweep gave 1 usable role. XING: 8 thesis keywords x 2 pages with scroll-extract = 199 slugs, 38 fresh (id >= 157.5M), 30 after tracker dedupe, 18 opened, 10 language-gated, 2 usable. Accumulate the slugs in localStorage.__JOBS, not a window variable, and avoid JS regex literals - test the trailing id with String(Number(tail))===tail. arbeitnow returned 250 cards and ZERO thesis roles. StepStone 6 keywords x 2 pages = 384 cards, 43 thesis+tech, 4 survived language, 2 of those were exact duplicates of already-Submitted rows - 1 usable. ats_probe boards across 20 German AI/tech company slugs found 4 usable student roles (Langdock/Ashby, KINEXON+NavVis/Greenhouse) for almost no tokens - worth a standing pass. THE REAL CONSTRAINT ON THESIS ROLES IS THE COMPANY CAP, NOT THE LANGUAGE GATE: DLR, Fraunhofer (13 open), BMW, AGCO, Mercedes, HELLA and Freudenberg all had live, language-clean thesis postings that were capped out.

## General — detail

Dated cross-portal lessons behind the rules above, by topic, newest last. Grep one `###` topic when it comes up.

### General — Dedupe

- Never re-apply to a role already in the tracker, `Application_Packages/`, or `Companies/`.

- 2026-07-04 — tracker.py check gave false CAP_REACHED for short company names ("b-trend" → token "b" matched 9 folders); fixed matcher (tokens ≥3 chars). Rule: when a cap verdict looks absurd, read the matched rows before skipping a job.

- 2026-07-14 — dedupe gap found: goaudio "Working Student Full-Stack & AI Engineering" was emailed twice (2026-07-01 and 2026-07-14, same role, same address) because the second NeedsUser row was created without checking Gmail sent history, only the tracker. Rule: tracker.py check only sees tracker rows/folders — for email-only applications, also search Gmail sent (to:<company-email>) before creating a new email draft, since a prior send may not have made it into the tracker.

- 2026-07-19 — XING dedupe is the bottleneck, not discovery: of the 5 best XING finds, 4 were dupes only caught by reading the prior tracker rows — Silver Atena (same XING id 155744844, already Skipped stale + CAP_REACHED), **CROWN Gabelstapler GmbH = "Crown Equipment Corporation"** (same thesis role already Submitted under a different legal name), MTU (same role the user explicitly dropped 2026-07-14), Krones (prior row records "sehr gute Deutschkenntnisse" gate that is only on the official page, not XING). Rule: XING lists employers under alternate legal names — always read the matched tracker rows' Position text, never trust the company-name check verdict alone.

- 2026-08-15 (duplicate-send post-mortem, the user: "why were they sent twice?") — **Clar AI, Next Intelligence and Hutter und Unger were each emailed TWICE** (18.07+12.08, 24.07+12.08, 07.08+12.08). Root cause is the email handoff itself: the agent creates the Gmail draft and *the user* sends it, so the send happens outside the agent's view and nothing ever flips the row — it stays `NeedsUser` with notes "send email - Gmail draft rXXXX", which reads to the next backlog-drain as *not yet sent*, so a new draft gets written and goes out again. The 12.08 sends were 25s apart (one drain pass) and that session ALSO failed to log them, which is why they were still `NeedsUser` on 15.08. **This exact gap was already written up on 2026-07-14 (goaudio, emailed 01.07 + 14.07) and the written rule did not hold — so it is now enforced in code, not prose.** Two fixes: (1) **a handed-off draft is logged `--status Submitted --outcome Awaiting --portal "email:<recipient>"`, never `NeedsUser`** — the application is out of the agent's hands at handoff and there is nothing left for a later batch to do; (2) **`tracker.py check` now prints an EMAIL GATE** (recipient + the exact `in:anywhere to:<addr>` query) for any company with an email-channel row, and a new **`tracker.py emails`** subcommand lists every email row with one combined Gmail query — 0 sent messages = a handoff the user never sent, 2+ = a duplicate. The optimistic `Submitted` is safe precisely because `emails` closes the loop the other way. Detector note: matching any address anywhere in Portal/Notes flagged **71 rows, nearly all ATS confirmation SENDERS** (no-reply@concludis, system@successfactors, *@myworkday) plus the user's own alternate inbox — an email-channel row must *declare* itself via `Portal: email:<addr>` or an explicit send-email marker in Notes. Also found and fixed a second dedupe hazard in the same rows: the Clar AI row was filed under company **"Early-Stage AI Startup (Munich)"**, which no future `check "Clar AI"` would ever match (`update --newcompany` added for renames). **Rule: for any email-only application, the Gmail sent folder is the authority on whether it went out — the tracker is only a claim.**

- 2026-08-22 — **The 90-day company cap now counts only STILL-OPEN applications; a rejection or ghosting frees the slot and waives the cap** (the user's rule). Implemented in `tracker.py` as `is_closed()`, which checks **both** `Status` and `Outcome` — that mattered: **67 rows carried a terminal `Outcome=Rejected` while `Status` was still the employer-facing value from submit time**, and every one of them had been silently eating a cap slot. the user's two calls on the edges: (a) the waiver does **not** apply when 2+ applications are still genuinely open — that is the spam case the cap exists for, so `CAP_REACHED` stands; (b) `Ghosted` discharges a slot the same way `Rejected` does, since a no-reply application is dead in practice. **The bigger finding while implementing it: most `CAP_REACHED` verdicts were never coming from the row statuses at all.** `cap = max(recent, recent_pkgs)` also counts matching `Application_Packages/` folders, and that matcher is fuzzy — `Siemens Energy`'s count of 4 included `Arteus_Energy` and `SFC_Energy`, two unrelated companies, and Mercedes/AUDI were folder-driven too. The waiver now clears a folder-driven cap as well, and `check` prints `open employer-facing <=90d: N (+M pkg folders)` so the two signals are no longer conflated in one number. **Rule: `(+M pkg folders)` is a hint that something may be unlogged, not a count of real applications — read the rows.** Net effect on the current sheet: Mercedes, AUDI, Siemens Energy, CROWN, Xsolla, ICB, MESSRING, elunic and ABEL all flip from `CAP_REACHED` to `OK`; the cap still fires for the 4 companies with 2+ open rows (Retorio, Ströer Content, Clar AI, Himbeer Media) — verified both directions. Unchanged: re-applying to a company that rejected you is fine, but re-applying to **the same role** you were rejected for is still a hard skip (CROWN, 2026-08-19).

- 2026-08-23 — **Two duplicate near-misses caught by rules already in the playbook.** (1) A StepStone card advertised by *meinestadt.de* was actually a **Peras GmbH** posting already submitted on 2026-08-16 under a different id — always read the employer off the opened posting, never off the card. (2) `fields()`-style dumps that truncate `option.value` produce silently-failing `setval` calls on VORGABEWERT selects — **match select options by their TEXT**, not by a truncated value.

- 2026-08-23 — **A `Skipped` row is NOT proof that we never applied — Gmail is the authority.** MTU's portal rejected today's attempt with "already applied"; Gmail then showed a Bewerberprofil created 2026-07-14 and a rejection on 2026-07-21 naming *"Abschlussarbeit Machine Learning (all genders)"* — the exact role. Tracker row 180 had it as `Skipped`, and my dedupe note literally read "prior row was Skipped never applied", so the wrong status is what waved the duplicate through. Row 180 is now corrected to Rejected. **Rule: when `check` returns a `Skipped` row for the SAME ATS id you are about to apply to, verify it against Gmail before treating the slot as free — `Skipped` is a decision the agent recorded, not an observation of the employer's system.** (Cheap on XING: an applied posting renders "You applied for this job on <date>" in the body.)

- 2026-08-23/24 (thesis-priority batch of 10) — **The batch's defining mistake: I re-applied to a role the user had already been REJECTED for.** OTTO FUCHS "Masterarbeit KI und Computer Vision" went out via SmartRecruiters and was Gmail-confirmed before I noticed tracker row 153 — same role, same ATS, rejected 2026-07-22. Cause: during EVALUATE I ran the position-level row diff on only *some* of the shortlisted companies and took `tracker.py check`'s one-line `verdict: OK` at face value for the rest. **That verdict is now routinely `OK` for companies with history, because a rejection waives the 90-day cap (2026-08-22 rule) — so `OK` no longer implies "no prior application to this role".** Re-checking the other nine immediately afterwards caught **four more duplicates before submitting** (SAP and Groz-Beckert had both been submitted by the user *earlier the same day*; BMW's xing id was already a Blocked row from the same day; Dräger's role was row 1085 + a Rejected row 371). **Rule: `check`'s verdict line answers the cap question only. Always read the `row:` lines and diff the POSITION for every single job, no exceptions — and re-run it right before APPLY, because a same-day sibling session may have submitted it since SEARCH.**

- 2026-08-25 — **`tracker.py check` output must be read in FULL, not `head`-ed.** I piped `check "Otto GmbH"` through `head -5`, saw only OTTO FUCHS / Ottobock / ottonova / Otto Group one.O, and concluded Otto GmbH & Co. KGaA was fresh. Both roles had in fact been **submitted 3 and 6 days earlier** — the matching rows were below the cut, and the package folders (`Otto_Werkstudent_*`) were the tell I also truncated away. **Rule: never truncate `check` output; if you must, grep for the ref, never `head`.** A cheap safety net that caught this and 8 other dupes: after building the batch, diff every queued ref against the whole Reference Code column in one pass.

- (2026-08-30) **Build the dedupe check-list FROM `tracker.py queue`, never by hand.** Baumann was left out of the sweep
  entirely and only surfaced when `update` refused an ambiguous match — the same role had been submitted six days
  earlier. Iterate the queued rows and check every one; a company you "obviously" have not applied to is exactly
  the one that gets skipped.

- (2026-08-30) **Short company names collide inside `check` and hide the matching rows.** `check "Sappi"` printed only **SAP**
  rows, so a duplicate went out to *Sappi Ehingen — Werkstudent Data Scientist*, a role already **rejected**
  2026-07-02 (row 44) and therefore a hard skip. `check` is a grep, not an answer: after running it, grep its
  output for the POSITION text as well, and treat any company whose name contains a shorter company's name
  (Sappi/SAP, Axon/Apraxon, init/appliedAI, Top Werk/…) as a name that needs a second, position-level look.

- (2026-08-30) **Run the ref+position dedupe over the WHOLE queue before APPLY, not per-company as you add rows.** Four of ten
  queued rows this batch were duplicates and `tracker.py check` caught none of them at add-time because I never ran it
  on those companies: Sammer (identical ref, submitted the previous day - found only because the package folder already
  existed), Blickfeld ("Werkstudent IDP Software Development" submitted 2026-07-23, reposted in **English** under a new
  id), Barmag (identical title **Rejected** 02/07/2026), Peras (submitted 2026-08-16). **A ref diff alone cannot catch a
  repost under a new id, and a per-company `check` cannot catch what you never pass to it.** Drive one pass over
  `tracker.py queue` that diffs company AND position text against every prior row, and run it *after* the queue is
  assembled - that pass caught all four in one call.

- (2026-08-30) **A pre-existing `Application_Packages/<Company>_<Role>/` folder with a `confirmation.png` is proof of a prior
  submission**, even when `check` reports "0 pkg folders". Trust the filesystem over the counter.

- (2026-08-30) **A `Skipped` row for the same role is not a duplicate - re-read WHY it was skipped.** WiBU had been skipped
  2026-07-13 on an HRworks upload "hang" that was later diagnosed as a selector bug (ids starting with a digit need
  `input[id="19-488"]`, not `#19-488`). It submitted first try today. Re-test skipped rows whose reason was a tooling
  failure.

- (2026-08-31) **Aggregator bylines hid the real employer twice in one batch:** the XING card said *Motius* but studyflix and the
  ATS both resolve to **eigenblue** (`eigenblue.breezy.hr`), and *Novotechnik* applies through the **Siedle Gruppe**
  pi-asp tenant (`tenant=RSIEDLE`). Run `tracker.py check` on the ATS-domain name too, not only the card name.

- (2026-09-01) **The clean-language pool is not the bottleneck; the DEDUPE rate is.** ~60 fresh StepStone/XING cards screened
  gave 6 qualified rows, and the second search round was ~100% duplicates (logen.ai, ARTEMEON, snapADDY, C24,
  Schouren, Scaile, HMS, DaphOS all already applied — DaphOS only caught by StepStone's own "Schon beworben").
  **Grep the card list against `tracker.py check` BEFORE opening any posting**, and treat a second search round
  in the same day as unlikely to pay.

- (2026-09-04) **`tracker.py check` substring collisions bit again, in the CAP direction.** `check "BHS Intralogistics"`
  reported **CAP_REACHED** purely because "BHS Intralogi**sti**cs" contains "**STI**" and matched
  *STI GmbH*; the real BHS prior count is 0. Same class as Sappi/SAP. **Read the `row:` lines before
  believing a CAP verdict, not just before believing an OK verdict.**

- (2026-09-04) **The queue-wide dedupe pass earned its keep four times in one batch**, and three were invisible to a
  ref diff: ZEISS 14082304 "Working Student Automation, Software Development & Data Analysis" (Wetzlar)
  is **yesterday's** German req reposted in English under a new StepStone id; RECONIQ "Werkstudent Test
  Automation" and HMS "Werkstudent Software Development, Data & AI" were the *same position* already
  submitted/rejected; Quantum Systems "Working Student Full-Stack Software Development" was **rejected**
  under the identical title. Pan Dacom's generic "Bachelor-/Masterarbeit im Bereich Software" was skipped
  as a near-duplicate of the KI-Wissensassistent thesis submitted there three days earlier.

- (2026-09-06) **TWO SESSIONS RAN THIS BATCH AT ONCE AND NEITHER KNEW.** While this session was mid-form on Statista's
  Ashby page, another session searched, applied to, and logged **Statista, LVM x2, NXP, WVV, Kontron,
  Geiger, Bechtle, AVAT, Landeskrankenhilfe, KI-PIE, Primetals and Soloplan** - 12 rows dated 2026-09-06
  that this session never created - and left ~40 tabs plus 5 staged handoff forms in the shared Chrome.
  The tell was the daemon's ACTIVE tab silently becoming a XING custom-apply flow for a job this session
  had never opened. **Before resuming any batch after an interruption, `git pull` AND re-run
  `tracker.py queue` before touching the browser** - the queue had drained to 0 without this session
  writing the rows. And **never `close_tab` at end of batch when tabs you did not open are present**: the
  end-of-batch tab cleanup in application.md would have destroyed 5 staged handoffs. Prefer leaving tabs
  and saying so.

- (2026-09-06) **`tracker.py check` output must not be grepped, not just not `head`-ed.** Grepping check's output for
  `row:|verdict|CAP` hid the row that mattered: ZEISS "Abschlussarbeit Data Science / Mechanikdesign" was
  already **Submitted 2026-08-30 and Rejected**, and it went into the queue as Qualified. The full-tracker
  position diff caught it before any form was touched. The 2026-09-04 lesson said "read the row: lines
  before believing a CAP verdict" - extend it: **read them before believing ANY verdict, and do the
  position diff against the whole sheet, not against check's filtered view.**

- (2026-09-06) **The pool was ~85% already-worked.** 260 unique StepStone slugs and 271 XING slugs reduced to 9
  genuinely new qualified roles: the German gate killed ~55%, and the queue-wide dedupe then killed most
  of the rest (UVC Partners, Mischok, Crown, Dr. Sasse, RECONIQ, Rheinmetall, ROSEN CV/ML, dSPACE, ABB,
  OTTO FUCHS, CLAAS x2, Syntegon, viadee, encadi, STERNAUTO, Klangio, Prodware, Sopra Steria, GECKO,
  OpenKnowledge, Ehrhardt+Partner were all the SAME position already submitted or rejected). On a day
  like this the honest ceiling is ~5 fresh roles; padding to 10 means re-applying to rejections.

- (2026-09-06) **Four companies were CAP_REACHED (2 open applications inside 90 days): FORVIA HELLA, Mercedes-Benz,
  ROSEN, BMW.** Mercedes-Benz is worth noting because its reqs dominate every StepStone/XING thesis
  search - MB AG, MB Group, MB Werk Bremen, MB Consulting, MB Tech Innovation and MBition all count as
  one employer for the cap, so a thesis sweep can look productive and yield nothing applicable.

- (2026-09-08) **Check the legal entity before trusting a company cap.** `tracker.py check "Draeger"` said
  CAP_REACHED, but the Feuerwehrverwaltung role belongs to **Dräger Safety AG & Co. KGaA**, a different
  employer from Drägerwerk AG & Co. KGaA. Same lesson as the Fraunhofer per-institute finding: qualify
  the row with the entity that actually hires.

- (2026-09-10) **Run `tracker.py check` on EVERY company, not just the ones that feel new.** `tracker.py add`
  dedupes on company+position and caught XITASO (same thesis, *rejected* 2026-08-30 - a hard skip),
  but it MISSED autarc because the older row reads `autarc (autarc energy GmbH)` and the new one
  `autarc` - same position, submitted 7 days earlier. Only `check` caught it. Legal-suffix drift
  defeats the add-guard.

- (2026-09-10) **A CAP_REACHED verdict from package folders alone is noise.** PHW-Gruppe returned CAP_REACHED off
  three unrelated `*_Gruppe_*` folders while its own row count was 1; E-T-A matched on nothing at all.
  Read the `tracker rows:` figure, not the verdict line.

- (2026-09-11) **`tracker.py check` misses umlaut transliterations.** "Dr.*gerwerk" found Draeger rows spelled with
  the umlaut but not the 2026-09-08 row spelled "Draegerwerk" - the role was re-queued and only the
  Draeger portal's "Eingereichte Bewerbungen" list caught the duplicate. Check both spellings (ae/ä,
  ue/ü, oe/ö) for every German company.

- (2026-09-12) Duplicates caught by the position diff this batch: SAP, Volkswagen, Avelios, Mubea, Dematic, XITASO, Isar
  Aerospace - 7 of them, every one a company whose cap verdict read OK. The diff is doing real work.

- (2026-09-12) **2026-09-13 continuation (the last five): 0 submitted again, and each loss was a different wall.**
  DLR - **alias trap**: `check "German Aerospace"` found one closed row; `check "DLR"` found the two OPEN theses
  (5979, 5866) and CAP_REACHED. Caught one step before submit. Always run `check` on every short name / acronym.
  SUXXEED and Vanderlande - **the LinkedIn copy is not a language screen**: both passed the regex on LinkedIn's
  text, and both employer pages demand German (C1 / "sehr gute Deutschkenntnisse"). Screen on the employer's page.
  TARGOBANK - PeopleSoft CV attachment never links (howtologin section added). BNP Paribas - Avature
  `manualRegisterMethodsForm` = account registration, a hard stop.

- (2026-09-24) A LinkedIn card's employer name is not authoritative - same class as the StepStone slug lesson. A row queued as 'ProTek Systems - Werkstudent Digitalization and AI' (softgarden 67430862) opened as POLY-CLIP SYSTEM GmbH & Co. KG, a company the user had already applied to for the identical role eight days earlier under sibling id 67430917. tracker.py check on the queued name returned nothing; the duplicate only surfaced after reading the employer off the landing page and re-running check on the REAL name. Resolve the employer from the apply target's own page before the dedupe check, not from the aggregator card.

- (2026-09-25) Second aggregator-byline duplicate in two days, this time via a gohiring redirect: a LinkedIn card bylined 'collana GmbH' (linkedin_4469963190) resolved through t.gohiring.com to macits.jobs.personio.com/job/2677670 = MAC IT-Solutions GmbH, already Submitted 2026-09-01 for the identical position under THE SAME Personio job id. tracker.py check 'collana' returned 0 prior rows; check 'MAC IT' returned the row instantly. The generalisation: when the apply route is a redirector (gohiring, aplitrak, broadbean), the Personio/ATS tenant slug in the FINAL url is the employer key, and its numeric job id is a stronger dedupe key than the aggregator ref - grep the Reference Code column for that id before filling anything.

- (2026-09-25) A broken employer-side link can send BOTH LinkedIn and the employer's own board to the wrong job. MOBIS Parts Europe's board renders the card 'Computer Vision Intern - Machine Learning Operations (m/f/d)' with an overlaying <a> whose href is the unrelated 'SAP-Specialist-...-709210052' job, and LinkedIn's Apply href had scraped the same broken value - so li_apply_routes returned a completely different role and the board appeared not to list the intern job at all. Recovery that worked: fetch /sitemap.xml and match the slug, then read script ld+json on that page - its 'title' was 'Computer Vision Engineer Intern (m/f/d)' while the slug and H1 said only 'Computer Vision Engineer'. Rule: when an apply href resolves to a job whose title does not match the card, do not conclude the posting is dead - check the employer's sitemap and trust ld+json over the slug, the H1 and the card.

- (2026-09-26) An active interview can be invisible to tracker.py check, because interview invitations arrive by phone or inside the portal and nothing writes them to the tracker until the user says so. One employer read 'OK / 1 open row (Submitted three days earlier)' and a second application was packaged and filled before the user said an interview was already scheduled. Rule: when check shows an OPEN employer-facing row at the same company from the last ~2 weeks, ASK the user whether anything has moved on it before packaging a second role there - a fresh Submitted row is exactly the age at which an interview invitation lands. And record the interview the same turn they mention it (Status=In Progress + Outcome), which is what makes the company print CAP_REACHED for every later batch.

### General — Search and sources

- 2026-07-07 — Haiku search subagent found 3 candidates via Indeed but only skimmed snippets; 2 of 3 (Sal.A iT, INFODAS) turned out to have hard German C1/"sehr gut" requirements buried in the full job description, only visible after opening the listing. Rule: when delegating SEARCH to a subagent, still open and read the full posting text (not just title/snippet) before qualifying — the language-requirement filter needs the complete description, not the summary.

- 2026-07-13 — Haiku search subagent repeated the snippet mistake even with explicit "open the full posting" instructions: all 4 XING finds came from search-result cards (no URLs captured, one company name misread TRUSTWEQ→TRUSTEQ), and 2 of 3 had hidden C1 gates (Soley, TRUSTEQ). Rule: treat ALL subagent finds as unverified leads — main session must re-open every posting during EVALUATE and must not trust subagent refs/URLs/language claims; ask the subagent for its URLs before re-searching (it may not have any).

- 2026-07-14 — the user: batches skewed almost entirely to Werkstudent/Praktikum; Master thesis roles were neglected. Rule: every SEARCH batch runs a dedicated thesis pass (Masterarbeit/Abschlussarbeit/Thesis terms) and targets ≥3 thesis roles per 10 found (see search.md § Keywords).

- 2026-08-23/24 — **studyflix hops were stale 3 times out of 5 in one batch** (Fraunhofer IEE Kassel → jobs.fraunhofer.de 404 and gone from their own board; Göhring → jobs.guehring.de/Vacancies/751 403 and absent from the live board; CENIT and SDZeCOM and Baumann resolved fine). Both dead ones were confirmed dead by searching the employer's own board, which is the cheap check. **A XING thesis card is not evidence the requisition is still open — resolve the employer URL and confirm on the employer board before packaging.** Also caught a XING posting whose start date read "Beginn im 1. Halbjahr 2023" (Basler) — read the start date, not just the posting's freshness badge.

- 2026-08-25 (batch: 10 submitted) — **The XING/StepStone THESIS pool is not "drained", it is fully APPLIED-TO.** A StepStone bare-slug sweep of 4 thesis slugs returned 237 cards -> 20 thesis-titled -> and **every single language-clean one was already in the tracker**, most submitted within the previous 48 h (GECKO, Liebherr-Aerospace, Speed4Trade, Endress+Hauser, Hirschmann x2, FITOK, Putzmeister, elobau, Rosenxt, Baumann, TSO-DATA). CROWN was a *repost* of a role that had already **rejected** him. **Every one of these returned `verdict: OK`.** Fresh thesis roles came only from XING (ABB, Syntegon, CLAAS, Hoerbiger, HMD, Draegerwerk). Rule unchanged but re-proven: the verdict line is worthless on its own — diff the ref AND the position, every time.

- (2026-08-30) **The clean-language pool really can run dry in one day.** This batch screened ~65 postings across arbeitnow,
  XING (thesis + Werkstudent + quick-apply) and StepStone (7 slug sweeps) and **~80% died on the German line** —
  far above the 60-75% baseline. Worse, the *fresh-find* rate was the real bottleneck: arbeitnow was already
  fully mined by the morning batch (Bettermile, Technica, Edri, UVC all submitted hours earlier), and XING's
  thesis page 1 was 20/20 already-processed rows. **When two sources come back fully mined, that is the signal
  to stop searching and drain the NeedsUser backlog instead** — this batch spent roughly half its budget on
  search for 8 conversions.

- (2026-08-30) **The German gate hit ~85% today, well above the 60-75% baseline** - and every clean role found was already applied to.
  Screened ~50 fresh postings across arbeitnow, XING (thesis x3 pages, Werkstudent, Data, quick-apply) and StepStone
  (10 slug sweeps, am=INTERNAL and bare): the *fresh-find* rate, not the search, is the bottleneck. LinkedIn EasyApply
  for Germany returned the same 7 irrelevant rows for every keyword - that pool is dead for student/AI roles.

- (2026-08-31) **Employer boards outlive dead aggregator ids, but the role can be renamed.** B. Braun's XING req 156908408 is
  "not available" on jobs.bbraun.com while req 13167 *Werkstudent AI & Robotics Development (VLA & Automation)* is
  the live equivalent; eigenblue's "Embedded Software Engineering" listing is now folded into
  "Electronics & Mechatronics Engineering". Search the tenant board by keyword before writing a find off.

- (2026-09-01) **Two employer boards defeated their own search this batch** (FZI umantis: search box and `?page=`
  both no-ops, only the first 10 of 90 vacancies reachable; Dr. Willmar Schwabe: page-2 control does
  nothing). Navigate by direct vacancy id where the pattern is guessable, and cap the attempt otherwise.

- (2026-09-07) **"Must have a named contact" is a source decision, not a filter.** Filtering postings after the fact
  throws most of a search away. Fraunhofer prints an Ansprechpartner on every posting; StepStone and
  Workday almost never do. For contact-required batches, go straight to research institutes and
  Mittelstand career pages — all 3 finds came from one `jobs.fraunhofer.de` search.

- (2026-09-07) **A phone-only contact is not a dead end.** IWU printed a phone and no address; the supervisor's real
  address was published on the project's own page (kognitive-produktion.de). Look for the person's
  project page before guessing `firstname.lastname@`. Never guess an address for outreach.

- (2026-09-07) **A generic `recruiting@` address is not the hiring manager.** For IKS the posting listed only the
  institute mailbox, so the note goes to the named researcher on LinkedIn instead of dying in a queue.

- (2026-09-08) **A portal's keyword search may not index the title.** Searching Dräger for "Feuerwehr" returned zero
  results while "Feuerwehrverwaltung" and "Data-Analytics" both found the req. Try a distinctive
  compound noun before concluding a posting is gone.

- (2026-09-10) **A second thesis batch on the same day has to change SOURCE, not keywords.** After the morning batch,
  14 more StepStone slugs and 9 more XING keywords produced 4 usable finds between them - every strong
  card was already a tracker row. What actually filled this batch: the **SmartRecruiters public API**,
  the **TUM Schwarzes Brett**, and **Indeed as a discovery-only source**.

- (2026-09-10) **`portal.mytum.de/schwarzesbrett/hiwi_stellen/` lists industry-adjacent research theses that no job
  board carries** (both Helmholtz Munich labs came from there). Each posting names a supervisor and asks
  for an email application - the cheapest channel in the file.

- (2026-09-11) **The thesis pool is dry; internships refilled it from ATS public APIs, not job boards.** Ashby
  (`api.ashbyhq.com/posting-api/job-board/<org>`), Greenhouse and Lever boards of Munich/Berlin startups
  plus a LinkedIn guest-API sweep (`/jobs-guest/jobs/api/seeMoreJobPostings/search?...&f_JT=I&f_TPR=r604800`,
  429s after ~15 calls - pace it) produced most of the batch. StepStone/XING internship cards were ~80%
  already-applied or capped.

- (2026-09-12) **Qualify on the APPLY HOST, not on the job title.** Batch 1 (10/10 submitted) came from arbeitnow, whose
  employers are SMEs on Personio / JOIN / Ashby - guest forms that take 2-4 calls each. Batch 2 came from the
  LinkedIn guest API, which surfaces big corporates: of 9 qualified roles, 3 were account walls (Fraunhofer x2,
  Amazon), 1 blocked at the final submit (Rohde & Schwarz) and 4 needed portal spelunking that never reached a
  form. **Before qualifying a role, resolve its apply host and prefer known guest-friendly ATSs**; park
  corporate portals (SuccessFactors / Workday / passport logins) in a separate, clearly-labelled queue.

- (2026-09-14) **Group portals hide subsidiaries' jobs.** KOCH Pac-Systeme's site has no job list at all - the role lives on the
  parent's portal (career.uhlmann.de). When an employer site is empty, check the group ("Teil der ... Group").

### General — Evaluate: language gate and fit

- 2026-07-01 — Search: ~½ of otherwise-perfect German AI Werkstudent roles die on explicit German C1 / "sehr gut" / "fließend" requirements. Check the language line FIRST before reading the rest of a German posting.

- 2026-08-22 — **Language gate killed 6 of the first 10 evaluated quick-apply roles** (AKDB C1, DIN "sehr gute", ESB "sehr gute", ElringKlinger "sehr gute", Waldemar Link C1, Mayfair "sehr gute"). The AI-titled Werkstudent postings on StepStone are the most German-gated segment there is; the clean-language survivors were the QA/BI/generic-IT ones. Budget for that ratio when picking a batch from StepStone AI slugs.

- 2026-08-24 — **Klangio: a fit gap worth surfacing rather than papering over.** The posting's first requirement is "Du spielst mindestens ein Musikinstrument"; the resume has no music background and no librosa/music21/MIR experience. The draft claims neither and says so explicitly, and the gap was flagged to the user to fill in himself if true. **Preferable to both silently skipping a good ML role and silently inventing a qualification.**

- 2026-08-25 — **Language gates killed ~75% of candidates this batch, worse than the recorded 60%.** Wave-by-wave: 8 of 9 Werkstudent finds rejected, then 14 of 18, then 3 of 6. Rejected phrasings: "Sichere Deutsch-", "Verhandlungssichere", "Exzellente", "Fließende(s)", "Deutsch ab B2", "C1/C2", "Fluent in German", "German (fluent or native)". **Accepted (and all of them submitted fine): "Gute Deutsch- und Englischkenntnisse" (no level), "Gute Deutsch- ODER Englischkenntnisse", "English C1 required; German is a plus", "Good communication skills in English/German", "Deutsch A2"/"Deutsch B1" stated explicitly.** Two Otto roles literally asked for A2 and B1 — worth searching for postings that name a LOW German level rather than filtering only for English-only ones.

- 2026-08-25 — **Two fit-based skips worth repeating rather than papering over.** Hoerbiger's "Abschlussarbeit (BA)" body says "Thema der **Bachelorarbeit**" — a Master's student who already holds a B.Tech cannot write it (skipped, not applied). ITONICS' "Working Student - IT" is helpdesk/laptop-setup work, not AI or software engineering (skipped despite a clean English-language requirement). TYTAN was skipped as an **unsolicited** posting in autonomous air-defence, where DE employers routinely impose citizenship/clearance limits on non-EU applicants. **A clean language line is not a reason to apply to a role that does not fit.**

- (2026-08-29) **The employer's own posting text beats every aggregator badge.** 11 of ~30 candidates this batch died
  on a German C1/B2/"sehr gute" line that the StepStone card did not show, including four StepStone rated
  "Passt hervorragend". Screen the language line for the whole shortlist in ONE browser pass before
  writing any cover letter — it is the cheapest filter in the pipeline.

- (2026-08-29) **Conversely, search actively for postings that NAME a low German level.** Otto's cards asked for
  "Deutsch A2" and "Deutsch B1" explicitly, and UVC Partners wrote "German is helpful but not required".
  These exist and are the highest-yield segment; treat an explicit A2/B1 line as a strong positive signal.

- (2026-08-29) **Check eligibility clauses, not just the language line.** atvari's internship required *no completed
  university degree* (the user holds a B.Tech) and was unpaid; KNIME required enrollment at a Berlin
  university. Neither is fixable by willingness to relocate — read the eligibility block before packaging.

- (2026-08-29) **A dead posting can outlive its aggregator listing.** TUI Cruises ("Diese Stelle wurde leider bereits
  besetzt") and OKAPI:Orbits (Personio job 404) were both still live on StepStone with future deadlines.
  Follow the employer link before investing in a cover letter.

- (2026-08-29) **Aggregator job ids die faster than the roles do.** In one round: both Sereact roles 404'd on Ashby,
  OKAPI's Personio job 404'd, TUI Cruises was "bereits besetzt", and DATRON/MULTIVAC needed the employer
  site. In every case the employer's own board still had the role or a near-identical replacement. **List
  the tenant board before writing a find off** — Sereact's "Robotics ML and Data Intern" came back as
  "Internship Teleoperation & Data Labeling" with the same scope.

- (2026-08-29) **The C1 gate can be a screening question rather than a posting line.** Intermate's JOIN wizard asked
  "Sprichst du fliessend Deutsch - mindestens auf C1 Level?" with nothing in the posting to warn of it.
  Answer truthfully (Nein) and let the employer decide, but expect it: budget for the possibility that a
  clean-looking posting turns out to be gated three steps into the wizard.

- (2026-08-30) **Screen the FULL posting before writing a cover letter, not just the language line.** Kenbun IT looked ideal
  (Data Science & Deep-Learning, "Deutsch ODER Englisch mind. B2") but the actual role is French linguistic QC of
  ASR data and requires *Französisch auf nahezu muttersprachlichem Niveau*. The disqualifier was in the body, three
  paragraphs below the language line. Same class as the atvari/KNIME eligibility clauses.

- (2026-08-30) **Screen the language line with a PROXIMITY regex, not a token blacklist.** A flat "sehr gute|C1|fließend" match threw
  away XITASO ("English at least C1 level. Knowledge of German is desirable but not required") - the single best find of
  the batch. Require the bad token to sit within ~60 characters of Deutsch/German. Re-running that filter over the
  rejects surfaced two strong roles the crude pass had binned.

- (2026-08-31) **The language proximity screen must also match "Kenntnisse der deutschen Sprache".** iMAR Navigation opens with
  "Die ausgeschriebene Stelle erfordert sehr gute Kenntnisse der deutschen Sprache ... (Level C1)" and the
  `Deutschkenntnis|Deutsch-` token list missed it entirely. Add `deutschen? Sprache` to the pattern.

- (2026-08-31) **Screen the language line with the employer's own posting, and widen the pattern again.** Two misses this
  batch: `very good command of German` (iocto — English-language postings phrase the gate without a CEFR
  level) and the fact that a StepStone/XING card can be clean while the full posting is C1 (AKDB: *"verhandlungs-
  sichere Deutschkenntnisse mindestens auf C1-Niveau"* appeared only in the body). Add `very good command`,
  `good command`, `excellent` and bare `sicher(es)` to the proximity pattern.

- (2026-08-31) **The gate rate held at ~80%** — 25 postings screened in detail, 20 died on German. The survivors were again
  mostly *unlevelled* phrasings ("kommunizierst sicher auf Deutsch", "gute Deutsch- und Englischkenntnisse")
  and one explicit OR (qmBase: *"sicher auf Deutsch ODER Englisch"*), which is the single best signal there is.

- (2026-08-31) **Aggregator ids died faster than ever:** qmBase's StepStone id 404'd within a day of being posted "NEU vor
  17 Stunden", innosystec's kenjo id renders an empty Angular shell, Harting's SuccessFactors req is "not
  available", and Wanzl's softgarden jobdb link resolves to an unrelated HENSOLDT job. In three of four the
  employer's own board still had the role (qmBase, Wanzl) or proved it dead (innosystec, Harting) — **list the
  tenant board before recording either Submitted or Skipped.**

- (2026-08-31) **Check the Praktikum TYPE, not just the language line.** Würth Elektronik eiSos looked clean and well-matched
  and is a **Pflichtpraktikum**; resume.md records the user as *freiwilliges Praktikum*. Same class of eligibility
  clause as atvari/KNIME — read it before writing a cover letter. Mi-Jack and deerstreet were binned on the
  same line this batch.

- (2026-09-01) **The language proximity screen must exclude `Deutschland`.** `deutsch\w*` matches *Deutschland* /
  *deutschlandweit*, so any "sicher"/"sehr gut" within 60 chars of a company boilerplate line like
  "…größter Anbieter in Deutschland" fires a false gate. Use `deutsch(?!land)\w*`.

- (2026-09-01) **Skip on FIT, not only on language — three roles this batch.** OTARIS (*studienbegleitendes
  Pflichtpraktikum*), NETHINKS (Pflichtpraktikum **and** a *Bachelorthesis*, which a Master's student holding a
  B.Tech cannot write), Rosenberger (Maschinenbau/Physik + Werkstoffkunde + FEM), YOGI TEA (ERP work dominated
  by writing German Schulungsunterlagen and Anwenderhandbücher — the wrong job at B1) and Inverto (IT service
  desk = end-user support). All five had clean or absent language lines and would have converted; the
  eligibility/fit block was in the body. Read it before writing the cover letter.

- (2026-09-01) **The drained-day wider net has a floor.** Casting wider to German-gated roles (the user's standing preference)
  paid off where the gate was *unlevelled* — Asklepios ("sehr gute Deutschkenntnisse", no CEFR, no language
  question on the form) submitted first try. It is NOT worth it where the posting **names C1** *and* the only
  channel is email (rhenag: "C1-Niveau" + mailto only; AKDB, already twice-skipped with "do not re-test").
  Rule: wider net = unlevelled gates and form-based channels; a named C1 on an email-only route stays a skip.

- (2026-09-01) **Re-read WHY a role was skipped, especially "sehr gute Deutschkenntnisse".** Three of today's ten came from
  rows skipped weeks ago on that exact line: Pan Dacom, BearingPoint and citema. The phrasing that matters is
  **"runden dein Profil ab"** (nice-to-have) versus a named CEFR level. Under the user's wider-net preference the
  first is an apply, the second is a skip — and Drees & Sommer's "mindestens B2, idealerweise C1" was correctly
  skipped on the same pass.

- (2026-09-01) **The wider net has a hard floor and it was hit five times today**: named C1/C2/B2 lines killed
  AWS-Institut (C1), nextAudit (C1+ "muttersprachlich"), Commoda (C2), Lucid Labs (C1), bridgefield (B2)
  and SPiNE (B2) — all otherwise good, several of them Easy-apply. Unlevelled phrasings
  ("sehr gute Deutschkenntnisse", "…runden dein Profil ab", "Deutsch UND/ODER Englisch") stay in scope.

- (2026-09-01) **Skip on fit even when the route is easy.** KIRCHHOFF's AI Competence Center role had a working
  TalentLink guest form but is network coordination, workshop documentation and German management
  reporting — the YOGI TEA class. An easy channel is not a reason to apply.

- (2026-09-02) **The thesis pool's language-gate rate is far below the Werkstudent pool's** - 25 clean of 61 screened (~59%
  gated) versus the 80-85% seen on recent Werkstudent batches, because thesis postings frequently name no
  language level at all. That is a reason to keep the thesis quota high, not just to satisfy the search rule.

- (2026-09-02) **Skip on eligibility even when the channel is perfect.** Magna/Engineering Center Steyr's Windows->Linux
  porting thesis has a working Workday **guest** path ("Apply Manually", zero password inputs) but requires
  "Gute Kenntnisse in C++ und C#" (no C# in resume.md) and is formally supervised by the **JKU Linz** institute,
  which a <your university> student cannot satisfy. An easy channel is not a reason to apply.

- (2026-09-03) **Do not pad a batch with a bad-fit tenth.** The last four reachable roles (NEW Netz, GB Foods, ATLAS,
  Drees & Sommer Tender Management) all had clean or unlevelled language and working channels, and all
  four were Excel/PowerPoint/documentation roles or required a Bauingenieurwesen degree. Stopping at 9
  was the correct call; the YOGI TEA/KIRCHHOFF rule outranks the batch count.

- (2026-09-04) **Gate rate was ~55% on the first XING batch and ~62% on the third** - well below the 80-85% of
  late August, because this batch mixed thesis and plain Werkstudent-Softwareentwicklung terms
  rather than AI-titled ones. The duplicate rate was the real filter: 14 clean finds in batch 1
  produced only 4 fresh rows (~70% duplicates), exactly as the 2026-09-01 note predicts.

- (2026-09-04) **Employer-board retargeting failed for the first time in a while.** Schaeffler, Hannover Rueck and
  Allianz were all dead reqs ("bereits besetzt" / "position has been filled" / "ist besetzt"), and only
  Schaeffler had a live equivalent - whose **detail template returns `document.body.innerText.length === 0`
  under three URL forms while `/search/` renders fine** (the adesso RMK failure mode on a different tenant).
  Budget one retarget attempt, then record Blocked with the search-page route for next time.

- (2026-09-05) **A dead employer req often has a live TWIN under a different location.** EDAG's <your city> req 58836 404s
  and the board's search box is a no-op (only 8 promoted jobs render under every query, incl.
  `tx_kesearch_pi1[sword]`). The identical Wolfsburg req 58581 is live and its posting header reads
  "Wolfsburg / <your city>" - i.e. the same job. **Capture the XING employer link from a SIBLING card when
  the primary req is dead**, and read the retargeted posting's own location line before assuming a move.

- (2026-09-06) **The employer-page language re-screen killed the best-looking Werkstudent again.** flaschenpost's XING
  card (157306293) had no language line at all; the employer posting requires "Du beherrschst die deutsche
  Sprache **sicher** in Wort und Schrift" and the job is running the BI-Community-Call, writing the internal
  newsletter and building Schulungsunterlagen - genuinely German-dependent, not boilerplate. Screening the
  shortlist's employer bodies before packaging remains the cheapest filter in the pipeline.

- (2026-09-06) **"Pflichtpraktikum" is a standing hard skip** (no mandatory internship in the <your city> M.Eng.), and it is
  worth screening for in the same pass as the language gate - it killed montamo Berlin, Bosch Stuttgart,
  MB Boeblingen, MB Sindelfingen, ARRK and ZEISS's CV internship this batch.

- (2026-09-06) **A dead aggregator req can have a live twin worth MORE than the original.** trivago's XING req
  "Working Student - Data & Insights" is absent from careers.trivago.com entirely; the live
  "Student Data Scientist - Content" (Analytics/Student/Duesseldorf, English, Python/Pandas/SQL,
  Immatrikulationsbescheinigung required) is a better fit and converted the same hour. Budget one
  employer-board twin hunt per dead req - but check the twin's own requirements block before retargeting
  (ZEISS's "Working Student/Master Thesis Transport Systems" twin wanted Mechanical Engineering + CAD/FEM
  and was correctly skipped on fit, not applied to for the sake of a number).

- (2026-09-09) **On a drained day the wider net does convert.** The clean (no German gate) pool yielded 6 roles and
  half of them were dead or duplicates. Of the 5 German-gated roles applied to under the user's
  wider-net rule, 4 submitted cleanly; where the form asked a language question at all it was
  answered truthfully (`Grundkenntnisse` / B1) and none of them blocked submit.

- (2026-09-10) **Thesis-role language gates cluster at the top of the funnel.** Of 18 postings evaluated in this batch,
  6 died on German (C1: T.CON, mindsquare, FRAISA; "sehr gute"/B2: dSPACE, OKE (applied anyway under the
  wider-net rule), Corning) and 4 on a study-programme mismatch (Kautex, Krones, Bauerfeind, Diehl).

- (2026-09-11) **Read the eligibility line before packaging.** Buerkert's internship says "ausschliesslich
  Bachelorstudierende"; Lufthansa Technik and Studyflix require a written Pflichtpraktikum proof - all
  three are hard no's for a Master student on a freiwilliges Praktikum.

- (2026-09-14) **Postings die between LinkedIn and the employer**: StrategyBridgeAI (JOIN board empty), WITRON (404), Cremanski
  (Personio id gone), Kia Connect (needs unrestricted work permit - eligibility). Resolve and read the employer page
  before packaging.

### General — Apply: forms and answers

- Never invent experience, skills, or facts not in `application/resume.md`.

- 2026-08-24 — **Aggregator/apply-link traps, three in one batch.** (1) Mubea's Lumesse apply URL 500s on direct navigation and only works when the in-page "APPLY ONLINE" anchor is clicked (referer-gated, gohiring class). (2) Mubea's Lumesse upload widget clears `input.files` after a successful upload — **verify by filename in `document.body.innerText`**, never by the input. (3) KfW's BeeSite "Direct start without log in" is an **accordion toggle** (`data-toggle="collapse"`), not the apply button — clicking it does nothing visible; the real control is the "Apply now" anchor *inside* `#panel-muz-*`, which leads to `ac=applicationform_privacy`. That guest path then ends in an arithmetic **security query** (`math_captcha_response`) = bot-detection = agent stop.

- (2026-08-29) **Do not guess personal facts a form asks for, even trivial-looking ones.** Sereact required "Do you have
  a driver's license valid for the EU?" and JOIN asked for pronouns. The licence was worth one question to
  the user (answer: No); the pronouns field was correctly left as "Keine Antwort". Neither belongs in a guess.

- (2026-08-29) **Two consent classes to flag, not silently accept:** an AI-conducted first interview (Intermate's "Pepe
  Allbacher") and a background check (TYTAN, defence). Both were answered Yes because declining ends the
  application the user asked for, but both change what he is signing up for — always name them in the row
  notes and in chat.

- (2026-08-29) **Never bypass a TLS certificate warning or a human-verification challenge.** `de.multivac.com` served an
  expired cert and multivac.com's vacancy board sits behind a "confirm you are human" button; both are hard
  stops -> prepare the package and hand off, exactly like a password wall.

- (2026-08-31) **A missing personal fact is worth one question, not a guess.** MBDA required City of Birth; resume.md only
  had "born in Gujarat, India" (a state). the user's own documents show Surat as a home address, which would
  have been a plausible and wrong answer on a defence form. Asking cost one turn: the answer is **Amreli**,
  now recorded in resume.md.

- (2026-09-01) **atsiQuestions `freifeld*` fields are matchable ONLY BY LABEL.** `freifeld1_txt` was
  "Aktuelle Taetigkeit*" on one form and "Kuendigungsfristen*" on another; `freifeld2_txt` was
  "Hausnummer*". Any name-based fill map silently skips them and the section never clears. Match on
  the visible label text, fall back to the name.

- (2026-09-01) **Enumerate required fields by scanning for lines ending in `*`**, not by reading `.required`.
  On BWT the DOM said `required:false` for all 13 required questions, and a country `<select>`
  flooded the visible-label extraction with 200 country names, hiding six required questions
  (Englisch*, Deutsch*, MS-Office*, ...) below the fold of the first dump.

- (2026-09-01) **the user's earliest start date is now "the 15th of the current month"** (confirmed 2026-09-01, supersedes the
  fixed 1 September 2026 answer): re-derive it each month rather than copying a date forward. `resume.md` is
  updated.

- (2026-09-01) **Two consent-class answers to keep naming in chat:** citema asks *"Wären Themen im Verteidigungsumfeld in
  Ordnung für Dich?"* (answered Ja) and BearingPoint has a 0-100 *Reisebereitschaft* slider with no resume
  answer (set to 100 to match "relocate: YES always"). Neither is a fact in `resume.md`; both are flagged in
  their rows.

- (2026-09-03) **A signed-in ORC/Workday PROFILE carries a stale address that goes out silently.** Dürr's step 1 was
  prefilled with Gymnasiumstr. 11 / <postcode2> and a stale Anschreiben from a job rejected in July; ZEISS's
  Workday needed the address typed fresh. Read back every prefilled field, and on a re-application to a
  tenant, check the attached documents as well as the text fields.

- (2026-09-04) **Salary fields keep being numeric-only and the error names the field, not the constraint.** TKMS
  rejected "15600 EUR brutto p.a. (Werkstudent, 20 Std./Woche)" with only
  "Bitte nenne uns Dein Wunscheinkommen" and accepted a bare `15600`. Try the bare number FIRST.

- (2026-09-08) **A logged-in ATS prefills from the LAST application, so prefill is stale by default, not fresh.**
  Dräger pre-populated entry dates of 30.08.2026/31.08.2026 (already in the past) and had the *country*
  ("Indien") sitting in the `Geburtsort` city field. Re-read every prefilled field on every job; the
  same profile then carried my corrections forward to jobs 2 and 3 for free.

- (2026-09-08) **Ticking an extra option can make a hidden field required.** Adding "Praktikum" alongside
  "Abschlussarbeit" revealed `Dauer des vorgeschriebenen Pflichtpraktikums`, which showed no asterisk
  until validation failed. the user's programme prescribes none, and the field is free text, so the
  truthful answer is a sentence ("Kein Pflichtpraktikum in der Studienordnung vorgeschrieben") — not a
  made-up number and not a reason to abandon the option.

- (2026-09-09) **A SuccessFactors profile CV is stale by default — replace it, and check the address.** MTU's
  profile served a CV from 14.07.2026 and an address the user left long ago (Gymnasiumstr. 11 / <postcode2>);
  Workday's Airbus profile had the *same* stale address. Both had to be corrected by hand. Assume
  every returning-candidate profile is stale on both counts.

- (2026-09-10) **Ask for a fact rather than inferring it.** adjoe required "how many full or half days have you
  already worked in this calendar year" - a declaration about the user's student permit that is not in
  `resume.md`. Asking mid-batch cost one turn and he answered 40; guessing 0 would have put a false
  statement on a visa-related question.

- (2026-09-12) Talent-pool consents are NOT application requirements: Hypatos (Nein) and Emidat (24-month box left
  unchecked) both submitted fine. Decline them unless the user says otherwise.

### General — Browser tooling

*Submit-button blockers (recurring family)*

2026-07-23 - Three forms in one batch had a working submit button that simply could not be clicked. Detector: measure the button, then `document.elementFromPoint(cx,cy)` - if it returns anything other than the button, something is on top.

- **Consent overlay over the button**: Cogitaris `.cogitaris-consent-overlay` ('Alle ablehnen'), itsax `.cookies-eu` ('Nur funktionale Cookies'). Decline, then RE-MEASURE (the layout shifts).

- **Session-expiry modal**: perview shows 'Warnung vor Ablauf der Sitzung' as a `.modal.fade.show` over the form - click 'Sitzung erneuern', it disappears and the form state survives.

- **Styled-disabled buttons**: itsax keeps the submit at `opacity-50` with `disabled===false` until fields that only appear after an earlier answer are filled (choosing 'Ich wohne in Deutschland' reveals required Wohnland/Strasse/PLZ/Ort). No validation message is shown - diff the form's fields for empty values instead.

*Upload verification*

2026-07-23 - Two distinct failure modes beyond the documented 'AJAX inputs clear themselves':

- **Cogitaris**: the widget consumes the File into JS state and resets `input.files` to 0, so a retry looks necessary but is not - three retries produced FOUR attachment rows for one file. Count occurrences of the filename in `document.body.innerText` and delete extras (each row has its own remove button).

- **perview**: hidden file inputs do NOT correspond to the visible document rows in order (`input[2]`=Schulzeugnisse, `input[3]`=Leistungsuebersicht Studium, `input[1]` and `input[6]` both land in the generic 'Weitere Dateien hochladen' slot; the Motivationsschreiben/Lebenslauf rows appear to create their inputs lazily). Upload one file, read which row the filename appears in, and fall back to the bundle slot with clearly named files. Removing a file opens a 'Sind Sie sicher?' modal - confirm with 'Dokument loeschen'.

*HTML `input[type=date]` (q23.de and friends)*

Neither the native value setter nor CDP `Input.insertText` lands a value. Coordinate-click the field, then dispatch **digit keystrokes in mm/dd/yyyy order** (`"08152026"` → `2026-08-15`). Typing German order (`15082026`) produced `2026-12-08`. Segments only commit after the last digit, so don't bail out when intermediate reads come back empty.

- 2026-07-02 — browser-harness js() heredocs mangle umlauts (ü → Ã¼) when typed literally into form values; use \uXXXX escapes in JS strings instead. German text READ from pages is fine.

- 2026-07-17 (batch resumed after Allow click) — CDP came back only after the user clicked Allow during a pending connection attempt (Chrome restart also wiped all parked tabs — never rely on parked form state across a CDP outage). Harness finished the queue: Edgeless + MESSRING Personio guest submits (Edgeless needed the required Urkunde* doc slot = Immatriculation, Agile-Robots pattern; JS native-setter fills left Personio submit disabled — fill_input keyboard-level fills enabled it). AL-KO d.vinci: form POSTs back with a TEXT CAPTCHA (input[name=captcha]) only revealed on submit — all values survive the bounce, so fill everything, then NeedsUser for the captcha+Absenden. d.vinci wants ONE merged PDF for 'Vollstaendige Bewerbungsunterlagen' (pypdf merge CV+Immatriculation+Transcript worked).

- 2026-07-17 (batch, CDP outage) — Chrome (M136+) now gates CDP behind an "Allow remote debugging?" popup that appears AT CONNECT TIME; ticking the chrome://inspect checkbox alone is not enough — the user must click Allow while a connection attempt is pending. Fallback used: claude-in-chrome extension (tabs/JS/clicks/typing all work) with ONE hard limit: file uploads are impossible (file_upload accepts only session-shared paths; page-JS injection is blocked by ATS CSP for localhost fetch AND iframe relay; OS-clipboard file paste does not reach file inputs). Batch strategy under this limit: (1) LinkedIn EasyApply works END-TO-END because the stored profile resume avoids any upload (Quistor submitted this way, incl. required cover-letter TEXTAREA + GDPR consent checkbox); (2) prefill guest forms and park each in its OWN tab (navigating a tab away wipes React form state — Edgeless fills were lost this way); (3) wall-class ATS (Workday/career5-SF) can still be classified NeedsUser. Also: gohiring redirect links 404 on direct navigation but work when click()ed in-page on the LinkedIn job page (referer-gated).

- 2026-07-19 — **Heredoc encoding trap is worse than documented**: browser-harness reads the `browser-harness <<'PY'` script as **cp1252**, so ANY non-ASCII typed in the heredoc is already mojibake *inside Python* (`"ö"` -> ords [195,182]) — this corrupts `fill_input` too, not just JS injection, and it is invisible until a summary page renders "KI-LÃ¶sungen". Verify with `[ord(c) for c in s]` and repair in-script with `s.encode('cp1252').decode('utf-8')` BEFORE using the text. Reliable German-text recipe: fix the string, then inject via `String.fromCharCode(...)` from a Python-generated code array (pure-ASCII payload) + React native setter + `input` event.

- 2026-07-19 — JS regex literals with backslashes broke `js()` twice again in one session (`/\s+/g`, `/
/g` -> "Invalid regular expression: missing /"). They are ALWAYS worth avoiding: use `indexOf`/`includes`/`split` in JS and do the regex work in Python on the returned text. Also: matching German text inside `js()` fails for the same encoding reason — match an ASCII substring (`'berpr'` instead of `'überprüfe'`) when hunting validation errors.

*Harness text encoding — umlauts (2026-08-14, applies to EVERY portal)*

`fill_input()` AND plain JS string literals passed through `js()` both **mangle non-ASCII**: the UTF-8 bytes get re-read as cp1252, so `für` is submitted as `fÃ¼r`. Verified live (a Sunpeak StepStone answer went out mojibake before this was caught). **`String.fromCharCode(n)` is the only reliable channel.** For any field containing German text, build the value as an ASCII-run + `String.fromCharCode()` concatenation and set it with the native setter + `input`/`change`/`blur`. Helper: `jstr()` / `set_value()` in `scripts/jstr.py`. **Always read the field's `.value` back and eyeball the umlauts before submitting.**

- 2026-08-19 — **The browser-harness CDP daemon died mid-batch** ("DevToolsActivePort not found", `--doctor`: chrome running, daemon dead, 0 connections) and could not be revived from the agent side; it needs the user to re-tick "Allow remote debugging for this browser instance" at `chrome://inspect/#remote-debugging` and click Allow. **What saved the batch: everything that does not need a browser was done anyway** — packages, job_posting.txt, CVs, supporting documents and five tailored German Anschreiben (PDF/A, 254–268 words) for all six remaining jobs. Rule: when the browser dies mid-batch, do not idle — pre-build every package and cover letter so the resumed session is pure form-filling.

- 2026-08-22 — **Two submits that silently no-op'd, two different causes.** NOWEDA (talentsconnect): a cookie modal was covering the page and swallowed two coordinate clicks on "Bewerben" with no error — decline it first, and even then only a JS `.click()` on `#form-application-send-submit` fired. Greenhouse embeds: the submit button sat at y≈950 in a 551px viewport, so the coordinate click missed entirely; `scrollIntoView` did not help because the scroll container is not the window — a JS `.click()` worked. **Rule: when a submit produces no error, no URL change and no confirmation, suspect an overlay or an out-of-viewport rect before assuming the form is broken, and try a JS `.click()` as the second method.**

- 2026-08-22 (batch 2 of the day, 10 targeted) — **6 submitted, and the batch's real lesson is a wedged input pipeline.** DaphOS.ai, snapADDY, Testo (softgarden), BLIKS IO, Otto ×2 all Gmail-confirmed. From roughly the WISAG attempt onward, **Chrome's CDP Input domain was dead browser-wide**: `cdp("Input.dispatchMouseEvent", ...)` timed out while `Runtime.evaluate` kept working, so every `click_at_xy`, `type_text` and `press_key` silently did nothing (a coordinate click on a text input left `document.activeElement === BODY`). Root cause was a leftover **native file-picker window** from an earlier batch (visible in `EnumWindows` as `SanaHR_Werkstudent_Data_Engineer`) sitting on the desktop. **Rule: when a click "lands" (`elementFromPoint` returns the target) but nothing happens, test `cdp("Input.dispatchMouseEvent", type="mouseMoved", ...)` once — a TimeoutError means the pipeline is wedged, not that the form is broken. Then close stray dialog windows and (last resort) restart the daemon; note the restart re-triggers Chrome's "Allow remote debugging?" popup, which only the user can click.** Everything that still succeeded that evening went through JS-only paths.

- 2026-08-22 — **German text through `js()`: base64 + `TextDecoder` is the reliable path.** `fill_input` no-ops on React/Ashby/Otto fields, `\uXXXX` gets pre-decoded, and raw umlauts in a heredoc get mangled. Working recipe: base64-encode the UTF-8 string in Python, then in JS `new TextDecoder().decode(Uint8Array.from(atob(B64), c=>c.charCodeAt(0)))` and write it with the native value-setter. Verified on Otto (2 × ~100-word Motivationsfragen) with umlauts intact.

- 2026-08-23/24 — **CORRECTION to the 2026-08-22 "wedged Input pipeline" diagnosis: the real cause is a BACKGROUND TAB, not a stray native dialog.** Symptoms are identical and misleading: `Input.dispatchMouseEvent` and `Page.captureScreenshot` both time out while `Runtime.evaluate` and `DOM.setFileInputFiles` keep working perfectly. I burned this batch's second half on the recorded remedy — hunted `#32770` dialog windows (none), closed 61 tabs (no effect), and finally had the user re-click Chrome's "Allow remote debugging?" after a `--reload`, **which also did not fix it**. A fresh daemon with the same symptom is the tell that the problem is Chrome-side. **Detector: `js("document.hidden")` — if it returns `true`, Chrome is refusing input and frame capture because the tab is not visible. Fix: `cdp("Page.bringToFront")`, one call, instant.** This happens whenever `new_tab` is used repeatedly and the foreground tab drifts away from the one being scripted. **Check `document.hidden` BEFORE concluding anything is wedged, and never ask the user for an Allow click on this symptom again.** (Everything still completed JS-only in the meantime — `el.click()` for checkboxes/radios/submits, and the full `pointerover/pointerdown/mousedown/pointerup/mouseup/click` sequence with real `clientX/clientY` for React/Workday controls — so a hidden tab costs precision, not the batch.)

*"CDP Input is wedged" — check `document.hidden` FIRST (2026-08-24)*

`Input.dispatchMouseEvent` and `Page.captureScreenshot` time out, but `Runtime.evaluate` and `DOM.setFileInputFiles` work fine. This is almost always a **background tab**, not a broken pipeline: Chrome will not deliver synthesized input or capture frames for a non-visible target.

```python
js("document.hidden")          # True  -> that's the whole problem
cdp("Page.bringToFront")       # fixes both, instantly
```

Happens whenever repeated `new_tab` calls leave the foreground tab pointing somewhere other than the tab being scripted. **Do not** hunt for stray `#32770` file-picker windows, mass-close tabs, or restart the daemon — a `--reload` plus a fresh "Allow remote debugging?" click does NOT fix it (verified 2026-08-24), and a fresh daemon showing the same symptom is proof the cause is Chrome-side. Only after `document.hidden` is `false` and input still fails should you consider a real dialog block.

Meanwhile, JS-only paths keep working: `el.click()` for checkboxes/radios/submit buttons, and for React/Workday controls dispatch the full `pointerover/pointerdown/mousedown/pointerup/mouseup/click` sequence with real `clientX/clientY`.

- 2026-08-24 — **`document.hidden` is not always fixable, and it does not have to be.** The background-tab diagnosis from earlier held, but this time `Page.bringToFront`, `activate_tab`, `Target.activateTarget` and even restoring/focusing the Chrome window via `ShowWindow`+`SetForegroundWindow` all failed to un-hide the tab, so `Input.*` and `Page.captureScreenshot` stayed dead for the whole batch. **It cost nothing: all 6 submissions went through JS-only.** The working substitutes are `el.click()` for checkboxes/radios/submits, the full `pointerover/pointerdown/mousedown/pointerup/mouseup/click` sequence with real `clientX/clientY` for React and select2 widgets, and `DOM.setFileInputFiles` for every upload (which never needs visibility). **Rule: check `document.hidden`, try `bringToFront` once, then stop fighting it and work JS-only — do not restart the daemon and do not ask the user for an Allow click.**

- 2026-08-24 — **Chrome crash cleared the invisible-tab problem instantly.** After the restart `Page.bringToFront` worked on the first try and `Input.*` came back, having been dead for the whole previous batch through daemon restarts, `activateTarget` and a Win32 `ShowWindow`+`SetForegroundWindow`. So the state is real but not always recoverable in-place, and **a browser restart is the fix that actually works — not a daemon restart.** Still not worth chasing mid-batch: JS-only had already carried 6 submissions.

- 2026-08-24 — **The "CDP input pipeline wedge" has a concrete cause: TWO `browser_harness.daemon` processes.** Symptom is exactly as recorded before — `Runtime.evaluate` keeps working, every `Input.*` call times out browser-wide (all tabs), `scroll()` hangs, and `window.scrollTo` appears to do nothing. Diagnosis in one command: `Get-CimInstance Win32_Process | Where CommandLine -like "*browser_harness.daemon*"` — if it lists more than one PID, they are fighting over the CDP socket. Fix: `Stop-Process` **all** of them and let the next `browser-harness` call spawn a single fresh daemon (Chrome then re-asks for the Allow click). **Do not restart Chrome first** — that was the previously recorded fix and it is the expensive way to solve a daemon problem.

- 2026-08-24 — **`goto_url` hits the daemon's ACTIVE tab, not the tab you last opened with `new_tab`.** I destroyed the parked TSO-DATA form twice this way: `new_tab(tso)` then, one job later, `goto_url(next_job)` reused that same target. Rule: after `new_tab` for a parked form, note its `targetId` in the tracker row AND `switch_tab` to a different target before the next `goto_url`.

- 2026-08-25 — **The native value-setter CONCATENATES onto keyboard-typed text; it does not replace it.** Filling a field with the setter and then re-typing it with `Input.insertText` produced doubled values on Workday ("6 Monate…6 Monate…") and on Ashby ("<Your Name><Your Name>"). On Workday it survived to the **Review page**, which is the only place it was visible. **Fix: click, Ctrl+A, Delete, assert `.value.length === 0`, then insertText once.** And always diff the review/summary page against what you intended before the final submit.

- (2026-08-29) **Cookie banners: accept them (standing instruction, the user 2026-08-29).** Several employers hide the
  whole job board behind consent (DATRON: "Bitte akzeptieren Sie die Cookies, um die Stellenangebote
  anzuzeigen"). Click *ALLES AKZEPTIEREN* and carry on — this replaces the older "decline non-essential"
  default. The banner can re-appear over the form after the widget re-renders; accept it again.

- (2026-08-29) **A collapsed/overlapping embedded form is usually a VIEWPORT problem, not a broken widget.** DATRON's
  upload slots stacked on top of each other at 1366x551 and refused to bind files ("Bitte laden Sie das
  erforderliche Dokument (Lebenslauf) hoch" even with 3 files in the shared input). One
  `cdp("Emulation.setDeviceMetricsOverride", width=1500, height=1200)` + reload laid the three tiles out
  properly and each slot then took its file. **Try a taller viewport before declaring an ATS automation-proof.**

- (2026-08-29) **Hit-test the submit button before retrying a silent failure.** Two coordinate clicks on Graband's
  `Absenden` did nothing and left the form populated with no error;
  `document.elementFromPoint(centre of the button)` returned a **Borlabs cookie dialog**
  (`brlbs-dialog-positioner`) sitting invisibly on top. A JS `.click()` on the input submitted instantly.
  One `elementFromPoint` call diagnoses this faster than any number of re-clicks.

- (2026-08-30) **`goto_url` reuses the active tab, so "park the form for the user" fails silently.** The Dräger consent page was
  prepared and then destroyed by the next job's navigation. Either open handoffs with `new_tab`, or write the note
  so the row is refillable from the URL alone — assume the tab will not survive the batch.

- (2026-08-30) **`switch_tab` takes the `targetId` string, not a list index.** `switch_tab(i)` throws
  `Failed to deserialize params.targetId`. Use `switch_tab([t for t in list_tabs() if ...][0]['targetId'])`.

- (2026-08-30) **When screenshots time out but `js()` still works, the CHROME WINDOW is minimized, not the tab.**
  `document.hidden` reads True on *every* tab. `Page.bringToFront` alone does not fix it. What works:
  `w=cdp("Browser.getWindowForTarget", targetId=tid)` then `cdp("Browser.setWindowBounds", windowId=w['windowId'],
  bounds={"windowState":"minimized"})` followed by `{"windowState":"normal"}` — the minimize/restore cycle is what
  actually un-hides it; setting `normal` on an already-"normal" window is a no-op. This blocked the NXP autofill
  test and two confirmation screenshots.

- (2026-08-30) **German string literals inside `js()` break even in a `r"""..."""` heredoc.** `x.innerText.trim()==='Übermitteln'`
  arrived as `'Ãœbermitteln'` and the find returned undefined. Match an ASCII substring instead
  (`.indexOf('bermitteln')>-1`). This is the same rule as the existing regex-literal note — it applies to plain
  string comparisons too.

- (2026-08-30) **`document.hidden` going True mid-batch is recurring; the minimize/restore cycle does not always fix it.** What
  worked twice today: `switch_tab(targetId)` -> `Page.bringToFront` -> `Browser.setWindowBounds` with an explicit
  `{"windowState":"normal","left":0,"top":0,"width":1382,"height":744}`. Setting `normal` on a *maximized* window is the
  no-op; giving explicit bounds is what un-hides it.

- (2026-08-31) **`document.hidden` is now the FIRST thing to check on a disabled submit, not the fifth.** WISAG had been
  recorded `Blocked` on 2026-08-22 because "Bewerbung abschicken" never enabled. It was `document.hidden ===
  True` the whole time: every section read *Bereit*, no required field was empty, no error node existed. The
  minimize→restore `Browser.setWindowBounds` cycle enabled the button and the very next click submitted.
  **A recorded "Blocked / button never enables" verdict is a prime candidate for a stale-wedge retry** —
  this one cost a submit for nine days.

- (2026-08-31) **`document.hidden` re-wedged roughly every 2-3 harness calls on this flow.** One un-wedge at the start is
  not enough — check it immediately before every commit action (Save/Continue/Submit) and treat any silent
  no-op as the wedge until proven otherwise.

*Careers pages that hide their job list in an IFRAME (2026-09-01)*

`innerText` on the employer's careers page returns a few hundred chars and looks broken/empty, but
`document.querySelectorAll('iframe')` reveals the real board on another host:

- `aws-institut.de/karriere/jobs` → **`awsi.jobs.personio.de`** (Personio guest board)

- `renk.com/de/karriere/stellenangebote/stellenangebote-europa` → **`renk-group.softgarden.io`**

- `schwabe.de/karriere/stellenangebote` → `karriere.schwabe.de` (separate host, own pagination — broken)

Go to the embedded host directly; it is usually a converting channel (Personio/softgarden), and the
employer's own site adds nothing but a cookie wall.

- (2026-09-01) **Label-to-control mapping: the asterisk is usually NOT on the leaf node.** Match a label by
  `textContent` on the smallest element that contains the key and holds no control, then take the
  first following control via `compareDocumentPosition`. A leaf-only or `endsWith('*')` matcher
  returns nothing.

- (2026-09-01) **`ß` does not survive a bash heredoc into a Python regex, and the failure is SILENT.** The language screen's
  `fließend` alternative arrived mangled, so `Fließende Deutschkenntnisse` read as CLEAN — caught only because
  MURTFELDT's tracker row already recorded that exact gate. Write the pattern as **`flie\w*end`** (matches
  fließend/fliessend/Fließende) and keep every regex ASCII. Same root cause as the existing
  German-literals-in-`js()` rule; it applies to Python-side patterns too.

- (2026-09-01) **A `beforeunload` dialog wedges the ENTIRE daemon, not just the tab.** ARDEX's portal left one pending;
  every subsequent `goto_url`/`switch_tab`/`js` timed out, and `Page.handleJavaScriptDialog` answered
  "No dialog is showing". The recovery that worked was **`close_tab(<wedged targetId>)`** then `new_tab`.
  Also: `list_tabs()` targetIds are longer than they look — copy them whole, a truncated id throws
  "No target with given id found".

- (2026-09-01) **`document.hidden` was the single biggest cause of the Blocked backlog, not any ATS.** Four rows that had
  been written up as different, portal-specific defects were the same wedge: BWT ("Kontaktdetails never gets a
  badge", 2 batches), ARDEX ("steps are DIVs, nothing advances"), Deichmann and the first Thieme click all
  behaved normally after one minimize→restore `Browser.setWindowBounds` cycle. **Make the un-wedge the first
  action on every page load in a drain batch**, before reading state at all — it is cheaper than one wrong
  diagnosis, and every wrong diagnosis here cost a whole row for days.

- (2026-09-01) **The second-biggest cause was VIEWPORT.** ARDEX at 1366x551 renders its wizard navigation off-screen and
  looks like a dead page; `Emulation.setDeviceMetricsOverride(1500, 1300)` made all four steps appear. Pair the
  `document.hidden` check with a viewport override as one standard "page looks broken" remedy.

- (2026-09-01) **When a click does nothing and there is no validation error, drain the CDP exception log.** One
  `cdp("Runtime.enable")` + `drain_events()` around the click named the failing file, line and function
  instantly. That is far cheaper than the usual escalation ladder of JS click → coordinate click → hit-test →
  viewport → screenshot.

- (2026-09-01) **A job list that `innerText` cannot see is almost always an IFRAME.** aws-institut.de embeds
  `awsi.jobs.personio.de`; renk.com embeds `renk-group.softgarden.io`. Both looked like empty/broken pages
  under text extraction. **Check `document.querySelectorAll('iframe')` before declaring a careers page dead**,
  then go to that host directly — it is usually a Personio or softgarden tenant, i.e. a converting channel.

- (2026-09-01) **`press_key("a", modifiers=2)` does NOT send Ctrl+A — it types a literal "a"** and corrupts the field
  (`the user` → `the userathe user Maheshbhai`). To replace a value in a React/parser-filled input:
  coordinate-click it, then `el.focus(); el.setSelectionRange(0, el.value.length)`, then
  `cdp("Input.insertText", ...)`. That worked everywhere the native setter and `fill_input` did not.

- (2026-09-02) **`Input.insertText` concatenates; only Backspace reliably clears a React-controlled input.** Triple-click plus
  insertText appended ("<street>, ...Deuts<postcode> <your city>chland") on two different forms today. A loop of
  ~20 `Input.dispatchKeyEvent` Backspaces from the end of the field is what actually worked.

- (2026-09-03) **`js()` and raw `cdp()` can address DIFFERENT targets after a click opens a new tab.** On Mühlbauer's
  softgarden form `js("document.querySelectorAll('input[type=file]')")` listed `cv-file` while
  `cdp("DOM.querySelector", selector="#cv-file")` returned nodeId 0 and `Runtime.evaluate` returned null.
  `switch_tab` did not fix it. Root cause: **the element had `name="cv-file"` and an EMPTY id** — the
  `#cv-file` selector never matched, and `x.id||x.name` in the dump made it look like an id.
  Dump `JSON.stringify(x.id)` (quoted) rather than `x.id||x.name` before building a selector.

- (2026-09-04) **`Browser.setWindowBounds` does NOT change the page's `innerHeight` on this setup - use
  `Emulation.setDeviceMetricsOverride`.** The minimize->restore cycle un-wedges `document.hidden`
  correctly, but `innerWidth/innerHeight` stayed 1034x523 afterwards, so `scrollIntoView` reported a
  rect at y=1659 that was off-screen and `document.elementFromPoint` returned **null** - the click was
  swallowed with no error, no URL change and no validation message. This cost one failed submit each on
  dSPACE and Lauterbach before diagnosis. **Rule: hit-test EVERY submit (elementFromPoint at the button's
  centre) and treat `hit: null` as "the button is outside the real viewport", not as a broken form.**
  `cdp("Emulation.setDeviceMetricsOverride", width=1500, height=1300, ...)` fixed both immediately.
  Pair it with the `document.hidden` un-wedge; they fix different things.

- (2026-09-06) **`document.hidden` went True three separate times mid-form** (VW SF login, OEDIV smart-apply, Statista
  Ashby) and each time CDP `Input.*` went dead while `Runtime.evaluate` kept working - on Ashby it burned
  four attempts at one `type=number` salary field before the check. **Re-check `document.hidden`
  immediately before any keystroke-dependent step, not once per job.** The minimize->restore
  `Browser.setWindowBounds` cycle plus `Emulation.setDeviceMetricsOverride` fixed it every time.

- (2026-09-10) **`document.hidden` needs `Target.activateTarget` BEFORE the window cycle.** The 2026-09-09 recipe
  (minimize -> normal) cleared it on the tab that was already frontmost but did nothing for a
  background tab in the same window - `switch_tab(activate=True)` and `Page.bringToFront` both
  no-opped. The order that works: `cdp("Target.activateTarget", targetId=...)`, *then*
  `setWindowBounds` minimized -> normal, then re-read `document.hidden`.

- (2026-09-10) **`browser-harness` reads its script as cp1252, so UTF-8 source is mangled before it reaches the page.**
  Umlauts typed into a heredoc *or into a UTF-8 file piped into it* arrive as `Ã¼`. Only Python `\uXXXX`
  escapes (ASCII bytes in the script) survive; base64 them from there. Verified by reading `charCodeAt`
  back from the field: 195,188 = broken, 252 = correct.

- (2026-09-11) **document.hidden struck three times in one batch** and each time the fix was closing the foreign tabs
  (a 127.0.0.1:5173 dev server and a stale XING tab), not the window-state dance. Close stray tabs before
  a submit, not after it fails.

- (2026-09-11) **Two agents on one browser-harness daemon share ONE "current tab".** Another agent's research (arbeitnow /
  Greenhouse API docs, Karrierepilot) kept moving `page_info()`/`js()` onto its own tabs mid-form and finally
  closed the Henkel tab. A separate Chrome profile did NOT isolate it: the daemon, not the profile, holds the
  current-tab state. Fix that worked: `SID = cdp("Target.attachToTarget", targetId=TID, flatten=True)["sessionId"]`,
  then pass `session_id=SID` to every `Runtime.evaluate` / `DOM.*` call. That is immune to tab switches and works
  on a hidden tab for JS clicks and `setFileInputFiles`. Guard every write with a `location.href` check.
  `Page.captureScreenshot` on a hidden tab hangs until the IPC times out - `Target.activateTarget` first.

- (2026-09-12) **Match German option text by an ASCII prefix, never by exact string, from a bash heredoc.** `'ChatGPT,
  Claude o.Ä.'` never matched (the umlaut mangles to cp1252); `indexOf('ChatGPT')===0` worked.

### General — Verify

- 2026-08-24 — **E-mail confirmation links can be mangled by plaintext extraction.** KfW's "Bewerbung bestätigen" identity link rendered as `&codedca2f3f-...` in `PLAIN_TEXT` (a character swallowed into the param name) and the portal answered "Der übertragene Code ist nicht korrekt". The RAW message carried the true href (`&code=64ca2f3f-...`). **When a confirmation link fails, re-fetch the message as RAW before assuming the link is dead** - and note KfW DELETES the application after 20 days without that click, so this step is not optional.

*Portals that send NO confirmation email (verified 2026-08-30)*

Add to the list in feedback.md § VERIFY: **Faber-Castell `/oja/`** promises "In wenigen Minuten erhalten
Sie einen Zwischenbescheid per E-Mail" on its success page and then sends nothing (checked at +0 h and
+16 h). **Personio ctrl-qs** likewise sent no receipt. For both, the on-page success panel plus
`confirmation.png` is the proof; do not downgrade the row for a missing mail.

- (2026-09-01) **A bounced email handoff is invisible unless you look.** The CAS Software email to `jobs@cas.de` was rejected
  by the remote server (`550 5.7.1`) — the application only survived because the portal route ALSO went through
  the same afternoon. Add `from:mailer-daemon` to the end-of-batch Gmail sweep, not just the ack search.

- (2026-09-05) **Two email handoffs from earlier batches were never sent** (`bewerbung@bhs-intralogistics.de` 2026-09-04,
  `jobs@iph-hannover.de` 2026-09-02) - both logged Submitted with zero sent messages. `tracker.py emails` +
  the Gmail count query is doing its job; keep running it at the end of every batch.

- (2026-09-06) **Gmail confirmed both of this session's submits** (trivago `no-reply@trivago.com` "Your Application
  (Student Data Scientist - Content)", OEDIV `Bewerbung@oediv.de` "Eingangsbestaetigung"). The parallel
  session's **Kontron AIS produced no confirmation email** - left as its own session recorded it, but it
  is the one 2026-09-06 "Submitted" row with no independent evidence.

- (2026-09-06) **Kontron correction, and a second phantom-backlog row caught the same way.** The 2026-09-06 note above
  flagged Kontron AIS as the one Submitted row without email proof - that was WRONG. Its confirmation is
  `antwort+...@bms.empfehlungsbund.de` 00:35Z, identifiable only by the body (signed "Kontron AIS GmbH,
  Frau Zenner" + a status link under `/bewerbung/ais_automation_dresden/`); the sender is a generic
  Empfehlungsbund address and the subject is the generic "Vielen Dank fuer Deine Bewerbung", so it is easy
  to mis-attribute when several confirmations land in the same minute. **Match confirmations by BODY, not
  by sender or subject, whenever the ATS is a shared platform** (empfehlungsbund, bewerbermanagement.net,
  softgarden, personio all send employer-agnostic envelopes). All nine of the day's submits were confirmed
  once read this way.

- (2026-09-09) **Same-day rejections are real.** ONEJOON rejected the StepStone smart-apply ~90 minutes after it
  was sent. Do the Gmail sweep at the END of the batch, not the next morning, or the tracker carries
  a phantom Awaiting.

- (2026-09-10) **"Zero sent messages" does NOT mean "never applied" - both of my `tracker.py emails` findings were
  wrong, and the user corrected both.** The sweep flagged Fraunhofer IKS and CAS Software as dead
  `Submitted` rows; in fact IKS was applied through the **Fraunhofer careers portal** (so it was never
  going to appear in Sent, and that portal sends no acknowledgement), and CAS *did* bounce on
  2026-09-01 but the user re-applied **on the CAS portal**, which `jobs@cas.de` acknowledged on
  2026-09-07. The sweep only proves what the *email channel* did. Before downgrading any row from it:
  search Gmail for an **employer confirmation** as well as for the sent message, and ask the user -
  an email-channel row is often satisfied by a portal application later. A mailer-daemon reply in the
  thread proves that *send* failed, not that the application never happened.

- (2026-09-14) solago rejected within 8 hours - run the Gmail sweep at batch end, not next day.

### General — Handoffs and the NeedsUser backlog

- 2026-08-15 (NeedsUser drain): before treating a `NeedsUser` row as work-to-do, **check Gmail for that company first**. Draegerwerk had been sitting as "agent cannot set a password" since 24.07 while the user had actually finished the registration on 27.07, been asked for extra documents on 28.07, and been rejected on 12.08. The row was three weeks of phantom backlog. Rule: `NeedsUser` rows older than ~1 week get a Gmail check before a browser retry.

- 2026-08-15: a "captcha-blocked" row is still worth a full pass — filling every field and attaching the documents converts it from "the user redoes the whole application" into "the user clicks one button". levigo and jatosha were both parked 100% ready this way, and on Elementor/reCAPTCHA v3 the values survive the rejected submit.

- 2026-08-21 — **"TAB PARKED 100% READY" notes are worthless after a Chrome restart.** All five parked tabs from 2026-08-15/19 (Funke 95%, levigo 100%, jatosha filled, Schattdecor filled, BMW/Miele/Eppendorf login pages) were gone; `list_tabs()` showed a single tab. Rule: a parked tab is a same-day handoff at best — either tell the user to finish it in that session, or record enough in the notes to refill from scratch, and never count a parked form as progress in a later batch.

- 2026-08-21 — Liveness triage of the 12-row NeedsUser backlog: **all 12 postings were still live** (only jatosha's specific req had disappeared, into a generic contact form). The "~half the backlog is expired reqs" heuristic from 2026-08-16 did not hold — check, do not assume, in either direction.

- 2026-08-23 — **A handed-off tab can go stale and lose its session.** the user completed all three parked handoffs; BambooHR (FP Group) and Ashby (LIQID) confirmed by e-mail within a minute, but **CHECK24 silently failed** — the tab had reverted to a read-only form showing "Die Cookie-Funktion Ihres Browsers ist deaktiviert" and no confirmation mail arrived. Reloading, refilling and resubmitting worked immediately. **Rule: after a handoff comes back "done", verify each one against Gmail before marking it Submitted — and if a confirmation is missing, reload the form rather than trusting the parked tab.** (Also: on the fresh load CHECK24 remembered both the declined KI-Auswertung consent and the user's ticked `agbs_check`, so the redo cost nothing extra.)

- 2026-08-23 — **Two recorded blockers were WRONG when re-tested, and both converted the same evening.** (1) **levigo**: the noted "own-site form ends in a captcha the agent must not fill" was a **honeypot** — `f12_captcha-839` is `visibility:hidden`, 4x4px, and the correct handling is to leave it EMPTY, which the agent may do. Filled, uploaded and submitted in ~8 calls. (2) **Mercedes MER00046MM**: the block was only the expired Taleo password; once the user logged in the full 6-step wizard went through. **Rule confirmed for the third time: re-test the recorded blocker before treating a NeedsUser row as stuck — the note describes what the agent saw once, not what is true now.** Corollary: distinguish a real captcha from a honeypot by reading `getComputedStyle` + `getBoundingClientRect`, not by the field's name.

- 2026-08-24 — **A parked form that still shows all its values can still be dead.** I recorded "umantis parks are durable" after confirming both tabs held every field and upload overnight; the very next handoff proved the values are not the thing that expires. FZI's submit failed on umantis's **security token** ("The form was not saved because the security token was not sent") and the form blanked itself, while Baumann — submitted in the session it was filled — confirmed by e-mail in under a minute. **Durability of a park must be judged by whether the SUBMIT succeeds, never by whether the fields still look filled.** This is the same shape as the 2026-08-23 CHECK24 case, and it is why the standing rule holds: after a handoff comes back "done", verify each one against Gmail AND the tab's URL before writing Submitted — 1 of 3 came back done-but-not-sent this time.

- 2026-08-24 (login handoff) — **Once the user signs in, the "account wall" rows convert fast: Siemens, Dematic and KfW all completed the same session.** Worth planning around: park the credential-walled rows, get ONE login pass from him, then drive the wizards to submit. Siemens (5 steps) and Dematic/Workday (5 steps) each took one pass.

- 2026-08-24 — **Never park a half-filled form in the only spare tab.** The TSO-DATA form (fully filled, waiting on its captcha) was destroyed when the next job reused that tab via `goto_url`. Park handoff forms in their own tab (`new_tab`) and note the targetId in the tracker row, or accept that the handoff must be refilled.

- (2026-08-30) **Re-test a NeedsUser row against Gmail before the browser.** On 2026-08-30 two of eleven rows were phantom:
  ZEISS JR_1047706 had been applied to *and rejected* (2026-08-19 → 2026-08-25), and VW Infotainment had been
  submitted through StepStone on 2026-08-22 (Job ID 29532) while the row still recorded the SF login wall. Both
  were closed without touching a browser.

- (2026-08-31) **The clean-language pool was ~80% gated again**, and the survivors were mostly password walls: of 13 qualified
  rows this batch, 8 converted and 5 died on account creation (Hilti/Avature, B.Braun/SuccessFactors,
  Weidemann/Wacker Neuson, MBDA/Workday, Advantest/ADP). Prefill-and-hand-off is the realistic plan for those,
  so package them early rather than discovering the wall after the cover letter.

- (2026-08-31) **A "route unreachable" note is not evidence the application is missing — VW was a phantom for a day.**
  The Volkswagen row sat as NeedsUser with a detailed note (karriere.volkswagen.de `ERR_CONNECTION_RESET`,
  req not on jobs.volkswagen-group.com), and the application had in fact been **submitted and acknowledged
  on 2026-08-30 at 20:52** (`no-reply@career.volkswagen-group.com`, Job ID 28785). The note described a
  failed *re-attempt*. This is the third phantom in two days (ZEISS, VW Infotainment, now VW AG).
  **Rule: before opening or re-chasing any NeedsUser row, grep Gmail for the company/req first** — it is
  cheaper than a browser attempt and it is what the existing "re-test against Gmail before the browser"
  line was for. Applying it to the whole backlog at the start would have saved this one entirely.

- (2026-09-01) Two rows stay Blocked with sharper diagnoses rather than vague ones: BWT (all 13 required
  questions satisfied, `Aktion erforderlich` = 0, but Kontaktdetails never receives ANY badge —
  the SUBSEQ symptom, which cleared on its own retry) and MEAG (server-side reject with every
  required field satisfied, all three uploads confirmed, honeypot verified empty).

- (2026-09-01) **A "Wartungsarbeiten" / maintenance page seen from the agent session is NOT proof the employer form is down
  for the user.** CAS Software's `form.cas.de/support/formJob.aspx?ID=20090320212909` served Maintenance.aspx on
  three separate checks (2026-07-23, 07-24, 09-01) — including via the live session-token link taken straight
  off cas-mitgestalter.de — so I routed it to an email handoff. **the user then applied through that same portal
  the same day.** Before converting a "form is down" into an email handoff, say so as a hypothesis and offer
  the portal to the user first; the email route costs him a manual send and can double-apply.

- (2026-09-01) **A "Blocked / portal is broken" note is a hypothesis with a shelf life of about one batch.** Of 36 Blocked
  rows: 6 converted to Submitted today, 5 were stale bookkeeping (already submitted elsewhere — WISAG, SUBSEQ,
  Lülf+, both CAS rows), 2 were dead postings (1&1 expired, SCHOTT withdrawn), 1 was a real password wall, and
  only 2 stayed genuinely blocked with the same symptom. **Re-derive, don't re-read.**

- (2026-09-06) **Sweep result: 21 NeedsUser rows retested, 2 converted (NXP, R&S), 19 remain.** Of the 19, only ~6 are
  credential walls; the rest are things no login can fix - arithmetic captchas (KfW, Draeger x3), a German
  grade record the user alone can supply (Senacor), a candidate-authored work sample (Perplexity), and
  account *creation* (Stryker, Miele, Wacker Neuson, LVM x2, Deutsche Boerse, Hamburger Energienetze,
  MAHLE, HOERBIGER, FC Bayern, Endress+Hauser). **Triage the backlog by blocker TYPE first** - it would
  have pointed at NXP and R&S immediately instead of after eight dead logins.

- (2026-09-11) **A documented Blocked verdict is a reason NOT to retry.** The VW thesis (req 26228, Baunatal) went
  straight to Blocked because howtologin already records that jobs.volkswagen-group.com has no
  automatable apply route; re-deriving it would have cost the slot.

### General — Tracker

- Tracking.xlsx cannot be saved while open in Excel (~$Tracking.xlsx lock) — ask the user to close it, never kill the Excel process.

- Do NOT apply to Mercedes-Benz while the user's existing application there is in the interview stage (as of 2026-07-02). Ask before applying to any company where the tracker shows an active interview process.

- 2026-07-13 — tracker.py update without --status wipes Status to None; always pass --status on every update call.

- 2026-08-19 — **CROWN Gabelstapler (Abschlussarbeit KI-gestützte Codegenerierung, applied 04.07) reached interview and was rejected by phone.** Row was still `Submitted` — the interview stage had never been logged, so nothing in the tracker would have warned a later batch that this was an active process. Rule: when the user mentions an interview/call for a company, update the row (`--status "In Process"` / `--outcome`) in the same turn — phone-stage outcomes never reach Gmail, so the daily email routine cannot catch them and the tracker is the only record. Note: CROWN **reposted the same req on StepStone 18.08** (`am=INTERNAL` sweep, "vor 20 Stunden", Feldkirchen) — a fresh posting is not an invitation to re-apply to a role you were just rejected for; it stays a hard skip.

- 2026-08-22 — **All active-interview holds cleared; the tracker's interview warning can no longer fire for any company.** the user confirmed there are no live interview processes anywhere, and that Mercedes-Benz and CROWN are both dead. Three rows were still `Status=In Process` even though each already carried a terminal `Outcome` — AUDI (Praktikum KI-basiertes Assistenzsystem, Ghosted since the 2026-04-28 acknowledgement), ICB (Praktikant KI-Agenten, rejected 2026-07-23) and Xsolla (AI-First Engineering Intern, rejected 14 Aug). `tracker.py check` keys the warning off the **Status** column only (`"process" in status or "interview" in status`, tracker.py:155), so a recorded rejection in `Outcome` does nothing to lift it — the status has to be closed too. All three closed; **zero `In Process` rows remain**. Rule: when an interview process ends, close `--status` in the same turn as `--outcome`, or the company stays blocked for every future batch. The rule in `evaluator.md`/`search.md` (interview warning → ask the user first) **stands unchanged** — it is the state that expired, not the mechanism. Also normalised the one stray non-schema `Status=Applied` row (Huawei) to `Rejected`. **Still-live gates after this cleanup are the 90-day company cap only** — Mercedes-Benz (3 rows ≤90d), AUDI (3) and Siemens Energy (4) all read `CAP_REACHED`, which is the self-imposed 2/90d rule and needs the user's explicit go-ahead to override (precedent: the 2026-08-16 Mercedes entry), not an interview hold. Unrelated open item that survives: the Mercedes-Benz Masterarbeit `MER00046MM` row stays `NeedsUser` — its blocker is the expired Taleo password, which only the user can reset.

- (2026-08-31) **`--outcome` is not accepted by `tracker.py add`, only by `update`.** Logging a fresh email handoff takes two
  calls: `add --status Submitted` then `update --status Submitted --outcome Awaiting`.

- (2026-09-04) **`tracker.py update --ref` is a FILTER, not a setter.** Passing the new reference in `--ref`
  makes the row un-matchable ("no matching row"); the setter is `--newref`. Cost three failed calls
  on the Debeka retarget.

- (2026-09-06) **`tracker.py update --ref` is a FILTER, not a setter.** Passing a new reference silently matched zero
  rows ("no matching row - use 'add'") three times in a row and looked like a company-name spelling
  problem. The setter is `--newref`.

### General — CV, cover letters and documents

- Upload only package-local files.

- (2026-08-29) **Cover-letter word count: draft tight the first time.** Every letter this batch overshot 250-260 on the
  first pass and cost 2-3 rebuild cycles. Aim for ~245 words in the draft; the PDF/A export is one page
  well past 260, so verify page count with pypdf rather than iterating on the count.

- (2026-08-30) **Cover letters: the first draft still overshoots.** Both letters this batch came in at 304-310 words against a
  250-260 target and needed two trim passes each. Draft at ~245 words; both finished at 268-269 and still exported
  as one page, so page count is the check that matters.

- (2026-08-30) **Cover letters: build to ~250 and CHECK PAGE COUNT, not word count.** German letters run longer than English at equal
  word count - 302 and 291 words both spilled to page 2 while a 304-word English letter stayed on one page. Trim German
  drafts to ~260.

- (2026-08-30) **The cover-letter templates carried a stale postcode (<postcode2>) that contradicts resume.md (<street>, <postcode>).**
  Both templates are now fixed, but three letters went out with the old header before I caught it. **Diff the template
  header against resume.md once per batch** - the CV has always had the right address, so the mismatch is invisible
  unless you look.

- (2026-08-31) **A combined Embedded+AI CV now exists** at `application/CV/Embedded_AI/` (EN `CV_…_Embedded_AI.pdf`,
  DE `Lebenslauf_…_Embedded_AI.pdf`), rebuildable with `scripts/make_combined_cv.py [--lang en|de]`
  + `scripts/docx2pdfa.ps1`. It merges the ESP32-S3/KiCad/SPI/VHDL/Adalm-Pluto projects from the Embedded CV with
  the LangGraph/RAG/ResNet50 work from the AI CV — nothing invented. Use it for embedded/hardware-adjacent roles
  where either single CV would hide half the profile (the user's standing request, 2026-08-31).

- (2026-08-31) **An `Arbeitszeugnis` now exists as a package-ready asset.** Taunus Sparkasse required one and it looked like
  a NeedsUser handoff — but pages 12-13 of `Other Docs/Weitere_<Name>.pdf` are a real Alphapark
  EXPERIENCE CERTIFICATE and an Aimbys internship certificate. Extracted to
  **`Other Docs/Arbeitszeugnisse_<Name>.pdf`**. `Weitere_…pdf` is a 13-page scanned bundle whose
  contents are otherwise invisible — **page-by-page `extract_text()` over it before declaring a document missing.**

- (2026-08-31) **Cover letters finally landed in range on the first pass** (249 / 260 / 267 words, all one page) by drafting
  five paragraphs at ~245 and trimming once. The 290-word first draft needed exactly one trim pass — that is the
  cheapest this has been; keep drafting short rather than trimming twice.

- (2026-09-01) **Cover letters: five letters, four in range on the first pass** (263 / 242 / 245 / 265 / 246 words, all one
  page) by drafting five paragraphs at ~245. The one that overshot (296) needed a single trim. Continue drafting
  short; German at 265 words still fits one page, at 296 it does not.

- (2026-09-02) **Cover letters: five of seven overshot and needed one trim pass; a 246-word German letter still spilled to
  page 2 when the RECIPIENT BLOCK was two long lines.** DLR only fit after shortening
  "Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR) / Institut fuer Flugsystemtechnik, Oberpfaffenhofen" to
  two short lines and cutting the subject line. **Page count depends on the header, not only the body** - trim the
  recipient block and subject before trimming a fifth paragraph.

- (2026-09-03) **Cover letters: 2 of 3 spilled to page 2 on the first pass at 257 and 273 words.** Both fit after one
  trim to ~230 plus a shortened subject line. For letters with a long recipient block, draft at ~235.

- (2026-09-04) **Cover letters: 8 of 9 needed at most one trim** and every one exported as a single page
  (251-271 words German, 292-293 English). Drafting five paragraphs at ~245 continues to be right.

- (2026-09-04) **A single required "vollstaendige Zeugnisse" slot with `multiple=false` needs a merged PDF.**
  Machineseeker wanted Studium + Ausbildung + Abitur in one file; `pypdf.PdfWriter` over Transcript +
  B.Tech degree + HighSchoolReport produced a 5-page `Zeugnisse_<Name>.pdf` that satisfied it.
  Worth keeping as a standing asset rather than rebuilding per job.

- (2026-09-04) **Never author a German cover letter through a bash heredoc.** Written that way the paragraphs arrived
  as ASCII transliterations ("zusammenhaengen", "ueber", "Gespraech") and would have gone out looking
  wrong. Author every letter with the **Write tool in UTF-8**, then verify with
  `PdfReader(...).pages[0].extract_text()` that a real umlaut survived.

- (2026-09-05) **Cover letters: 6 of 7 overshot on the first pass** (276/292/275/324/345 words) and every one fit on a
  single page after exactly one trim to ~245-270. The English letter ran longest (345). Drafting five
  paragraphs at ~235 for English would have saved a rebuild each.

- (2026-09-07) **Verify recipient postal addresses; do not write them from memory.** I put Fraunhofer IKS at
  Hansastraße 32 from memory — it is Lichtenbergstraße 13, Garching. Check the Impressum every time.

- (2026-09-07) **German cover letter vs. B1 German on the CV.** the user's call (2026-09-07): where a posting accepts
  "Deutsch und/oder Englisch", write English. A C1-reading letter next to a B1 language line is a
  mismatch that surfaces at interview. `coverletter.md`'s "match the posting language" still holds when
  the posting is German-only.

- (2026-09-07) **Outreach emails should ask something.** Ending on "I'd be glad to discuss" invites no reply; a
  specific question the right person can answer in one line does. Stagger the sends too — same-day is
  right for a named scientific supervisor, day 3-5 for a recruiting mailbox.

- (2026-09-07) **Tailored LaTeX CV only when a job is worth one.** Otherwise send the existing designed PDFs
  in `application/CV/`. The generator is the exception, not the default.

- (2026-09-07) **A German posting gets a German CV.** `scripts/make_tailored_cv.py` carries a `lang` per job
  and emits `Lebenslauf_*.pdf` for `de`, `CV_*.pdf` for `en`; `--lang` overrides. German wording
  is copied from the docx builder's German section list (`DOCX_CV['de']` in `application/cv_data.py`) so nothing is invented — only
  LegalAddress needed new German, and that translates facts already in resume.md.

- (2026-09-07) **No photo**, by decision. The designed PDFs keep theirs; the generated ones have none.

- (2026-09-07) **Umlauts are fine in the LaTeX path** — verified end to end through pdflatex with inputenc
  utf8. the user's rule is to fall back to an ASCII spelling or the English word only when a
  string actually breaks, and only where it reads naturally; tech terms staying English on a
  German CV is normal and was left alone. The place that *does* break is browser form-filling,
  where a bash heredoc turns `Männlich` into `MÃ¤nnlich` — base64 those, per application.md.

- (2026-09-07) **Two claims of mine were wrong, and both had been used as arguments.** The designed CVs are
  not badly parsed: they extract 4,284 chars in correct reading order, so "switch for ATS
  reasons" was never a real argument. And the old `docx2pdfa.ps1` does not leak a WINWORD
  process on failure — each call is its own process and Word is released on exit. Test the
  claim before it becomes a reason to change something.

- (2026-09-07) **`resume.md` was a lossy summary of the CVs, not the richest source.** The dataset names,
  model configuration, locations, and two whole projects (VHDL stopwatch, baseband signal) existed
  only inside the CV PDFs, so generated CVs read vaguer than the user's own. Back-ported 2026-09-07
  (+26% content). **When a document holds detail that resume.md lacks, back-port it** — the
  generator can only be as specific as its source.

- (2026-09-09) **A cover letter built from the German Kostal template overflows to 2 pages above ~235 words**,
  even though `coverletter.md` asks for 250-260. Check `len(PdfReader(pdf).pages) == 1` after every
  conversion and trim; 229 words was the first version that fit. Word count is the target, one page
  is the constraint.

- (2026-09-12) **`make_cover_letter.build()` stamps a STALE DATE unless you pass one.** Its signature is
  `date="<your city>, 30. August 2026"` - a hardcoded default, so every letter built without an explicit
  `date=` argument carries 30 August. Always pass `date="<your city>, <today>"`. Worth auditing older packages.
  **Fixed since:** `build()` now stamps today's date when `date` is omitted; pass `city=` for the place prefix.

- (2026-09-12) **The 250-260 word rule and the one-page rule conflict on the German template.** 255 words spilled the
  signature onto page 2; what actually fixed it was cutting the recipient block from three lines to two
  (243 words then fit). Check `len(PdfReader(pdf).pages)` every time and trim the ADDRESS before the prose.

- (2026-09-26) German cover letters cannot hit the 250-260 word body target and stay on one page. At 250-266 German words every one of six Anschreiben spilled onto a second PDF page (German compounds are far longer than English words); trimmed to 212-234 they all fit. Rule: English letters aim at 250-260, German letters at 210-235, and the one-page PDF check is the authority - always run pypdf len(PdfReader(f).pages)==1 on every letter before uploading, because make_cover_letter.py only prints the word count.

---

# Portal sections

One `##` per ATS. Company-specific `### <Portal> — <Company>` subsections are where
your own runs accumulate; `addlesson.py` creates them.

## Aggregators

### Aggregators — General

*Aggregator traps (jobportale-siegen.de / berufsstart, itsax.de, karriere.fhdw.de)*

2026-07-23 - XING often links to a regional/university aggregator rather than the employer ATS. Three behaviours seen in one batch: **itsax.de** hosts its own inline application form (first_name/last_name/email/telephone/livingInGermany radios/comment/file-upload) and forwards to the employer - usable. **karriere.fhdw.de** shows the employer's ad but its 'Jetzt bewerben' points at FHDW's own *study* application - the real channel is the employer email in the ad body. **jobportale-siegen.de** (berufsstart network) has no apply control at all and its `anzeigenverlinkung.php` redirect renders blank - dead end, only the printed phone/postal contact remains. Always follow the aggregator to an actual apply control during EVALUATE.

## amazon.jobs

### amazon.jobs — General

- (2026-09-24) First amazon.jobs submit (AWS SDE Internship 3130528). Route: job page -> 'Bewerben Sie sich noch heute' = /applicant/jobs/<id>/apply -> passport.amazon.jobs email-first login (enter email, Weiter, THEN coordinate-click the password field - Chrome autofill fires there). If the saved credential is not your `JOBAGENT_EMAIL`, confirmations land in a mailbox the Gmail tool cannot read: the portal's /summary?result=success page is the proof. The form is a 9-tab wizard that PREFILLS from the last Amazon application and the prefill is stale - the preferred start date and the CV were both months old and the sponsorship answer was wrong, so re-check every prefilled tab against resume.md. Every date input (placeholder JJJJ-MM or JJJJ-MM-TT) silently reverts to empty after cdp Input.insertText and re-blocks Fortfahren one section later; only the native value-setter plus input+change+blur commits them. Dropdowns are select2: click the control, read li.select2-results__option, coordinate-click the option; multi-selects need the search field re-clicked between every pick and show chips as li.select2-selection__choice. Replace the CV via input#document-replace-input.

## arbeitnow

### arbeitnow — General

- **arbeitnow** — free and worth a pass. `?search=` barely filters and it 429s after ~4 rapid calls:
  page the unfiltered feed and filter in Python.

- 2026-08-25 — **arbeitnow is worth a pass again (it was written off as "zero" on 2026-07-14).** 650 rows fetched free over 5 API pages produced Agile Robots x2 (Personio, both submitted) and Phlair (Ashby, submitted) — 3 of the batch's 10. Its "similar jobs" blocks on a job page also surface leads the API search misses. Caveat: `?search=` barely filters (it returns the default page) and the API **429s after ~4 rapid calls** — page through the unfiltered feed and filter in Python instead.

- (2026-08-29) **arbeitnow's free JSON feed is worth a full pass at the start of every batch.** Paging 10 pages
  (~1150 jobs) into a file and filtering in Python cost no browser time and produced 9 of this batch's
  qualified rows, including two Personio guest forms and a paid TUM-supervised master thesis. Its apply
  links resolve to the employer ATS via `<job-url>/apply`.

- (2026-08-30) **arbeitnow's `search=` is useless but its unfiltered feed still pays - and rate-limits hard.** It 429s after ~3 rapid
  pages; page it with ~6 s sleeps and a retry, and cache to disk. 1300 jobs -> 187 student/tech candidates -> 94 with a
  clean language line -> 4 genuinely fresh after dedupe.

- (2026-09-01) **arbeitnow was fully mined again** (1150 jobs → 87 clean → 11 tech-titled → 7 duplicates → 0 usable), and the
  StepStone/XING clean pool produced only 5 genuinely fresh qualified rows out of ~90 postings screened in
  detail. Duplicate rate on the "clean & fresh" shortlist was **~70%** — the queue-wide company+position diff
  caught 19 duplicates that the per-company cap verdict would have waved through. That pass is now clearly the
  single highest-value step in the pipeline.

- (2026-09-02) **arbeitnow was fully mined for the third batch running** (750 jobs -> 16 clean student/tech titles -> 0 usable:
  Hypatos "Working Student IT" is helpdesk, Simcon is CAE plastics plus Schulungsunterlagen, the rest marketing
  or design). Budget one Python pass, expect zero, and move on.

- (2026-09-03) **arbeitnow finally paid again after three empty batches**: 950 jobs → 5 clean student/tech titles →
  **2 submitted** (Supreme Sports via Recruitee, autarc via Personio guest). Both had the best language
  lines of the day ("You are fluent in English. German … is a plus"). Keep budgeting the one Python pass.

- (2026-09-04) **arbeitnow paid once again**: 950 jobs -> 121 student/tech titles -> 46 clean -> 1 genuinely fresh
  and usable (greenventory Cloud & DevOps, submitted). Keep budgeting the one Python pass.

- (2026-09-07) **arbeitnow's `?search=` parameter is ignored.** Three different keywords returned byte-identical
  results. Do not trust it to filter; either fetch and filter locally, or skip the API.

- (2026-09-10) **The arbeitnow API is the cheapest source in the file and it is under-used.** 1,783 unique jobs
  over 15 `curl` pages, filtered in Python, produced **all 10** of today's qualified roles - no
  StepStone, no XING, and zero browser calls during search. Page 1-3 are mostly noise; the strong
  technical student roles started around page 6. Pull 10+ pages before judging the pool.

- (2026-09-11) **When every board is dry, re-read the feeds you already pulled with a WIDER filter.** Re-filtering the
  arbeitnow pages on the *description* instead of the title surfaced IPG Automotive, whose student roles
  end with "Die Moeglichkeit, im Anschluss deine Abschlussarbeit bei uns zu verfassen" - three
  thesis-track roles that a title filter for Masterarbeit/Thesis never sees.

- (2026-09-12) **`arbeitnow.com/jobs/companies/<co>/<slug>/apply` 302s straight to the employer ATS.** One `curl -L -o
  /dev/null -w '%{url_effective}'` per job resolved 8 employers (5 Personio, 2 JOIN, 1 Ashby) with no browser
  at all. The apply button on the HTML page is JS-only, so scraping hrefs finds nothing - use the /apply URL.

- (2026-09-12) **arbeitnow's whole board is ~1,700 records / 15 pages.** Pulling it twice in a day is pointless - the second
  batch of the day needs a different source, or tomorrow's postings.

- (2026-09-14) arbeitnow (2,200 jobs) yielded only 4 fresh roles - mined out again; LinkedIn guest API + ATS resolution
  supplied the other 6. Resolving the host took longer than the forms.

## Ashby

### Ashby — General

*Ashby*

**Used by:** Growing number of tech companies and startups.

**How to recognize:** URL contains `jobs.ashbyhq.com` or the form has Ashby branding.

*Common Quirks*

- Very clean, single-page form.

- Sometimes has a "referral" field — leave blank unless applicable.

- **`type=number` fields (e.g. "Salary expectations") do NOT register via the native value-setter + input-event trick** — React state stays empty and submit fails with "Missing entry for required field". Fix: focus the field, clear it, then type real keystrokes via CDP `Input.dispatchKeyEvent` with `type:"char"` **only** (sending both keyDown+char doubles each digit → "1155"). Text/email fields fill fine with the native setter; only number fields need keystrokes (confirmed Avelios 2026-07-16).

- Date custom fields use **react-datepicker**: day cells are `.react-datepicker__day` divs (click via native `.click()`); month nav buttons re-render on each click so **re-query the next button every iteration** (a cached reference clicks a stale node and does nothing). Value lands as `MM/DD/YYYY`.

- File inputs whose `id` starts with a digit break `DOM.querySelector("#<id>")` (invalid CSS) → use `input[id="<id>"]` attribute selector.

*Ashby (jobs.ashbyhq.com) — 2026-08-22 addition*

- `_systemfield_name` / `_systemfield_email` / phone and the **file inputs** and **radio groups** do NOT accept the native value-setter or synthetic `MouseEvent`s: submit returns "Missing entry for required field: …" while `input.value` reads correct. They need **real** CDP input — `el.focus(); el.setSelectionRange(0, el.value.length)` (wrap in try/catch: `type=email` throws on `setSelectionRange`) then `cdp("Input.insertText", text=...)`; radios and the CV drop-zone need a genuine mouse click. Custom questions, date fields and textareas *do* take the native setter.

- File inputs have **no `name`** (only `id`, e.g. `_systemfield_resume`) — `input[name="..."]` selectors fail; tag them with `setAttribute` and select by index/id.

- Date custom fields render **MM/DD/YYYY** — "01.09.2026" becomes 9 January. Write `09/01/2026` for 1 September.

- 2026-08-23 — **Ashby needs real input events for its system fields.** `_systemfield_name`/`email`/phone, the radio groups and the CV drop-zone all reported correct `.value` yet submitted as "Missing entry for required field"; only `cdp("Input.insertText", ...)` after a focus+select fixed name/email/phone, and the radios/upload never registered while the CDP Input pipeline was wedged. Custom text questions, dates and textareas take the native setter normally. Also: Ashby date fields are **MM/DD/YYYY** — "01.09.2026" silently means 9 January.

- 2026-08-25 — **Ashby auto-submit worked (2nd success, after Avelios), so the "Ashby is submit-proof" note from Manex/Hawk is wrong as a blanket rule.** Phlair went through on the first genuine attempt; the two earlier failures now look like spam-scoring on those tenants, not an Ashby-wide block. What did bite: its **react-datepicker is MM/DD/YYYY**, so a German-format "01.09.2026" silently became 9 January. Drive the picker (next-month arrow, then the day cell) and read the field back before submitting.

*Ashby - read the form without a browser; clicks need a visible document (2026-09-11, 7 submitted)*

- **The whole application form is available as JSON**: POST
  `https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobPosting` with query
  `jobPosting(organizationHostedJobsPageName, jobPostingId) { applicationForm { sections { fieldEntries
  { ... on FormFieldEntry { id field isRequired } } } } }` - returns every field's `path` (= the DOM id),
  type (String/Email/Phone/Number/Boolean/ValueSelect/MultiValueSelect/Date/Location/File), title,
  required flag and `selectableValues`. Build the fill config from it before opening the page.
  (`descriptionPlain` is NOT a valid field on FormFieldEntry - the query fails if you add it.)

- **Boolean fields are Yes/No `<button>`s** (`_active_` class when chosen), not checkboxes; ValueSelect /
  MultiValueSelect render as radios/checkboxes - click their `label[for]`, not the input.

- **All clicks no-op while `document.hidden` is true, even with a single tab** - run activateTarget +
  window minimized->normal after navigation. Text fields filled via `Input.insertText` still show values,
  so the problem only surfaces as "checked:false" on radios/consent.

- Location is `input[role=combobox]` with placeholder "Start typing..." (no `_systemfield_location` id on
  some tenants) - find it via its label, type the city, click the `[role=option]`.

- Success text varies: "Your application was successfully submitted" (default) vs a custom
  "Thank you for your application..." (Avelios) - check that the Submit button is gone as a fallback.
  Confirmation mail from `no-reply@ashbyhq.com` arrives within ~1 min on tenants that send one - not all
  do (see 2026-09-25 below), so the on-page text is the proof.

- (2026-09-11) **`document.hidden` also strikes with ONE tab open.** On Ashby every radio/Yes-button/consent click
  was silently ignored until `Target.activateTarget` + window minimized->normal; text fields filled via
  `Input.insertText` still "worked", which hides the problem. Run the visibility fix right after
  navigating, before the first click.

- (2026-09-12) **A truncated field dump produces unusable selectors.** Slicing Ashby ids to 34 chars silently broke six
  `querySelector` calls (they are 36-char UUIDs) - every field read "MISSING" while the form was fine.

- (2026-09-16) (2026-09-16) The ApiJobPosting form JSON is also a LANGUAGE-GATE DETECTOR, not just a fill config. Langdock's LinkedIn text said only 'communicate clearly and professionally in both German and English' (no level named = passes the usual screen), while the form carried a REQUIRED Boolean 'I have C1+ or equivalent in German language'. One GraphQL POST caught it before packaging or a browser tab. Read the schema on every Ashby job and grep the field titles for C1/C2/Deutsch/German before investing.

- (2026-09-19) 2026-09-19 (amber): the whole form went through with bh_helpers alone - safe_fill (hit-tested click + selectAll + insertText) registered the system name/email/phone, the type=number salary and the MM/DD/YYYY date; setFileInputFiles on _systemfield_resume worked; Yes/No buttons via safe_click (verify aria-pressed). The location typeahead: safe_fill the text, then safe_click the [role=option].

- (2026-09-23) _systemfield_name can fail submit with "Missing entry for required field: Name" even after cdp Input.insertText leaves the correct .value - React never committed it. Fix that worked on rivianvw.tech: focus + setSelectionRange, a real Delete keyDown/keyUp to clear, then per-character Input.dispatchKeyEvent type=char, then blur. Same submit then went through unchanged. Treat insertText as necessary but not always sufficient on system fields; always resubmit once after a Name/Email correction rather than re-filling the whole form.

- (2026-09-25) Two Ashby gotchas worth the note. (1) safe_click on a Submit tagged in an EARLIER browser-harness call returns {'ok':False,'reason':'stale'} - Ashby re-renders the button after the last answer commits, so tag AND click it in the same call, or re-tag first. (2) Big tenants (Snowflake) drop the _systemfield_location id entirely: the field is input[role=combobox] with placeholder 'Start typing...' and no id, so '#_systemfield_location' throws. Find it by placeholder/role, set_text the city, then click the [role=option]; it commits as '<City>, <State>, <Country>'. Boolean YES/NO buttons are easiest handled by tagging every YES/NO button in document order (2 per group, groups follow the API field order) and reading back aria-pressed.

- (2026-09-25) Ashby confirmation mail is PER TENANT, not guaranteed: Snowflake's 'Thank you for applying' from no-reply@ashbyhq.com landed within a minute, while Langdock and Kyrall sent nothing in the same-night sweep. So the 2026-09-11 note that a no-reply@ashbyhq.com mail 'arrives within ~1 min' cannot be used as the submit test - treat the on-page 'Your application was successfully submitted.' plus the Submit button disappearing as the proof, and do not reopen a row just because no mail came.

## BambooHR

### BambooHR — General

*BambooHR*

**Used by:** Small to mid-size companies.

**How to recognize:** URL contains `<company>.bamboohr.com`.

*BambooHR (<company>.bamboohr.com) — 2026-08-23 addition*

- `nickname_*` (label "Please leave this field blank") is a **honeypot** — never fill it.

- Field ids are Fabric UI and **regenerate between renders** (`FabricTextField-318` → `-328`); select by `placeholder` instead (the Date Available field is `input[placeholder="dd/mm/yyyy"]`).

- The country `<select>` renders with a single empty-text option; its displayed value lives in the wrapper's text (`Germany`), so read the wrapper, not `option.text`.

- **Submit reveals a reCAPTCHA** ("Almost there! Please confirm you're not a robot") → bot detection, hand off to the user with the tab left open.

- 2026-08-23 — **Two more bot-detection walls: BambooHR and CHECK24's career.check24.de.** BambooHR (azolver) fills fine — including its `nickname_*` honeypot, which must stay empty — then reveals a reCAPTCHA at submit. career.check24.de needs the applicant to accept a **Vermittlungsvertrag** (a placement contract), which is beyond a data-processing consent and so is the user's call, not the agent's. Both are "fill everything, leave the tab open, hand off the same day" cases like Greenhouse.

- (2026-09-24) icct.bamboohr.com/careers/401 shows the pattern to check BEFORE investing: three separate REQUIRED file slots (Cover Letter*, Resume*, and a Python code sample*) plus a required free-text field asking for two references with contact details. Read the file-slot headings early - they are not on the input, walk up the parents until the first line is not "Choose File". Radios have no id and no label, only name=customQuestionAnswer and value=Yes/No, and repeat per question, so address them by index order and set them with a CDP coordinate click (label-based clicking finds nothing). A code sample or referee list is a candidate fact, not an agent fact - prefill everything else and hand off rather than skipping the row.

## Breezy HR

### Breezy HR — General

*Breezy HR (<company>.breezy.hr)*

2026-07-23 (GECKO) — Guest form, no login. `#main-attachment` (name `cResume`, required), `cName` / `cEmail` / `cPhoneNumber` / `#fullAddress` (required), questionnaire fields named `section_<ts>_question_<n>` (file inputs get ids `questionnaire-file-<ts><n>`), `gdprAgreement` checkbox required. **`hp_<hex>` (e.g. `hp_7f2b`) is a honeypot — leave empty.** Selects take the native setter with the option's *text* as value. Submit → `/apply/submitted` "Application Submitted"; **`document.body` is briefly null during the transition** — sleep before reading. Gmail confirmation from `candidate-*@<company>.breezy-mail.com`.

## catch-talents

### catch-talents — General

*catch-talents (catchHR)*

**Used by:** German SMEs/startups; `easyapply.jobs/r/<id>` short-links redirect here.

**How to recognize:** URL `jobboard.catch-talents.de/companies/…/jobs/…/apply`. Guest, no login.

- Standard text fields (firstName/lastName/email/emailConfirm/phone/date/salaryPreview) fill with the native setter. "Desired salary" is **per month** (Werkstudent ≈ 1300 EUR/mo for 15 EUR/h × 20h).

- Required dropdowns are **ng-select** (Angular) rendered as `<ng-select>` reading "Please select" — the native-select approach fails. **Coordinate-click** the `<ng-select>` box to open, then click the `.ng-option`. Fields: Salutation (Mr./Ms.), Country code (defaults +49), and "Select language level" — the latter is paired with a language name in its container text (e.g. "German | Please select | …"); map truthfully (DE B1 → "Good knowledge (B1)").

- Two required consents: Terms/16+ and data-processing — check both. Real confirmation = green checkmark "Your application has been submitted successfully."

## CHECK24

### CHECK24 — General

*CHECK24 jobs (jobs.check24.de)*

**Used by:** CHECK24 own careers portal. Reached via StepStone "Ich bin interessiert" → "geklappt?" → Unternehmenswebsite. **Guest form, no login.** Standard HTML inputs (`first_name`, `last_name`, `email`, `phone`, `sq_*` screening questions, `select` dropdowns) — `fill_input` for text, native-setter for selects.

- Long screening set: address (`sq_…`=Straße, PLZ, `location_query`=Ort), Deutsch-Kenntnisse select (A1-B1/B2/C1/C2 → pick **A1-B1 (Grundkenntnisse)** for the user), Arbeitsgenehmigung (Nicht-EU befristet), Umzugsbereitschaft (Ja per prefs), Stundenlohn (14-15 per prefs), source dropdown (no StepStone option — any per prefs).

- **Two silent-fail traps (both block submit with no obvious error):** (1) **"Ort" is a geocoding autocomplete** — typing text leaves hidden `location_payload` empty; must type via real keystrokes and **click the suggestion row** ("<your city>, Bayern, Deutschland") so `location_payload` fills. (2) **"Frühester Eintritt" is a DATE field** (`dd.mm.yyyy`) not free text — "ab sofort" errors "Bitte gebe ein Datum…"; use a real date (e.g. 01.08.2026). Success → `/apply/success/` "Vielen Dank für Deine Bewerbung".

*CHECK24 career portal (career.check24.de/<slug>.html)*

**Used by:** CHECK24 (this is the concludis/`bewerbung_form[...]` platform, NOT the `jobs.check24.de` form documented above). Reached via StepStone → Unternehmenswebsite.

- Fields are `bewerbung_form[<name>]`; native value-setter works for text and selects. Placeholders (not labels) carry the real question — read `input.placeholder`: `eintrittsdatum`="Frühester Eintritt (TT.MM.JJJJ)*", `vordef_bew_feld_26`="Immatrikulation – Wie lange bist Du das noch?*", `freifeld4_z`="Gewünschte Wochenarbeitszeit*", `freifeld2_z`="Stundenlohn (gewünscht) in Ziffern*", `freifeld1_txt`="Von CHECK24-Mitarbeiter empfohlen." (leave blank).

- `sprachkenntnisse[]` and `vordef_bew_feld_254[]` are **multi-selects** — set `option.selected` per option, then fire input/change.

- **Every file upload pops a jQuery-UI dialog** ("Hinweis … Inhalte durch eine Künstliche Intelligenz (KI) ausgewertet … Bei Ablehnung wird keine KI eingesetzt") with **Akzeptieren / Ablehnen**. Click **Ablehnen**. Each retry stacks another dialog **and another `.ui-widget-overlay`, which swallows every later click** — the page just looks greyed out. Answer the dialog once, and if stale copies remain, remove the leftover `.ui-dialog`/`.ui-widget-overlay` nodes before touching the form again.

- **Submit requires ticking `agbs_check`: "Hiermit beauftrage ich die CHECK24 Personal … und akzeptiere den Vermittlungsvertrag".** That is a placement contract, not a data-processing notice → **hand off to the user** (fill everything else, leave the tab open, tell him it is one checkbox + "Bewerbung absenden").

- (2026-09-05) **The employer-page language re-screen killed only ONE of ten today, but it was the last one:** CHECK24's
  StepStone card was clean while the body demands *verhandlungssichere* Deutschkenntnisse **plus**
  "exzellente Noten (Hochschulreife und Studium)". Screening the shortlist's bodies before packaging remains
  the cheapest filter - and the replacement pulled from the arbeitnow leftovers (Maple Tales, Flutter)
  converted the same hour.

## concludis

### concludis — General

*concludis / "prospective" platform (corpuls, HOPPECKE, UNITY, SFC Energy — jobs.<company>.com)*

2026-07-23 — Same engine everywhere; the recipe is identical across tenants:

- URL pattern: `...-de-j<NN>.html` = job ad, **`...-de-f<NN>.html` = the application form**.

- Fields: `#gender` (`GENDER_MALE`), `#vorname` `#nachname` `#strasse` `#plz` `#ort` `#geburtsdatum` (TT.MM.JJJJ) `#telefon` `#mail` `#eintrittsdatum` `#gehaltswunsch` (numeric only), `#country` / `#nation` / `#wie_gefunden` selects use opaque `VORGABEWERT_*` / `TA_*` / `PUB_*` values — read `select.options` first. Germany is `VORGABEWERT_799aa285cec4005187038` on every tenant seen.

- **Dismiss the cookie banner ("Ablehnen") FIRST** — with it open, `fill_input` and the native setter silently no-op on the form fields (cost several calls at HOPPECKE).

- **The submit control is an `<a>` with text `SENDEN`, not a `<button>`** — `[...form.querySelectorAll('a')].find(a=>a.innerText.trim().toUpperCase()==='SENDEN').click()`. Success page: "Bewerbung abgeschlossen / Vielen Dank für Ihre Bewerbung!".

- `input[name=website]` is a **honeypot** — leave empty.

- Upload slots by input name: `anschreiben` (usually the required "Komplette Unterlagen"/"Bewerbungsunterlagen*"), `lebenslauf`, `anlage1/3/5/6/9`, `foto`. Read the labels — the mapping differs per tenant (UNITY: `anlage9` = Motivationsschreiben, `anlage1` = Zeugnisse).

- **CRITICAL — upload ONE file at a time and verify each before the next.** The widget is AJAX and `input.files` always reads 0; the only proof is the filename appearing in `document.body.innerText`. Setting three files back-to-back at UNITY silently dropped two of them, and the application went out with **only the Anschreiben** — and UNITY blocks a second attempt ("Eine Bewerbung pro Stellenausschreibung ist nur einmal möglich"). Always: `setFileInputFiles` → `sleep(5)` → assert the filename is on the page → next file.

*concludis — 2026-07-24 updates (ASAP join.asap.de, Stern Stewart, Kermi)*

- **JS `.click()` on SENDEN is now server-rejected** ("Leider konnten wir Ihre Anfrage nicht bearbeiten. Bitte versuchen Sie es erneut.") — scroll the anchor into the viewport (`window.scrollTo`, verify `elementFromPoint` returns it) and **coordinate-click**. Verified: Stern Stewart submitted this way after 2 JS-click rejections. ASAP (join.asap.de) rejects even the coordinate click — treat that tenant as NeedsUser after 2 tries.

- These tenants have **named doc inputs** (`lebenslauf`, `anschreiben`, `anlage1..N`) instead of the type-select widget; `DOM.setFileInputFiles` + change event works, `input.files` reads 0 afterwards, filename in body text is the proof. **Kermi truncates the filename with an ellipsis** ("Bewerbungsunterlag...ya.pdf") — verify by prefix, not full name.

- Kermi field variants: `staatsangehoerigkeit` (options "Indien" not "indisch"), consents `freifeld1_ms` + `vordef_bew_feld_104` with options **"Ich stimme zu"** (not "Ja"), `vordef_bew_feld_12` = Lohnvorstellung (text, "15 EUR/Stunde" accepted), second source-select `freifeld4_ms`. Kermi also has a **second cookie layer** ("Privatsphären-Einstellungen" bottom bar) that sits over Senden — its Ablehnen needs a coordinate click too.

- Stern Stewart: required doc slot **anlage1 = "Akademische und praktische Zeugnisse (inkl. Abitur)*"** → transcript PDF satisfied it; source select has no XING option (used "Social Media").

- (2026-08-30) **Do not hand-clear parsley error classes to force a submit.** Stripping `.parsley-error` off a concludis select made
  the client-side error vanish and left the form permanently un-submittable (`#formsent` stuck at 0) - a clean reload
  and refill did not recover it either. Fix the field, or reload before the state is polluted.

## Cornerstone (csod)

### Cornerstone (csod) — General

*Cornerstone (csod)*

**Used by:** HELLA (hella.csod.com), other Cornerstone career sites.

**How to recognize:** URL contains `<company>.csod.com/ux/ats/careersite`.

- CV parsing does NOT autofill — fill contact fields manually (native setter + input/change events).

- Date fields want **US format MM/DD/YYYY** typed via keyboard (datepicker opens; body.click() closes it); DD.MM.YYYY → "Please enter a valid date".

- Radio groups: `input[name="radio_<uuid>"]`, select by index with .click().

- Conditional radios appear after answering (e.g. internship-duration weeks after "All of the above") — re-scan before Next.

- HELLA sends **no confirmation email** (observed 2026-07-14 and 2026-07-15) — the "Thank You! You have successfully applied" page is the only proof; save confirmation.png.

*Cornerstone OnDemand (csod.com)*

**Used by:** HELLA (hella.csod.com), other large corporates.

- (2026-09-22) HELLA req 18840 (2026-09-22): Earliest-start text field ignored native setter AND fill_input (value shown, still 'required' on Next); what worked: focus + setSelectionRange + Backspace, then per-char Input.dispatchKeyEvent keyDown/keyUp with text, then a Tab key event -> aria-invalid cleared. Transcript of records is REQUIRED on step 1 (attachment_upload_0_*). The 'existing account' modal re-opens on every Next until the step validates - read the errors, not the modal.

## d.vinci

### d.vinci — General

*d.vinci (jobs.<company>.group, `<company>.dvinci.de`)*

**Used by:** Krones (jobs.krones.group), Hertener Stadtwerke, AL-KO. Footer link to `dvinci.de` is the giveaway.

- Apply URL shape: `https://jobs.<company>.group/de/jobs/<id>/apply`, which redirects to `/intro`.

- `/intro` offers Bewerbungsformular / XING-Profil / LinkedIn-Profil / Lebenslauf hochladen / Dropbox. **Go straight to `/de/jobs/<id>/form`** — no account, no login, no captcha.

- Plain server-rendered form (`SYNCHRONIZER_TOKEN` hidden field), so the native-setter + `input`/`change`/`blur` dispatch works for every text field and `<select>`; radios take a plain `.click()`.

- **Select `Land` first.** The form ships five hidden address blocks (`ADDRESS_1..3`, `USA_`, `DEFAULT_`) and only reveals one; for `DE` it is `ADDRESS_1` where `address1`=Adresszusatz, `address2`=**Straße**, plus `zipCode`/`city`.

- Screening questions are `screeningQuestion.<n>` — read each question's text from the ancestor node, the ids are per-tenant.

- `attachmentFile` is `multiple` — one `DOM.setFileInputFiles` call with the whole list attaches all documents. It is an **AJAX input: it clears itself and re-renders each file as a row with an "Entfernen" button**, so verify by filename text on the page, never by `input.files`.

- Submit button is `Absenden`; success = redirect to `/de/jobs/<id>/applied` with "Wir haben die Bewerbung erhalten. Vielen Dank." Confirmation email arrives from `candidate-<hash>@jobs.<company>.group`.

**Tenant notes**

- **Wanzl (`wanzl-karriere.dvinci-hr.com`, 2026-08-31): IMAGE CAPTCHA — prefill and hand off.** Both live
  student roles (31179 Software Development, 31320 Datenanalyse/Data Engineering) end at a required
  `input[name=captcha]` backed by `/simpleCaptcha/captcha`. It is visible (455x38), so it is a real
  bot-check, not a honeypot — verify with `getComputedStyle` before deciding. A submit with it empty
  bounces with that as the ONLY error, and the bounce **keeps every text value AND every attached file**,
  so the parked form is complete and the user only types the captcha. Park both in one sitting.
  Entry point is the employer site, not the aggregator: `wanzl.com/de_DE/karriere/Jobs` links straight to
  `wanzl-karriere.dvinci-hr.com/de/jobs/<id>/...`; the XING card's softgarden `jobdb ... /click?jp=<id>`
  link is **stale and resolves to an unrelated HENSOLDT job**.

- **Hertener Stadtwerke (2026-07-24):** guest flow `/de/jobs/<id>/apply` → "Bewerbungsformular ausfüllen" → `/form`. NO captcha on this tenant (unlike AL-KO). Country-dependent address blocks (fill ADDRESS_1_* for DE). Required beyond basics: `earliestStartingDate` (TT.MM.JJJJ), **`attachmentFile` = "Vollständige Bewerbungsunterlagen*"** (one merged PDF; pypdf CV+Transcript+Immatriculation). POST bounce ("Das Formular enthält Fehler") keeps text values but **wipes the file input** — re-attach on every retry. Success URL ends `/applied` ("Wir haben die Bewerbung erhalten").

- **CDP session trap: after multiple new_tab/goto_url cycles, `js()` reads can silently target a DIFFERENT tab** — the Hertener submit had actually succeeded (`/applied`) while `js()` kept returning the old form. When results look stale or nodeIds go missing, run `list_tabs()` and check the target tab's URL before concluding failure.

## easyhr

### easyhr — General

*easyhr (jobboard.easyhr.io)*

Employer pages embed it as an **iframe** — read `iframe.src` off the company career page and navigate to it directly. Element-UI/Vue form whose inputs have **no name and no id**: assign temp ids in JS (`document.querySelectorAll('input,textarea').forEach((e,i)=>e.id='f'+i)`), then `fill_input('#fN', …)`. Field order: Anrede, Vorname, Nachname, E-Mail, Telefon, Straße, PLZ, Wohnort, then two textareas (Stunden/Woche*, nächstmöglicher Eintrittstermin*).

- Anrede is an `el-select`: coordinate-click `input.el-input__inner[0]`, then coordinate-click the matching `.el-select-dropdown__item` (Divers / Herr / Frau).

- Consent is an `el-switch`: coordinate-click `.el-switch`, verify `.el-switch__input.checked === true`.

- One CV slot; `input[type=file]` takes CDP `setFileInputFiles` and the filename then renders in the page ("Name / löschen" row).

- Submit = coordinate-click "Bewerbung absenden" → `/thankyou/<uuid>` "Vielen Dank für Ihre Bewerbung!"; employer sends its own Empfangsbestätigung.

- **Careful with umlauts in JS selectors**: matching `x.placeholder==='auswählen'` throws a SyntaxError through the heredoc — match by index or ASCII substring instead.

## Eightfold

### Eightfold — General

- (2026-09-23) THE fix for Eightfold comboboxes (input-N, role=combobox, aria-controls=list-N): click_at_xy and JS .click() both no-op on the option, and ArrowDown+Enter only sometimes commits. What works every time is a RAW CDP mouse sequence with an explicit mouseMoved first: Input.dispatchMouseEvent mouseMoved -> mousePressed(clickCount=1,buttons=1) -> mouseReleased, on the field to open it and again on the button[role=option]. After that the input's .value really does read back the chosen label, so verify by read-back. Also: these fields are NOT readOnly on every tenant - a Space keypress typed two spaces into one instead of activating the highlighted option. Selecting an option can REVEAL a dependent required question that the first submit then rejects (Telekom: 'What type of internship is it?' = Other revealed 'What does it refer to?'), so budget one extra submit round. Verified on jobs.infineon.com and growthhub.telekom.com.

## Empfehlungsbund (EBMS)

### Empfehlungsbund (EBMS) — General

*Empfehlungsbund BMS / EBMS (`bms.empfehlungsbund.de`) — neocx and other members*

2026-08-30 — Guest form, no account, converts unaided. Entry: the employer page's "Join now" →
`bms.empfehlungsbund.de/bewerbungen/start/<company>/<reqcode>` → redirects to `/<uuid>/profile`.

- The landing page is the **Express-Bewerbung** (one CV, fields auto-extracted). Click **"Vollständiges
  Bewerbungsformular verwenden"** for the full form (adds `?skip=1`).

- Fields (native setter + input/change all stick): `job_application_start_form[salutation]` radio
  (`value=male` = Herr), `[first_name]`, `[last_name]`, `[telephone]`, `[email]`, `[country_code]` select,
  `[postcode]`, `[city]`, `[street]`, and a **required** `[applicant_comment]` textarea — paste a short
  motivation there; the uploaded Anschreiben does not satisfy it. `[employee_referral]` and a visible
  `url` field are optional. `[datenschutz]` checkbox is required, `[transfer_sharing_allowed]` is not.

- **One file input, not `multiple`** — upload the CV, then the Anschreiben in a *separate* harness call;
  both then list by filename in the page text.

- Flow: **Weiter & Prüfen** → `/questions` (employer Kurzfragen as radios whose `value` is a JSON blob
  containing `"isCorrect":true` for the answer the employer wants) → `/confirm` → **Jetzt bewerben** →
  `/finish` "Ihre Bewerbung wurde versandt!".

- Trap: the final button is a `<button>` with **no `type` attribute**, so `button[type=submit]` returns
  null even though `.type` reads "submit" — select it by its text instead.

- Confirms by email from `widget+…@mail.bms.empfehlungsbund.de` ("… wurde übermittelt").

## Factorial

### Factorial — General

*Factorial HR (lautmaler.factorialhr.de and similar <company>.factorialhr.de)*

Guest apply form reached via StepStone phantom -> "Unternehmenswebsite". Plain form (React-ish): fields first_name/last_name/phone_prefix(select)/phone/email/personal_url/cover_letter(textarea, optional)/cv(file input name="cv", REQUIRED)/photo(optional)/terms_of_service(privacy checkbox)/consent_to_talent_pool(marketing, leave unchecked). Native-setter fills work; `upload_file('[name="cv"]', path)` works; cover_letter via fill_input handles umlauts. A FACTORIAL cookie banner appears at the bottom (Cookies verwalten/ablehnen/akzeptieren) -> click "Cookies ablehnen" (privacy) which shifts layout, so RE-LOCATE the submit button ("Meine Bewerbung senden") after declining before clicking. Proof: URL -> /<id>/thanks.

## finest-jobs

### finest-jobs — General

*finest-jobs application engine (`jobs.mvtec.com`, `karriere.glendimplex.de`, `jobs.oke.de`) — 2026-09-10/11, 3 submitted*

One engine behind several employer career sites; the job page is `…-de-j<NNN>.html`, the form is the same
URL with **`-f<NNN>.html`** ("Jetzt bewerben" just links to it).

- Fields are `bewerbung_form[...]` with a parallel hidden `felder[...]`: `gender`, `vorname`, `nachname`,
  `strasse`, `plz`, `ort`, `country`, `geburtsdatum`, `telefon`, `mail`, `schulabschluss`,
  `berufsausbildung_o_sb`, `erfahrung_pref_inJ`, `eintrittsdatum`, `gehaltswunsch`, `wie_gefunden`, plus
  per-tenant `freifeldN_txt` / `vordef_bew_feld_NNN` (read their labels by walking up to the first parent
  with text — they differ per employer: Kündigungsfrist, PC-Kenntnisse, Umzugsbereitschaft, Studiengang).

- **Select option VALUES are per-tenant hashes** (`VORGABEWERT_…`, `TA_…`). Copying a value from another
  tenant, or truncating it in a debug dump, silently selects nothing. Always match on `option.text`.

- Native setter + `input`/`change` events fills the text fields reliably.

- File inputs: `foto`, `anschreiben`, `lebenslauf`, `anlage1/3/5` — `upload_file` works on all of them.
  Uploading the CV also auto-fills a `cv_image.jpg` into the photo slot on some tenants (harmless).

- **`agbs_check` is a 1px checkbox** — click its `<label for=agb_checkbox>` (x+20, mid-height), not the box.

- **`website` is a visible text input, not a honeypot** on these tenants; leaving it empty is fine.

- Submit is an `<a>` labelled **"Senden"** (MVTec: "Bewerbung absenden"). A cookie banner can sit on top —
  `elementFromPoint` returns the banner; click "Ablehnen" first, then re-measure.

- **Validation errors appear inline in the page text**: "Bitte fügen Sie Ihrer Bewerbung Anlagen bei. Die
  markierten Felder sind Pflichtfelder." — on OKE the required slot was **Anschreiben**, not Lebenslauf.

- Success text: "Bewerbung abgeschlossen / Vielen Dank für Ihre Bewerbung" (MVTec, OKE) or
  "die Übermittlung Ihrer Bewerbungsdaten war erfolgreich" (Glen Dimplex). Employer mail within ~10 min.

- (2026-09-10) **finest-jobs forms (`karriere.<company>.de`, `jobs.<company>.de`, `jobs.mvtec.com`) are one engine.**
  Field names are identical (`bewerbung_form[...]`), option VALUES are long per-tenant hashes - select by
  option **text**, never by a copied value. The `agbs_check` box is 1px wide: click its `<label>`. The
  "Anschreiben / Komplette Unterlagen" slot can be **required** (OKE) even though the CV slot is not.

## Glassdoor

### Glassdoor — General

*Glassdoor*

**Used by:** Glassdoor has its own application system and also redirects to company pages.

**How to recognize:** URL contains `glassdoor.com`, `glassdoor.de`.

## Greenhouse

### Greenhouse — General

*Greenhouse*

**Used by:** Many tech companies and startups: Stripe, Cloudflare, GitLab, Datadog, Figma, Notion, Toast, Celonis, Personio, many Berlin/Munich startups.

**How to recognize:** URL contains `boards.greenhouse.io`, `jobs.lever.co` (different — see Lever), or the apply form is a clean single-page layout hosted on a subdomain.

*Common Quirks*

- Greenhouse forms are generally straightforward — single page, no tabs.

- Custom questions appear at the bottom of the form.

- Some Greenhouse forms have a **"Are you legally authorized to work in [country]?"** question — answer truthfully based on resume facts.

- EEOC/diversity questions (gender, ethnicity, veteran status) — select **"I choose not to self-identify"** or **"Prefer not to say"** for all.

- **Embedded boards (`#grnhse_iframe` on company site, trivago pattern):** react-select combos IGNORE synthetic JS events, and React wipes native-setter values from text inputs on re-render (textareas survive). Fill EVERYTHING with trusted input: compute absolute coords (iframe rect + element rect), `window.scrollTo` so the element is in-viewport, `click_at_xy`, `type_text`. For selects: click control → options render in `div[class*="menu"]` (scope queries there — `[role=option]` alone matches the phone widget's country list) → click the option element at its coords; multi-selects don't filter on typing — scrollIntoView the option inside the menu, then click. The "Country*" field displays its chip as the dial code ("+49" = Germany).

- **Cookie walls on the host page** (Usercentrics `#usercentrics-root`) render in shadow DOM and silently eat clicks — dismiss via `shadowRoot.querySelector` ("Essential cookies only") before any coordinate clicking.

- **Email verification gate:** after Submit, Greenhouse may demand an 8-char security code sent to the application email ("resubmit after entering"). Boxes are `#security-input-0..7`, maxLength 1 — type ONE character per box (click box → type char); a single type_text only lands the first char. Then click Submit again. Success text: "Congrats! You've successfully applied!".

- 2026-08-24 (Isar Aerospace, `job-boards.eu.greenhouse.io`) — **hosted board = react-select everywhere; `fill_input` and `type_text` both fail, but the NATIVE SETTER works for the plain text inputs** (`first_name`/`last_name`/`email`/salary) and persists across re-renders. `upload_file('#resume'|'#cover_letter', path)` works directly.

- 2026-08-24 — **`window.scrollTo` / `scrollIntoView` are inert on this board; only the CDP wheel (`scroll(x, y, dy=...)`) moves it.** Write a `bring()` helper that wheels until `getBoundingClientRect().y` sits ~280px from the top, then coordinate-click. Everything below the fold is unreachable otherwise.

- 2026-08-24 — **react-select recipe that works:** coordinate-click the input → `type_text` a filter → the options render as `#react-select-<name>-option-<N>` (for multi-selects the name KEEPS its brackets, e.g. `react-select-question_123[]-option-80`) → coordinate-click the option element. `press_key("Enter")` on the highlighted option also commits. Clearing needs `End` + ~40×`Backspace`; a short burst leaves junk like `GeGermrm`. Country renders its committed value as the dial code (`+49` = Germany).

- 2026-08-24 — **The 8-char email gate is invisible until you look for it.** After Submit the page silently scrolls to top, the button goes `btn__disabled`, and NO success or error text appears — it looks like a hung submit. `document.querySelector('#security-input-0')` returning non-null is the tell. The code arrives from `no-reply@eu.greenhouse-mail.io`, subject "Security code for your application to <Company>". Type ONE character per box (click box → `type_text(ch)`), then click Submit again → "Thank you for submitting your application."

- 2026-08-30 (Engelhart, `job-boards.greenhouse.io`) — **the reliable react-select recipe is CDP, not typing.**
  `type_text` char-by-char interleaves with the widget's own re-render and produces junk ("GeGermrm",
  "<your city>stadt"), and `press_key("Backspace")` x60 clears only a few characters. What works every time:
  coordinate-click the control → `Input.dispatchKeyEvent` **Ctrl+A** (`modifiers=2, code="KeyA"`) → `Delete` →
  **`Input.insertText`** → read the options → coordinate-click the chosen one. After commit the input's `.value`
  reads **empty** (the chip lives in a sibling) — verify by the container's `innerText`, never by `.value`.

- 2026-08-30 — **match options EXACTLY, not by substring.** Filtering the school list for "Other" and taking the
  first `includes()` hit selected *Christian Brothers University* ("Br**other**s"), and "Hochschu" selected RWTH
  Aachen. Greenhouse's school list has no <your university> — the correct answer is the literal option `Other`.

- 2026-08-24 (KINEXON, embedded `iframe#grnhse_iframe` on kinexon.com) — **drive the embed through its own CDP target, not coordinate math on the host page.** `tid = iframe_target("greenhouse.io/embed/job_app")` then `js(expr, target_id=tid)` reads and native-setter-fills everything inside. For uploads, attach a session (`cdp("Target.attachToTarget", targetId=tid, flatten=True)["sessionId"]`), collect the inputs into `window.__fi`, then `Runtime.evaluate` + `DOM.setFileInputFiles(objectId=..., session_id=sid)`.

- 2026-08-24 — **Coordinate clicks into the embed need iframe origin + element rect**: viewport coords = `iframe.getBoundingClientRect()` (host frame) + `element.getBoundingClientRect()` (iframe frame). Wheel-scroll the HOST page to bring the sum into view. Needed for react-select options and the security-code boxes.

- 2026-08-24 — **A German-localised embed lists countries in German**: filtering the Country combobox with "Germany" returns "No options"; the match is **"Deutschland +49"**. Check the option language before concluding a combobox is broken.

- 2026-08-24 — The 8-char email gate fires here too, and the KINEXON privacy question is a one-option react-select ("Acknowledge/Confirm") that is required.

- 2026-09-06 (trivago, embedded `#grnhse_iframe` on careers.trivago.com) - **commit react-selects with the
  KEYBOARD, not by clicking the option.** Coordinate-clicking an option computed as
  `iframe.getBoundingClientRect() + option.getBoundingClientRect()` hit-tests as `IFRAME` (which looks
  correct) but commits nothing: four required selects silently stayed on "Select..." and only a screenshot
  caught it - `.value` reads empty for a committed react-select *and* for an uncommitted one, so it can
  never tell them apart. What works every time: coordinate-click the control -> `Input.insertText(filter)`
  -> **`ArrowDown` -> `Enter`**. Verify by walking up from the input to the first ancestor whose
  `innerText` is non-empty and not "Select..."; committed multi-selects render as
  `option X, selected.` followed by the chip list. Note the same coordinate math *does* work for the
  **Submit application** button - it is the react-select menu specifically that ignores it.

- 2026-09-06 - the iframe's fields are keyed by **`id`, not `name`** (`e.name` is empty on every input
  except `g-recaptcha-response`), so `[name=...]` selectors match nothing and a `querySelectorAll` dump
  reads as though the form vanished. Multi-select ids keep their brackets (`question_...002[]`) - select
  them with `document.querySelector('[id="..."]')`.

- 2026-09-06 - the host page scrolls, the iframe does not (`iframe.height === body.scrollHeight`, 5298px).
  To bring a field into view: `window.scrollBy(0, iframe.getBoundingClientRect().y + el.y - 400)` on the
  HOST, then re-read both rects. `window.scrollTo` works here (unlike the hosted job-boards).
  Uploads: attach a session to the iframe target and `DOM.setFileInputFiles` - worked first try for both
  `#resume` and the extra "additional documents" slot; verify by filename in the iframe's `innerText`.

- 2026-09-06 - trivago's Greenhouse did **not** fire the 8-char email code: success text was
  "Congrats! You have successfully applied!" and `#security-input-0` was null. Do not assume the gate.

- 2026-09-10 (Isar Aerospace, `job-boards.eu.greenhouse.io`, submitted) - **the 8-char email gate did
  NOT fire this time**: after Submit the page went straight to `/confirmation` with "Thank you for
  submitting your application." and `#security-input-0` was null. Same board, same tenant as the
  2026-08-24 run that did fire it - so test for the gate, never assume it either way.

- 2026-09-10 - **the CDP wheel's sign**: `scroll(x, y, dy=NEGATIVE)` scrolls **UP** (scrollY
  decreases, the element's `rect.top` increases). To bring an element with `rect.top === y` to ~300px
  the delta is `dy = y - 300`. The inverted formula moves the field further off-screen and a `bring()`
  loop then times out with the element still at y = -1054.

- 2026-09-10 - answers that worked on this tenant: Country combobox commits as the dial-code chip
  (`+49`), citizenship / country-of-birth are multi-selects that filter cleanly on "India", the
  disability question's neutral option is literally **`No selection`**, and "How did you hear about
  us?" offers **`Other job portal`** (the right answer for an arbeitnow-sourced application).

- 2026-08-22 — **Greenhouse stays a normal channel — keep applying there.** the user dropped the Raisin and SumUp forms that day ("not applying there"), but confirmed straight after that he has no issue with Greenhouse itself and only meant those two, that day. Do not turn a one-off decline into a portal filter; the mechanics note below is the useful part, and the handoff should simply be surfaced the moment the code is sent.

- 2026-08-22 — **Greenhouse now ends every application with an emailed 8-character "confirm you're a human" code.** Hit on both Raisin and SumUp: the whole form fills and uploads fine, then Submit reveals a Security-code box fed by an e-mail to the user. That is bot-detection, so the agent must stop there. **Rule: on a Greenhouse-hosted form, expect a handoff at the very end — tell the user the same day and keep the tab alive, because the filled form dies with it.** Related: keep each such job in its OWN tab (`new_tab`), otherwise the next job's `goto_url` destroys the parked form.

- (2026-09-12) **Greenhouse: the field labelled "Country*" next to the phone is intl-tel-input's country picker.**
  Committing its first option set +1 (US) and silently reformatted the phone to `(575) 978-1214`. Do not
  touch it - native-set the phone to `+49 1575 9781214` and the widget re-detects Germany on its own.

- (2026-09-18) The emailed 8-char security code expires (a code ~1h old was rejected as 'Invalid security code' even though every box matched). Clicking Submit again does NOT send a new one; reload the form, refill it and submit to get a fresh code, and tell the user to use the NEWEST message, because Gmail threads the codes together.

- (2026-09-19) The resume upload triggers an async CV parse that WIPES name/email/phone typed in the next few seconds (AutoScout24, Agile Robots 2026-09-19: fields read back empty while later fields stuck). Upload files first, wait ~10 s, then fill - or just re-run safe_fill on the fields whose read-back failed. Also: with invisible reCAPTCHA Enterprise the first Submit click can be swallowed silently; one retry went through.

- (2026-09-25) react-select on job-boards.eu.greenhouse.io does NOT commit from a coordinate click on the option - the click reports ok and the control still reads 'Select...'. What commits every time: focus the hidden input by its question id, clear value, ArrowDown to open, walk the highlight with ArrowDown while comparing aria-activedescendant against the target react-select-<qid>-option-N id, then Enter. Verify by the control container's innerText, never by input.value. Also: do NOT read options from [role=option] - intl-tel-input's phone country list (iti-0__item-*) matches it and floods 200+ countries; scope to [id^=react-select-<qid>-option]. NavVis submitted with NO 8-char email gate and redirects to <joburl>/confirmation - so the emailed-code handoff is per-tenant, not Greenhouse-wide; poll location.href for /confirmation as well as the success text.

## HiBob

### HiBob — General

*HiBob careers (`<company>.careers.hibob.com`) — Uppy uploader is a CDP DEAD END (2026-09-09)*

**How to recognize:** apply URL `https://<tenant>.careers.hibob.com/jobs/<uuid>/apply`; the page
credits "Bob Recruiting" in the privacy line.

- Guest form, no login. Text fields are addressable by `[id='/candidate/firstName']` (the id really
  does contain slashes — use an attribute selector, not `#`), plus `lastName` / `email` / `phone`,
  and an `initialConsent` checkbox.

- Upload slots (Lebenslauf / Anschreiben / Zeugnisse / Studienbescheinigung) are **Uppy Dashboard**
  modals opened by a "Datei hinzufügen" button; `input.uppy-Dashboard-input` exists only while the
  modal is open.

- **Every CDP route into that uploader failed at MURTFELDT 2026-09-09:** `DOM.setFileInputFiles`
  makes Uppy read size 0 and reject with *"This file is smaller than the allowed size of 1 B"*; a
  real `File` built in-page from streamed base64 and pushed onto the input via
  `Object.defineProperty(inp,'files',...)` + `change` stages briefly, then the modal re-renders
  empty; a synthetic `DragEvent` drop carrying the same 815 KB `File` on `.uppy-Dashboard-inner` is
  ignored.

- Lebenslauf* and Zeugnisse* are both required, so **fill the contact block, then NeedsUser** —
  the user picks the files. Do not spend more attempts on it.

## HR4YOU

### HR4YOU — General

*HR4YOU (<company>.hr4you.org) — OSCAR, 2026-08-23*

Guest flow, no login, two steps:

1. `applicantRegisterCvAnalyzerGenerator/upload/<id>` — a single `input[name="uploads[]"]`, then **Absenden** (or **Überspringen**). The CV is parsed to prefill the next page.

2. The main form: `vorname`, `nachname`, `geburtsdatum`, `plz`, `ort`, `handy`, `reg_mail`, a second `uploads[]` for the Lebenslauf, `applyprivacy` (required) + `applyprivacyoptional` (leave off), submit `ApplicationFormSubmit` ("Bewerbung senden"). Success = "Wir danken Ihnen für die Bewerbung."

**The CV parser mangles fields** — it produced `nachname = "<Name> KI"` (job-title words bleeding into the surname) and a phone as `(+49) 1575978121`. Re-derive every prefilled value from `resume.md` before submitting. Anrede is a custom `multiselect-search` combobox with no named input; it came out already set to "männlich".

## HRlab

### HRlab — General

*HRlab (app.hrlab.de/en/jobs/<Company>/<id>/apply)*

Guest apply form via StepStone phantom -> Unternehmenswebsite. Field names candidature[first_name]/[last_name]/[private_mail] (NOT private_email!)/[private_phone]/[street]/[house_number]/[postcode]/[city]/[available_from](date)/[salary_expectation](number, p.m. EUR)/[higher_education](select)/[comments](textarea)/[files][] (file, "Further documents", optional). Honeypot input hp_name_<hash> -> leave empty. Only name/email/phone REQUIRED; no cover letter, no mandatory consent checkbox. Upload via file input id (querySelector 'input[name="candidature[files][]"]' rejects as non-file for upload_file; instead grab input[type=file] and assign an id, then upload_file). Submit button "Send Application" top-right. Proof: URL -> /success "Your application has been successfully recorded."

## HRworks

### HRworks — General

*HRworks*

**Used by:** German SMEs (e.g. WiBU Gruppe, karriere.wibu.care).

**How to recognize:** Footer "bereitgestellt von HRworks GmbH"; form fields have numeric ids like `3-86`.

*Common Quirks*

- Text inputs reject `fill_input`; use the JS native-value-setter + `input`/`change` events (works for all fields incl. date).

- Selects (`Anrede`, `Land`, source) work with plain JS option-set + `change` event.

- **2026-07-24 — file upload SOLVED; the 2026-07-13 "unsolved" verdict below was a SELECTOR bug.** HRworks field ids start with a digit (`1-438`), so `upload_file('#1-438', ...)` fails with CDP `DOM Error while querying` — which looked like the widget hanging. `upload_file('input[id="1-438"]', ...)` works first try. Verify by the **filename appearing in the page text** (`input.files` stays 0 — the blueimp widget consumes it); upload one file per call and all files list under "Bewerbungsunterlagen". Text inputs and selects take the JS native-setter (select values are ids like `1-64`, not labels — read `option.value`). "Bewerbung absenden" opens a **JS confirm dialog** ("Bewerbung absenden?") listing the e-mail; click **Ja** — only then does the page change to "Wir haben Deine Bewerbungsdaten erhalten". Zuken E3 submitted this way with Lebenslauf + Anschreiben + Transcript.

- 2026-08-30 (WiBU submitted, karriere.wibu.care) — confirms the 2026-07-24 selector fix; the 2026-07-13
  "widget hangs" verdict was the `#19-488` bug and nothing else. Two more traps on this tenant:
  **"Wunsch-Jahresgehalt" is NUMERIC-ONLY** — a text answer is silently mangled ("ca. 15 EUR/Stunde…" became
  `-151520`); enter a bare number (12000) and explain the hourly rate in the `Bemerkung` textarea. And
  **"Bewerbung absenden" opens a Bootstrap modal (`.modal.in`) with Ja/Nein, not a JS `confirm()`** — overriding
  `window.confirm` does nothing; dispatch pointer events on the modal's **Ja**. Success:
  "Wir haben Ihre Bewerbungsdaten erhalten"; receipt from `noreply@hrworks.de`.

- **Superseded (2026-07-13, WiBU):** blueimp jQuery-File-Upload widget with `autoUpload:false`; its per-file process pipeline (loadImage → validate) hangs forever (`_processingQueue` stays pending) for files injected via CDP `setFileInputFiles`, DataTransfer-constructed Files, or the `fileupload('add')` API — no file row ever renders, "Bewerbung absenden" would submit without documents. Kontaktperson "E-Mail anzeigen" reveal also hangs ("Laden..."). → Prep the package and mark `NeedsUser` for a manual 3-minute apply.

## iCIMS

### iCIMS — General

*Common Quirks*

- iCIMS forms can be multi-page with extensive questions.

- Some fields auto-populate from a parsed resume — verify accuracy.

## Indeed

### Indeed — General

*Indeed*

**Used by:** Indeed is a job aggregator with its own application system.

**How to recognize:** URL contains `indeed.com`, `indeed.de`, `de.indeed.com`.

*Common Quirks*

- Indeed has its own resume and profile system — some applications pre-fill from the Indeed profile.

- "Apply on company site" listings redirect to external career pages — follow the target ATS.

- Indeed may show a CAPTCHA — mark `blocked_captcha` if encountered.

- **Indeed Apply (smartapply.indeed.com):** steps are location → resume selection (profile CV reusable) → relevant experience → review. A reCAPTCHA "Ich bin kein Roboter" checkbox appears at the very end and disables "Bewerbung absenden" — fill everything, leave the tab open at review, and hand over to the user for the final click.

- (2026-09-10) **Indeed is a fine DISCOVERY source and a bad apply channel.** Three of today's finds (Glen Dimplex,
  CHASKI, OKE) came from `de.indeed.com/jobs?q=…&fromage=14&sort=date`, and each was then applied to on
  the employer's own form. Indeed Apply itself still ends in a reCAPTCHA.

## Jobvite

### Jobvite — General

*Jobvite*

**Used by:** Various mid-to-large companies.

**How to recognize:** URL contains `jobs.jobvite.com`.

## JOIN

### JOIN — General

*JOIN*

**Used by:** Many European startups and SMEs.

**How to recognize:** URL contains `join.com`.

*Common Quirks*

- JOIN sometimes shows a "Passt hervorragend" or fit badge based on a previously uploaded profile — this is informational only.

- Some postings are "inline" (quick-apply via "Ich bin interessiert") while others redirect externally.

- **Wizard date picker (frühestmögliches Startdatum):** day cells are `<button aria-label="Choose ...">` on first render but plain `<td>` after "Switch to next month" — JS `.click()` on them no-ops; coordinate-click the `<td>` center and verify `aria-selected="true"` before "Weiter". The question can be skipped silently (Weiter advances with nothing selected), so always verify.

- 2026-08-24 — **On JOIN I clicked "Weiter" straight through two screening steps and only noticed at the review page.** The howtologin note already warned that Weiter advances with nothing selected; I clicked it in a loop without reading each step. The questions were a start-date picker and an annual salary field — both would have submitted blank. Rule: in any multi-step wizard, read the step's heading and inspect its inputs BEFORE clicking the next button, never loop blindly. Also: navigating directly to `/apply/question-1` bounces you back to the first step, so recovering means walking the whole wizard again (and re-uploading the Anschreiben).

- (2026-08-29) **JOIN's dashboard (`join.com/talent/applications`) is a dedupe source the tracker cannot see** — it
  lists every JOIN application with status (Applied N days ago / In Review / Not selected). Check it
  before applying to any JOIN-hosted role; a StepStone route into JOIN hid a live D-LABS application.

*2026-09-10 - answer cards, the silent-skip trap, and back-navigation*

- **Single-choice answer cards commit on a JS `.click()` of the option's own `<p>`, not on a
  coordinate click of the card.** The card container is ~100px tall but the clickable
  `div[role="radio"]` inside it is only ~44px, so a click at the card centre lands outside the
  handler and nothing happens (no error, no advance). `[...document.querySelectorAll('p')]
  .find(p=>p.innerText.trim()==='<Option>').click()` works every time and auto-advances the wizard.

- **The wizard advances past an UNANSWERED question with `Weiter` enabled.** The review page then
  shows the question with the value **"Keine Antwort"**. Always read the review page's
  "Details zur Bewerbung" block and diff every question before clicking Bestaetigen.

- **Never navigate back to `/apply/question-N` directly** - it bounces to `/apply/cv` AND drops an
  already-uploaded Anschreiben. To fix a missed answer, walk forward with `Weiter` from wherever it
  lands, re-uploading the cover letter on the way.

- The **date picker** is the same chakra widget as elsewhere: a `chakra-progress__range` progress bar
  overlays the cell centre, so scroll ~120px first and click the inner
  `[data-part="table-cell-trigger"]`, then assert `aria-selected === "true"`.

- Screening questions seen in one day: earliest start date, annual salary expectation (`type=number`),
  Vollzeit/Teilzeit, current city, and **"Wie gut sind Ihre Deutschkenntnisse?"** with the rungs
  Keine / Grundkenntnisse / Gute Kenntnisse / Fliessend / Verhandlungssicher / Muttersprache -
  B1 maps to **Grundkenntnisse**.

- (2026-09-10) **JOIN sends a confirmation mail per application - treat a missing one as a signal.** Four of the
  five JOIN submits mailed from `no-reply@msg.join.com` within minutes; 1KOMMA5 did not, despite a
  clean `/apply/success`. Logged Submitted with a WATCH note rather than silently trusting the page.

- (2026-09-10) **Cover letters are the gate on some JOIN and Personio forms, not a nicety.** MESKRU and Ramp106
  both held `Weiter`/`Bewerbung senden` disabled until an Anschreiben PDF was attached. The German
  Kostal template took 240 and 243 words onto one page here - above the 235-word figure noted on
  2026-09-09, so check `len(PdfReader(pdf).pages)` rather than trusting the word count either way.

- (2026-09-12) **JOIN's silent-skip trap hit 3 of 3 questions across two jobs.** Continue/Weiter advances past an
  unanswered question; the review page is the only place it shows ("No answer"/"Keine Antwort"). The review's
  own "Edit"/"Bearbeiten" is a `<p>` inside `a.chakra-link` with no href - a JS `.click()` on that `<p>` opens
  `question-N?backTo=review` and returns straight to review, which is safe (direct URL navigation is not).

- (2026-09-14) **JOIN's review page pre-ticks "use this CV by default"** - uploading a variant CV silently changes the user's
  JOIN default. Untick it unless the new CV should become the default.

- (2026-09-24) Two things on the JOIN wizard. (1) Step 1 can PRE-ATTACH the CV from the JOIN profile (heading "Bestaetige deinen Lebenslauf") with NO file input on the page - click "Datei entfernen" first, which then reveals the file inputs, or the profile CV gets sent instead of the tailored one. Verify by reading the rendered preview for the tailored headline. (2) The start-date calendar is an Ark/Zag widget (td with data-scope/data-part/data-value): scrollIntoView CHANGES the cell rect, so a coordinate captured before the scroll misses silently and leaves aria-selected=false. Re-read the rect AFTER scrolling, then dispatch mousePressed+mouseReleased on the cells inner div and verify aria-selected=true plus the data-value date.

## Kenjo

### Kenjo — General

*Kenjo*

**Used by:** Some companies (e.g., Charles Real Estate via StepStone redirect).

**How to recognize:** URL contains `kenjo.io` or Kenjo branding on the form.

*kenjo (kenjo.io ATS) — guest form, reached via StepStone phantom → Unternehmenswebsite*

- Employer boards like `<company>.kenjo.io/<slug>` open a job page with an **"Apply now"** button that reveals the actual form (`/apply`). Fields are Angular-Material `mat-input-orgos-career-siteN` (native-setter + input/change/blur works). Required: First/Last/Email/Phone/Notice period/Salary(annual)+currency; address fields optional; a required consent checkbox.

- Two required **mat-selects** ("How did you become aware", "Salary currency") do NOT accept a JS value set — coordinate-click the mat-select to open the overlay, then click the `mat-option` (e.g. "Stepstone / Totaljobs", "EUR"). Submit stays disabled until BOTH are set (check `mat-form-field.ng-invalid`).

- File upload: `DOM.setFileInputFiles` on the hidden `input[type=file]` — Angular consumes the file and clears `input.files` (shows 0) but the filename appears in body text and **Submit enables**; that's the real success signal, don't re-upload. "Submit application" → "Thank you. Your application has been received." Confirmation mail from `career@<company>.com`.

## Lever

### Lever — General

*Lever*

**Used by:** Many tech startups and mid-size companies.

**How to recognize:** URL contains `jobs.lever.co`.

*Common Quirks*

- Lever forms are very minimal — usually one page.

- Some Lever postings have a "Submit your application via email" note — follow the email-only application workflow in that case.

## LinkedIn

### LinkedIn — General

*LinkedIn (as source)*

**How to recognize:** posting refs `linkedin_<10-digit-id>`.

- The logged-in job page SPA does NOT render the description for automation (innerText stays ~2 kB, no "About the job") and `h1`/description selectors return nothing — don't fight it.

- **Full posting text: fetch the guest API from any linkedin.com tab**: `fetch('https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<id>')` → 28 kB HTML fragment. Parse it **in Python with regex** (`top-card-layout__title`, `topcard__org-name-link`, `posted-time-ago__text`, `show-more-less-html__markup`). DOMParser is unusable on linkedin.com (Trusted Types CSP → empty document), and innerText/textContent on the parsed doc return ''.

- **External apply URL:** the job page "Apply" control is an `<a>`; its href is `linkedin.com/safety/go/?url=<encoded target>` — read the `url` param, no click/window.open interception needed.

- Search-result cards are virtualized: only ~7 hydrate per viewport; scroll the results list container stepwise and re-extract. Date-sort (`sortBy=DD`) returns mostly irrelevant roles — keep relevance sort and filter titles in-script.

- **Guest search API** (works from any linkedin.com tab, no login): `fetch('https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<kw>&location=Germany&f_TPR=r604800&start=0')` → `<li>` cards with `data-entity-urn`, `base-search-card__title/subtitle`, `job-search-card__location`, `<time datetime>`. ~25 cards/page; regex-parse in Python.

- **EasyApply modal (confirmed Corbado 2026-07-16):** the modal is position:fixed → `offsetParent` is null for ALL its elements; test visibility with `getClientRects().length` instead. Yes/No radios have no associated `label[for]` and empty `.labels` — click the `input[type=radio]` directly (`radios[i].click()`); readback of `.checked` can lag but React state updates (verify on the Review step instead). Selects work with plain `.value=` + change event. Stored resumes appear as radio cards; the previously used CV is pre-selected. Confirmation = "Your application was sent to <Company>!" modal; the email went to the LinkedIn account address (`.kv`) at the time — since 2026-07-24 the account email is the primary Gmail, so it is checkable.

*LinkedIn*

**Used by:** LinkedIn job applications (Easy Apply and external).

**How to recognize:** URL contains `linkedin.com`.

*Application Types*

- **Easy Apply:** Multi-step modal within LinkedIn. Fill each step and click "Next" / "Submit".

*Common Quirks*

- LinkedIn Easy Apply may pre-fill fields from the profile — review each pre-filled field.

- Some Easy Apply forms ask for a resume upload even though the profile exists — always upload the package-local CV.

- LinkedIn aggressively rate-limits automated interactions — if blocked, stop and mark `blocked_rate_limit`.

- **LinkedIn** — the guest API is useless for thesis terms (fuzzy relevance returns junk); the
  logged-in `/jobs/search/` UI works. The EasyApply pool is ~90% senior/sales noise, but EasyApply
  itself submits reliably because it reuses the stored profile CV — no upload needed.

*Easy Apply modal mechanics (verified 2026-07-17, Quistor/Workable-backed)*

- Browser viewport is ~551px tall; the modal's Next/Review/Submit footer button sits BELOW the fold — `scrollIntoView({block:'center'})` the button, then coordinate-click (JS `.click()` does NOT advance pages). After centering, the button lands at ~(1025,519).

- Page count in modal text: `N/6 pages`. Validation errors only render after a failed Next — re-read the modal after every click.

- Location (city)* is a typeahead: click field, TYPE the city via keyboard, wait ~1.5s, coordinate-click the first suggestion (role=option). JS value-set alone does not commit.

- Resume page: stored profile resumes are listed newest-first and radio[0] is preselected — no file upload needed if the stored CV is current.

- Cover letter can be a required TEXTAREA (Workable-backed postings) — paste the letter body, native setter + input event works.

- GDPR consent on the Additional Questions page = first checkbox in the modal (second is the job-alert toggle — leave it). Click its label by coordinates.

- Success = "Your application was sent to <company>!" overlay; the job page's Applied badge may lag. **Check that the LinkedIn account email is your `JOBAGENT_EMAIL`** — if it is some other address, EasyApply confirmations never reach the batch-end check and the overlay is your only proof.

- (2026-09-02) **LinkedIn's logged-in UI needs the window un-wedged before it renders at all.** `document.hidden === true`
  left the Ember app stuck in `app-loader--default`: 1.35 MB of HTML, `document.body.innerText.length === 0`,
  `querySelectorAll('a').length === 0`. It looks exactly like a logged-out wall. The minimize->restore
  `Browser.setWindowBounds` cycle plus a reload fixed it instantly. **Check `document.hidden` before concluding
  LinkedIn is not signed in.**

*LinkedIn Easy Apply — 2026-09-10 (THRYVE + TCS submitted): the modal is an IFRAME*

- `document.querySelectorAll("select")` returns only the page-language select; every modal field lives in
  an **iframe**, so DOM-driven filling is impossible. Coordinate clicks pass through — drive by screenshot.

- **"Submit application" sits below a 551px viewport and the modal ignores `window.scrollTo` and mouse
  wheels.** `cdp("Emulation.setDeviceMetricsOverride", width=1366, height=1300, deviceScaleFactor=1,
  mobile=False)` reveals the whole modal; clear it afterwards.

- Dropdowns: clicking the visible option row does nothing (the answer stays "Select an option" and the
  step reports "Please enter a valid answer"). Click the control, then `press_key("ArrowDown")` +
  `press_key("Enter")`.

- Attempting `upload_file` inside the modal closes it and pops **"Save this application?"** — its X button
  returns you to the step with everything intact (Discard would delete the draft). There is no exposed
  `input[type=file]`; the stored profile CV is pre-selected and is what goes out.

- Language questions seen: "What is your level of proficiency in German?" (None/Conversational/…) →
  **Conversational** for B1; TCS's German scale was *Gar nicht / Gut / Verhandlungssicher / Muttersprache*
  with no basic rung — answered **Gut** for German (Gar nicht would be false) and
  **Verhandlungssicher** for English.

- Proof of submit: the green "Your application was sent to <Company>!" modal **plus** the job page's
  "Application status: Application submitted". No confirmation mail arrives for either.

- (2026-09-10) **LinkedIn Easy Apply renders inside an IFRAME.** `document.querySelectorAll` finds none of the modal's
  fields (only a stray page-language `<select>`), so drive it by screenshot + `click_at_xy`. Two more
  traps: the **"Submit application" button sits below a 551px viewport** - fix with
  `cdp("Emulation.setDeviceMetricsOverride", width=1366, height=1300)`, not by scrolling, because the
  modal has its own scroll container that ignores `window.scrollTo` and mouse wheels; and **clicking a
  dropdown option row silently does nothing** - open the dropdown, then `ArrowDown` + `Enter`.

- (2026-09-12) **The LinkedIn guest API is still an excellent DISCOVERY source, and it is free.**
  `jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<q>&location=Germany&f_TPR=r604800` returns 10 cards
  per query (8 queries -> 65 unique jobs, 36 student/thesis), and
  `jobs-guest/jobs/api/jobPosting/<id>` returns the full ad, so the German-language screen costs no browser at
  all. It killed 6 of 20 candidates on "sehr gute Deutschkenntnisse" before a single tab was opened.

- (2026-09-14) **The LinkedIn copy is not a language screen, again.** ARAG's LinkedIn text said "Sehr gute Deutschkenntnisse";
  the employer page adds "(mindestens C1-Niveau)". Open the employer page before packaging, every time.

- (2026-09-14) **Resolve LinkedIn apply hosts off the page, cheaply:** aggregator pages (workingstudentjobs.de) carry the raw
  ATS link in their HTML (`curl | grep ashbyhq|personio|...`); freehire slugs like `ThaliaBcherGmbH1` are
  SmartRecruiters company ids that the public API answers. LinkedIn's guest posting HTML has no apply URL.

- (2026-09-14) **LinkedIn copy dropped the C1 line twice more** (ARAG this morning, HDI Cloud AWS now). The employer page is the
  only language screen that counts.

- (2026-09-14) **The logged-in job page exposes the employer route in the Apply button's `href`** (`linkedin.com/safety/go/?url=<encoded ATS URL>`), no click or `window.open` hook needed; the guest `jobPosting/<id>` API hides it (`EASYAPPLY/none`). One `goto_url` + one `js()` per job resolved 11 routes (Workday, SF, Taleo, JOIN, Eightfold, SmartRecruiters via jobster/jobbird).

## Notion Forms

### Notion Forms — General

*Notion Forms (resistant to automation)*

**How to recognize:** apply URL is `<company>.notion.site/…` with "Application form"; fields have placeholder "Your answer".

- **Text/number inputs are controlled and DO NOT register via the native value-setter** — submit keeps flagging "This question is required" even though the DOM shows the value. Fix: focus, clear, then type **real CDP `Input.dispatchKeyEvent` char keystrokes** (same as Ashby number fields). This fixed name/email/etc.

- Dropdowns render as `[role=button]` reading "Your answer" → click, then click `[role=option]`. "Available from" is a react-datepicker (day divs `.react-datepicker__day`). Language-skill selects are also Notion dropdowns, not native.

- **File uploads via CDP `setFileInputFiles` are unreliable**: clicking "Upload" reveals one hidden `input[type=file]`; setting it shows the filename but the field can stay in a pending state (filename shown AND "Upload" button persists) and validation keeps flagging it required, with no way to force the async commit. Confirmed on Clar AI (clar-ai) 2026-07-16: resume + high-school committed, university-transcript would not. **If a required Notion file upload won't commit after 2 tries, fall back to the company's contact email (Clar provided talent@clar.ai) and mark NeedsUser — do not burn the batch on it.**

## onlyfy / Prescreen

### onlyfy / Prescreen — General

*onlyfy (onlyfy.jobs)*

**Used by:** onlyfy one (ex-Prescreen) applicant tracking, e.g. Jungheinrich (`<company>.onlyfy.jobs/application/...`). Reached via StepStone "Ich bin interessiert" → "Hat mit deiner Bewerbung alles geklappt?" → **Unternehmenswebsite** button (navigates same tab).

**How to recognize:** URL host `*.onlyfy.jobs`.

*Application (guest form — no login)*

- Heading "Einfach bewerben". Required: `personal_details[first_name]`, `[last_name]`, `[email]` only. Fill text via `fill_input`.

- CV upload: `input[name="cv[cv]"]` via `upload_file(...)`. Verify the filename chip (with KB/MB size) appears before submitting.

- **Selects are React-controlled** (`personal_details[salutation]`, `finish[application_source]`) — native `select.value=` does NOT register; use the React native-setter: `Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(sel,val)` then dispatch `input`+`change`+`blur`. Anrede options: Herr/Frau/Divers. Jungheinrich source list has no "StepStone" → use "Suchmaschine".

- Optional talent-pool consent checkbox (`finish[extended_data_retention]`) — leave **unchecked** (most privacy-preserving).

- Submit "Bewerbung absenden". **First submit may hang on a "Ihre Bewerbung wird jetzt hochgeladen" cloud overlay that never clears** — reload the apply URL and retry once; the 2nd attempt succeeds. Success page: "**Geschafft! Ihre Bewerbung ist unterwegs**" + a confirmation email from `reply@mail.onlyfy.jobs` (subject "Die Bewerbung ist abgeschlossen").

*onlyfy / Prescreen*

**Used by:** VIVAWEST (vivawest.onlyfy.jobs) and other German companies.

**How to recognize:** URL contains `onlyfy.jobs` or `prescreen.io`, often inside a widget iframe on the company site (the host page body may be empty).

*Flow (no login)*

1. Go directly to `<company>.onlyfy.jobs/application/apply/<id>` — skip the empty host page.

2. Real file inputs: `input[name="questions[cf_XXXX]"]`.

3. Custom radios need `label.click()`.

4. kununu review consent is a required radio — answer "Nein".

5. Submit.

## Oracle Recruiting Cloud

### Oracle Recruiting Cloud — General

*Oracle Recruiting Cloud (ORC, `fa-*.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience`)*

**How to recognize:** apply URL `…/hcmUI/CandidateExperience/<lang>/sites/<site>/job/<id>` and an apply flow at `/apply/email`.

- Flow: "JETZT BEWERBEN" (coordinate-click; the button sits far down the page — `scrollIntoView` first) → `/apply/email` asks only for **email + "Ich stimme den Vertragsbedingungen zu"** checkbox → WEITER → the **whole application form on one page** (`/apply/section/1`). No account/password is created up front.

- Cookie banner: click **"NUR TECHNISCH NOTWENDIGE COOKIES"** first; it re-renders the page and **input ids change** (`primary-email` → `primary-email-0`) — re-query after any re-render, prefer attribute selectors (`input[type=email]`) over ids.

- Text fields take `fill_input` fine. **Date fields (day/month/year triplets: `day-dateOfBirth-11`, `day-<custom>EarliestEntryDate-12`) ignore both fill_input and click+type** — use the native value setter + `input`/`change`/`blur` events. Re-verify them right before submit: an unrelated re-render silently cleared the DOB year once.

- Anrede and the Ja/Nein application questions are **`button[aria-pressed]`**, not radios — `document.querySelectorAll('button[aria-pressed]')` in DOM order = [Frau, Herr, N/A, Ja, Nein, Ja, Nein]; coordinate-click and verify via `aria-pressed`.

- Uploads: `input[type=file]` ids **change after every upload** (`attachment-upload-2/3/4` → `-25`, `-26`); upload one file, re-query, upload the next. Verify by filename text + "Gespeichert" in the page text (Lebenslauf and Anschreiben have separate slots, extra docs go to "Sonstige Dokumente").

- E-signature = `#fullName-5` (type full legal name), then **WEITERLEITEN**.

- **Submit sends a 6-digit email verification code** (`career@<company>.com`, valid 10 min). The pin inputs are `#pin-code-1..6` and auto-advance — typing all 6 into the first field only lands one digit; **click each field and type one digit at a time**. Then VERIFIZIEREN.

- Success: redirect to `/my-profile` showing "Vielen Dank für Ihre Bewerbung" + the role under AKTIVE BEWERBUNGEN with "Beworben am <date>" and status "Wird geprüft".

## Own-site forms

### Own-site forms — General

- (2026-09-24) jobware.net renders no job description at all - both /Studentenjob/<id> and the canonical /job/<slug> return navigation only, so a language and fit screen is impossible there. Do not write the row off: the 'Jetzt bewerben' anchor is a /apply/<token> redirector that lands on the employer's own posting (Salzgitter Flachstahl, 2026-09-24), which carried the full Aufgaben/Profil block and a live ONLINE BEWERBEN control. One goto_url on that anchor is the whole cost.

- (2026-09-25) bewerbermanagement.net (Max Planck institutes and other German public employers) - clean guest form, no login, ids are sequential bjpfg-input-field-<N>. THE WHOLE FORM IS disabled:true until the data-privacy checkbox (bjpfg-input-field-0) is ticked, and set_text returns '' on every field until then with no error - tick the consent FIRST, then fill. File inputs do not exist in the DOM at all: the 'Upload CV' and 'Upload files' buttons each inject one on click (mpf0 = CV-for-autofill which OVERWRITES typed fields, mpf1 = Attachments - use mpf1). The attachment input clears itself after upload, so verify by the filename in the page text. Two-step finish: 'Verify & submit' renders a Summary page, then 'Submit application'. Success: 'Your application was successfully submitted.'

- (2026-09-27) Avature (jobs.siemens-energy.com / Siemens Gamesa) is the first uploader in this project where DOM.setFileInputFiles is NOT enough. input.files reaches 1, input.value shows C:\fakepath\<name>, and the widget even RENDERS the filename under 'Upload your CV' - yet Avature's own validator keeps 'This field is required' and Continue never advances. Tried: plain upload(), upload()+dispatch input/change, Page.setInterceptFileChooserDialog(enabled=true), and clicking the 'Upload your CV' anchor after setting files. None cleared it, so budget a handoff for Avature rather than a 4th attempt. Separate trap on the same site: the page has TWO 'Login' controls - the top-nav <a> at y=40 reloads /jobs/Login and DROPS the folderId (losing the job context); the real one is button[type=submit] inside the form.

## P&I LOGA

### P&I LOGA — General

*P&I LOGA Bewerber-Web (pi-asp.de)*

**Used by:** S-Kreditpartner (sdworxskp.pi-asp.de), other SD Worx/P&I tenants.

**How to recognize:** URL `<tenant>.pi-asp.de/bewerber-web/`, GWT app, fields with ids `LG_FFC_<n>`.

- Guest form, no login. Reached via redirect service (cockpit.as-mediendesign.de jump links from LinkedIn).

- Text fields: native setter + input/change works (salary auto-formats 15000 -> 15.000).

- **Comboboxes are `input.gwt-combo-box-input`** (Anrede/Schwerbehinderung/Quelle): click the input's right edge (coordinate), then click the option's text node. Readback via `.value`.

- **Uploads:** 4 hidden `input[type=file][name=fileUploader]` in label order (Lebenslauf, Anschreiben, Zeugnisse, Sonstiges). CDP setFileInputFiles works; filenames appear as page text.

- **Submit: "JETZT BEWERBEN" ignores JS `.click()` — coordinate-click required** (BeeSite-adjacent GWT behavior). Success = in-place "Vielen Dank für Deine Bewerbung!" panel.

## perbility (mein-check-in.de)

### perbility (mein-check-in.de) — General

*mein-check-in.de / perbility (vr.mein-check-in.de/<company>)*

Reached as a StepStone phantom destination. Traps, in order:

1. The StepStone landing URL carries `?forward=1&openModalFastTrack=true` and hangs forever on "Bitte kurz warten. Weiterleitung erfolgt automatisch." — `form.submit()` and the "hier klicken" link both do nothing. **Fix: navigate to the bare `https://vr.mein-check-in.de/<company>/position-<id>` and JS-click the "Jetzt hier bewerben" anchor** (it routes to `/quest`).

2. Two pages: *Adressangaben* then *Weitere Angaben & Dokumente*, both driven by `[name="next"]`.

3. `fill_input` on a readonly/derived field (`province[country][1][country]`) types into the **previously focused** input instead — a "Deutschland" landed in `birthday_1_birthday`. Read every value back after a fill batch. The date field takes the **native setter** + input/change/blur (`02.07.2000`), not `fill_input`.

4. Uploads: `input[type=file]` ids `requiredfiles_<n>_requiredfiles_uploader` accept CDP `DOM.setFileInputFiles`. Proof is the sibling text input `requiredfiles[n][requiredfiles]` picking up the filename (and "Entfernen" appearing) — the page never prints the filename inline. Slot order = page label order: 1 Anschreiben, 2 Lebenslauf*, 3 Zeugnisse; slot 4 is a hidden "Einverständniserklärung" (minors only).

5. **A failed page-2 validation silently returns you to page 1** and marks only `LI.currentError` in the nav. To find the real culprit, query `.x-form-invalid-icon` and walk up to its field — here it was a required free-text `additionalpersonaldata` ("wie sind Sie auf uns aufmerksam geworden"), not the uploads.

6. Final `Bewerbung abschicken` (an `input[type=button][name=next]`) **ignores JS `.click()`** — use a coordinate click. Success = "Vielen Dank für Ihre Bewerbung." + `noreply@mein-check-in.de` Eingangsbestätigung.

## Personio

### Personio — General

*Personio*

**Used by:** Many German SMEs and mid-size companies, especially Berlin startups.

**How to recognize:** URL contains `<company>.jobs.personio.de` or `<company>.jobs.personio.com`.

*Common Quirks*

- Personio forms are typically in the language of the posting.

- File upload is drag-and-drop or click-to-browse.

- Required "Gehaltsvorstellung" field: enter "15 Euro pro Stunde" (market default for Werkstudent, consistent with observed postings). Optional salary fields: leave blank.

- Language level selects, mapped truthfully: DE B1 → "Gut", EN C1 → "Verhandlungssicher".

- Maximum file size is usually 20 MB.

*Personio (embedded widget on employer site) — dead api.personio.de endpoint*

2026-07-23 (Blickfeld) — Some employer sites embed an old Personio form whose `<form action>` is `https://api.personio.de/recruiting/applicant`. That endpoint is **retired**: submitting returns a JSON 404 (`The endpoint with /recruiting/applicant was not found`) and the application is lost. Recognise it by reading `form.action` before submitting. **Fix: apply on the Personio-hosted board instead** — `https://<company>.jobs.personio.de/job/<jobId>` (the jobId is in the employer page's `job-id=` query param). That board's `?apply` form works normally: `#field-first_name/last_name/email/phone/location/available_from`, `documents.cv` / `documents.cover-letter` / `documents.certificate` / `documents.other` file inputs, and language-proficiency `custom_attribute_*` selects (options are `custom_option_*`, labelled C2/C1/B2/B1/A2/A1). Submit stays disabled until **every** slot marked `*` is filled — Blickfeld required BOTH CV and Cover letter.

*Personio — 2026-07-24 fill-method note*

- Today `fill_input` did NOT stick at all (values empty after CV-upload re-render, all aria-invalid). **Native setter + focus + input/change/blur worked and enabled Submit** (UnternehmerTUM, HK Consulting) — the opposite of the 2026-07-17 note. Try native-setter-with-events first, fall back to fill_input, and re-verify field values after any upload (upload re-render wipes unfilled state).

- (2026-09-12) **Personio's job id is free from `<tenant>.jobs.personio.de/xml`**, and the application form is a SEPARATE
  page at `/job/<id>/apply` - `/job/<id>` and `#apply` both render only the ad.

## perview

### perview — General

*perview (jobsite.perview.de)*

2026-07-23 (DEOS AG, job=1514) - Guest form, no account. Reached from the employer page's 'Jetzt bewerben' anchor (set `target=_self` first). Required fields are many and all plain HTML: `TitleSingleSelect` (Herr), `FirstName`, `LastName`, `Email` + `emailConfirm`, `City`, `Degree` (textarea, free text), `Language`+`Level` (Level* is required - Deutsch/'Mittleres Niveau' = B1), `CellPhoneNumber`, `JobSourceSingleSelect` (XING is an option), `JobApplicationTypeSingleSelect` (Normal/Unemployed/Intern/**Student**), and two privacy checkboxes `CVWarehousePrivacy` + `CompanyPrivacy`. Free-text field `attribute_12614` = 'Was moechtest Du uns noch mitteilen?' (1000 chars). Document uploads are separate file inputs plus a `DocumentsList` select and are NOT HTML-required. Native-setter fills with input/change/blur events stick fine.

## Phenom

### Phenom — General

*Phenom / "CSB" career sites (`careers.<company>.com/global/en/...`) — Primetals, MHI Group*

- Step 1 "My Information": upload the CV into the single `input[type=file]` FIRST — **the parser then
  rewrites firstName / cellPhone / addressLine1**, so fill the profile fields *after* the upload and read
  them all back.

- **A cookie banner covers the fields**: `document.elementFromPoint` on `#cellPhone` returns a DIV until
  you click **Allow**. Do that before typing anything.

- Replacing a parsed value: `fill_input` and the native setter are both ignored. What works is
  coordinate-click → `el.focus(); el.setSelectionRange(0, el.value.length)` → `Input.insertText`.
  (`press_key("a", modifiers=2)` types a literal "a" — it is not Ctrl+A.)

- Phone must be plain digits; `+49…` fails with "Please enter valid phone number" and the NEXT button
  silently stays on step 1.

- Step 2 selects are React-controlled: the native setter DOES work, but `e.options[e.selectedIndex].text`
  read back in the same expression still shows "Please Select" — **re-read in a separate call** before
  concluding it failed. Fields: applicantSource, cust_QAwillRelocate, currency, cust_QAsalExpect,
  cust_QAprevEmpMHI1, cust_QArightToWork1, cust_QAimmigSpons, cust_QAnonCompAgree + 3 consent checkboxes.

- "Additional Documents" is a second `input[type=file]`; upload one file at a time (it appends).

- Success = `…/applythankyou?status=success&…` + "YOU HAVE SUCCESSFULLY APPLIED FOR"; ack from
  `donotreply@mssa.com`.

## PowerApps portals

### PowerApps portals — General

*PowerApps portals (*.powerappsportals.com)*

**Used by:** company career portals built on Microsoft Power Apps (e.g. INFOMOTION `infomotion-karriere.powerappsportals.com`). Reached via StepStone external redirect. **Guest, no login.** ASP.NET WebForms (field names `ctl00$ContentContainer$WebFormControl…`) — map fields by their `<label>` text; set text/selects via native-setter.

- Multi-step ("1 Persönliche Daten" → "2 Bewerbung abschicken"). Step 1 has a **honeypot** field labeled "Leave this field blank" — leave empty. Required consent checkbox "Ich stimme der Speicherung… laut Datenschutzerklärung zu" must be checked to advance ("Fortfahren").

- **CV upload trap (INFOMOTION):** the `<input type=file>` (`#AttachFile`) is paired with a required checkbox `#xrm1_cv_available` (label "Lebenslauf") that the portal normally auto-ticks on native pick but a CDP `setFileInputFiles` does NOT. AND every failed-submit **postback clears the file input**. Working order: check `#xrm1_cv_available` first → **then re-upload the file LAST** → then click submit ("Übermitteln") immediately, so the same POST carries both. Success → `/thank-you/` "Vielen Dank für Deine Bewerbung". Errors render as a banner "…konnte … nicht eingereicht werden: Aktivieren Sie … Kontrollkästchen …".

- Umlaut note: match "Übermitteln"/"männlich" by an ASCII substring (`/bermitteln/`, option starting `/^m/`) — heredoc mangles the umlaut so `===`/`/^Ü/` fails.

## Recruitee

### Recruitee — General

*Recruitee (`<company>.recruitee.com`) — 2026-08-30 addition*

- The application `<form class="sc-…">` sits inside a **`display:none` div** until the widget opens, and the
  "Bewerben" buttons did not open it. Fix: set that div's `style.display='block'` (walk up from
  `form.sc-1ntuzce-5`) — every field is then live and takes the native setter.

- Fields: `candidate.name` / `candidate.email` / `candidate.phone`, `candidate.cv`,
  `candidate.coverLetterFile`, `candidate.openQuestionAnswers.<id>.content` (text or textarea) and
  `…<id>.file` for document questions, `candidate.agreements.0.consent` checkbox.

- **"Senden" ignores coordinate clicks and only fires on a JS `.click()`.** The URL then moves to
  `…/applied` and the step tab reads "Beworben"; the form stays visible afterwards, so use the URL as proof.

## Rexx

### Rexx — General

*Rexx-Systems*

**Used by:** Some German companies (e.g., igus via StepStone redirect).

**How to recognize:** URL contains `rexx-systems.com` or a custom subdomain.

*Common Quirks*

- File inputs behave unusually — after uploading, the input value clears but the file IS attached. Verify by checking for the filename text appearing on the page.

- Silver Atena pattern (jobs.silver-atena.de inside an iframe on karriere.silver-atena.de): open the iframe URL (`bewerberformular_iframe.php?projGUID=...`) directly. File upload AJAX-fires on file selection (no upload-button click needed); set the Dokumentart select BEFORE the file. Privacy consent is a hidden checkbox `#AngabenRichtig` — click its label. Verify uploads via the file table text.

- KVB pattern (dienste.kvb.de/externe-stellen, reached via StepStone "Unternehmenswebsite"): plain `bewerbung_form[...]` fields fill fine with JS; `agbs_check` consent; upload slots by input name — `anschreiben`* (required), `lebenslauf`, `anlage1` = "letztes Arbeitgeberzeugnis" (NOT a free slot — no dedicated Immatrikulation slot, uploads are non-removable, so choose slots carefully BEFORE uploading). Gehaltswunsch is ANNUAL brutto (Werkstudent ≈ 15600). Submit is an `<a onclick>` with text "Senden". Success text: "Bewerbung abgeschlossen / Vielen Dank".

## SmartRecruiters

### SmartRecruiters — General

*SmartRecruiters*

**Used by:** Visa, Lidl, Bosch (some divisions), Equinix, IKEA, Swatch Group, LinkedIn (ironically).

**How to recognize:** URL contains `jobs.smartrecruiters.com`, `careers.smartrecruiters.com`.

*Common Quirks*

- SmartRecruiters parses the CV automatically — review parsed data carefully.

- Some instances have multi-step forms (Personal Info → Experience → Documents → Review).

- The "Review" step is critical — always check all fields before final submit.

- "Consent" checkboxes for data processing (GDPR) are usually required — check them.

- 2026-07-15 (Ströer oneclick-ui) — the whole form lives in **nested shadow DOM**: walk `el.shadowRoot` recursively for inputs/buttons; dispatch events with `{bubbles:true, composed:true}`. City is a **typeahead** (type → click the suggestion "Stadt, Land"; raw value fails "Wohnsitz" validation). Vorabfragen dropdowns (Arbeitserlaubnis, Deutschkenntnisse, Geschlecht) are also typeaheads — click input, type, click option; free text silently clears on blur. The message textarea **rejects semicolons** ("Feld darf nicht ; enthalten"). Only ONE document slot ("Lebenslauf*", re-upload REPLACES) — no CL slot; paste the letter into "Nachricht an das Hiring-Team" (via String.fromCharCode injection for umlauts). Weiter/Absenden are custom buttons — JS .click() no-ops; use getBoundingClientRect + click_at_xy (button y shifts as validation errors appear/clear; Absenden turns orange when valid). Photo file-input accepts images only — ignore it.

*SmartRecruiters oneclick-ui (jobs.smartrecruiters.com/oneclick-ui/...)*

No login needed (unlike classic SR flow). All controls are `spl-*` web components with shadow DOM:

- Text fields: `spl-input`/`spl-textarea` → `host.shadowRoot.querySelector('input|textarea')`, set via native setter + input/change events (`composed: true`).

- CV dropzone (`spl-dropzone[data-test=apply-with-resume-container]`): DOM.setFileInputFiles on the shadow file input DOES work but shows NO filename in page text (`hidefilelist`) — verify via the host's `files` attribute (JSON with fileId + attachmentType RESUME).

- CV parse OVERWRITES Vorname and CLEARS confirm-email — re-check both before Weiter.

- Screening comboboxes: type into shadow input, then click the matching `spl-dropdown-item` (light-DOM text). For `spl-multiselect-autocomplete` the inner input value stays "" after selection — check the HOST's `value` attribute (option UUID) to confirm selection.

- Buttons are `spl-button` → click the button in its shadowRoot. Watch for hidden required screening questions only visible after failed submit (screenshot to find them).

- Success = URL ends `/success` + "Bewerbung eingereicht!".

*SmartRecruiters oneclick-ui — 2026-08-24 additions*

- The Vorabfragen (screening) comboboxes are **NOT in any shadow root reachable from `document`** — they live under an `sr-screening-questions-form` element and my recursive `shadowRoot` walker never saw their dropdown items. They also do not open on click alone: **click the field, then `Input.insertText` one character, and the option list renders** — above the field when it is low in the viewport. Coordinate-click the option.

- `spl-multiselect-autocomplete` confirms selection via the HOST's `value` attribute (an option UUID), never via the inner input.

- CV parse fills first/last name, e-mail **and phone** (incl. the `+49` country select); it leaves confirm-email empty.

- Contact-step `Weiter` → `/screening`; `Absenden` → `/success` + "Bewerbung eingereicht!". Confirmation from `notification@smartrecruiters.com` within ~15 min.

*SmartRecruiters oneclick-ui (`jobs.smartrecruiters.com/oneclick-ui/company/<Co>/publication/<uuid>`) — 2026-08-24, Bosch*

- Everything lives in **shadow DOM**. `document.querySelectorAll('input')` returns 1 node; walk `el.shadowRoot` recursively.

- Field ids exist on BOTH the custom-element host and the inner `<input>`. `fill_input('#first-name-input', ...)` works (host), but `#question_<uuid>` does **not** — use `input#<id>` inside the shadow walk, or coordinate-click + `type_text`.

- `upload_file()` fails (its `DOM.getDocument` has no `pierce`). Working upload: collect file inputs into `window.__fi` with a shadow walk, then `Runtime.evaluate("window.__fi[i]")` → `DOM.setFileInputFiles(objectId=...)`. Verify by the filename text on the page.

- File-input order: `[0]` profile image, `[1]` top "autocomplete your application" dropzone, `[2]` the real **Resume** slot. The screening step has its own **Additional attachments** input.

- Buttons are `spl-button` / `oc-button` — `querySelectorAll('button')` misses them and JS `.click()` no-ops. Get `getBoundingClientRect()` after `scrollIntoView` and `click_at_xy`.

- **Back navigation clears the City field and renumbers every `spl-form-element_N` id.** Re-read ids after any Back.

- City is a **typeahead**: type, then click the "Stadt, Bundesland, Land" suggestion — the raw value alone does not commit.

- Phone: typing `+49 …` sets the country flag automatically and strips the prefix into the selector.

- **Screening questions that render with a magnifier icon are searchable selects, not free text.** Native-setter injection and `type_text`+Tab both LOOK filled and then silently clear on Submit ("Value is required"). Only: click → type one letter → click the option row in the dropdown.

- Bosch thesis screening asks: preferred period (DD/MM/YYYY), duration prescribed by the Studienprüfungsordnung (**6 months** for the user), prior contact with the department (Nein/No).

- (2026-09-02) **SmartRecruiters oneclick hides its confirmations in shadow DOM.** `document.body.innerText` never contains an
  uploaded filename, so "upload failed" is the default wrong conclusion - a screenshot showed the CV had attached
  on the first try. Its address field is a typeahead that rejects free text ("Bitte geben Sie Ihren Wohnsitz an");
  the fix is the **"Zum manuellen Ausfuellen hier klicken"** link, which swaps in plain Land/Region + PLZ fields.
  Also: the FIRST `input[type=file]` on the page is the **profile picture** (images only) - writing a PDF there
  produces a red format error that survives every later step. Target file inputs by position, not by index 0.

*SmartRecruiters public API — free search without a browser (2026-09-10)*

`https://api.smartrecruiters.com/v1/companies/<Company>/postings?q=thesis&limit=100&country=de` returns
JSON (title, city, releasedDate, id); `…/postings/<id>` returns the full ad in
`jobAd.sections.{jobDescription,qualifications}.text` (HTML — strip tags in Python). `BoschGroup` carried
18 thesis postings. Apply then goes through the normal oneclick-ui flow.

- (2026-09-10) **`api.smartrecruiters.com/v1/companies/<Company>/postings?q=thesis` is free, browserless and rich.**
  `BoschGroup` returned **18 live thesis postings** with full descriptions via
  `/postings/<id>` - enough to evaluate fit without opening a page. Probed slugs that do NOT exist:
  Vitesco, Continental, Schaeffler, KnorrBremse, Draegerwerk, Trumpf, Koerber, Festo, Wuerth, SICKAG.

## softgarden

### softgarden — General

*FriendlyCaptcha on softgarden forms is NOT a stop*

RENK's softgarden application renders an "I am human" FriendlyCaptcha widget. It is proof-of-work and
solves itself: check for `div.frc-container.frc-success` and a populated
`input[name="frc-captcha-solution"]` (≈600 chars). No challenge is presented and nothing is bypassed.
Also on that form the first COORDINATE click on "Submit application" did nothing (confirmed by
screenshot, per the softgarden hidden-confirmation rule) while a JS `.click()` submitted instantly;
success = `/applySuccess?aid=<uuid>`.

*softgarden (`job.<company>.com`) — 2026-08-30 addition*

- **The success text ships in the DOM at page load.** "Vielen Dank, die Bewerbung ist bei uns erfolgreich
  eingegangen!" reads identically in `innerText` before and after submit — verify by **screenshot**, never
  by text.

- Fields `applicationData.firstname/lastname/email/phone` + `applicationData.coverLetterText`; the CV input
  is `cv-file`, extra documents `attachments`. `resumeUploaded` and `allowApplied` are 0×0 **honeypots —
  leave them empty**.

- Attachments can carry over from an earlier session: check "Bereits hochgeladene Anhänge" and remove
  strays via the item's `[class*=DeleteButton]` before submitting.

- **FriendlyCaptcha ("Ich bin ein Mensch") self-solves** — `input[name=frc-captcha-solution]` fills itself
  with a proof-of-work token and needs no human interaction, so it is not a bot-check the agent must skip.

- The submit button reads "Bestätigen"; match it as `startsWith('Best')` (heredocs mangle the umlaut).

- (2026-08-30) **Confirmation text that ships in the DOM defeats `innerText` verification.** softgarden (`job.<company>.com`)
  renders "Vielen Dank, die Bewerbung ist bei uns erfolgreich eingegangen!" on page load, hidden — so the page text
  reads identical before and after submit. Four submit clicks were fired before a screenshot showed it had worked
  on the first (Gmail later confirmed exactly one application). **When a submit looks silent, screenshot before
  clicking again**, and only trust text that appears *and* is visible.

- (2026-08-31) **Chrome autofill fills honeypots.** softgarden's `allowApplied` GhostInput (aria-hidden, tabindex -1,
  opacity 0, `autocomplete="allow-applied"`) arrived pre-filled with "1" without the agent touching it. Read every
  honeypot back and clear it right before submit, instead of assuming "untouched = empty".

- (2026-09-01) **FriendlyCaptcha solves itself; it is not a human challenge.** RENK's softgarden form showed an
  "I am human" widget that reached `frc-container frc-success` with a 627-char `frc-captcha-solution`
  token without any interaction. Check for that class/token before treating it as a bot-check stop.
  (Same family as the RobCo reCAPTCHA-iframe lesson.)

*softgarden hosted form (`<company>.career.softgarden.de`, `<company>.softgarden.io`, `careers.<company>.de`) — 2026-09-03, Muehlbauer submitted*

- **File inputs carry `name=`, not `id=`.** `document.querySelector('#cv-file')` returns null while
  `querySelectorAll('input[type=file]')[0].id` looks like `cv-file` if the dump prints `x.id||x.name`.
  Use `input[name='cv-file']` / `input[name='attachments']`, and dump `JSON.stringify(x.id)` so an empty
  id is visible as `""`.

- 3 steps in one page (Lebenslauf -> Persoenliche Angaben -> Zusaetzliche Fragen); **"zum naechsten
  Schritt" only advances on a JS `.click()`**, coordinate clicks are swallowed.

- A previous application can leave **stray attachments** in "Bereits hochgeladene Anhaenge" (a `4.jpg`
  appeared on Muehlbauer). Its remove button also needs a JS `.click()`. Check the list before submitting.

- Text ids contain colons (`:r5:`) so `fill_input` cannot target them: match by `placeholder`, set a clean
  id with `setAttribute`, then fill.

- **German text: base64 + `TextDecoder`.** A `jstr()`-built string piped through `browser-harness < file`
  arrived double-encoded ("mÃ¶chte") because the harness reads stdin as cp1252. Encode in Python with
  `base64.b64encode(txt.encode())`, then in JS
  `new TextDecoder().decode(Uint8Array.from(atob(B64), c=>c.charCodeAt(0)))`.

- Radio/option groups (Standort, Bereich, Eintrittstermin) render as `<button>`s whose value lands in a
  hidden `input[name="applicationData.answers.N.answer"]` — click the button, then read that input back.

- **FriendlyCaptcha solves itself**: check for `frc-container frc-success` + a non-empty
  `input[name=frc-captcha-solution]` before treating it as a bot-check.

- **Confirmation ships hidden in the DOM on page load**, so `innerText` reads "Vielen Dank, die Bewerbung
  ist bei uns erfolgreich eingegangen!" both before and after submit. **Screenshot to verify.**

- (2026-09-10) **German button labels break JS string equality inside `js()`.** `t==="Bestätigen"` never matched on
  softgarden; `t.indexOf("tigen")>-1` did. Same class of bug as the cp1252 stdin issue - match ASCII.

- (2026-09-16) (2026-09-16) The attachment remove link (a.attachment__rm-lnk / .js-rm-lnk) fires a native confirm() that WEDGES Runtime.evaluate - the next js() call times out and looks like a dead target. It is not: call dismiss_dialog(accept=True) and the file is gone. A coordinate click on the same link did nothing first (the row re-renders), so JS .click() then dismiss_dialog is the working order. Poly-clip's form also carried a stray 4.jpg from an earlier session, confirming the carry-over warning above.

## StepStone

### StepStone — General

*StepStone*

**Used by:** StepStone is a job aggregator (like Indeed). It hosts both direct applications and redirects to company career pages.

**How to recognize:** URL contains `stepstone.de`, `stepstone.com`.

*Application Types on StepStone*

- **Smart-Apply ("Ich bin interessiert"):** Inline application within StepStone. Use JS `.click()` for the submit button (coordinate clicks are often ignored). Use the React native-setter pattern for text fields.

*Common Quirks*

- **Check the StepStone profile email.** Smart-apply locks the E-Mail field to whatever the profile holds, greyed out and uneditable — so if that is not your `JOBAGENT_EMAIL`, every StepStone confirmation lands somewhere the batch-end check cannot read, and the `/confirmation/success?applicationId` page plus `confirmation.png` are your only proof. Fix it once in the profile and the whole portal is covered.

- Detail pages show a "Passt hervorragend/weniger" fit badge computed against the uploaded Lebenslauf — use it as a pre-filter; skip "weniger" without opening.

- Smart-apply mechanics: "Ich bin interessiert" needs a JS `.click()` (coordinate clicks often ignored, submit button too). Text fields need the React native-setter pattern.

- First `input[type=file]` = CV slot. Uploading there **replaces** the existing CV.

- Extra docs: click **"Hinzufügen"** → upload via the modal's file input → confirm **"zu deiner Bewerbung hinzufügen"**.

- Some forms have a dedicated **"Anschreiben*"** (cover letter) slot under Bewerbungsfragen — check before attaching under Zusätzliche Dateien.

- StepStone rejects uploads under 8 KB — ensure PDFs are exported with embedded fonts (UseISO19005_1 / PDF/A → ~200 KB).

- **"Send application" can hang**: button goes disabled, no navigation, job missing from the applied list (verify at `stepstone.de/membersarea#applications`). Recovery that works: reload the job page → click **"Continue application"** (draft is kept) → submit again → lands on `/confirmation/success?userFlow=ApplyExpress`. Seen 2026-07-04 (Mitsubishi). A flow that 3x redirects straight to `/application/error` is broken server-side — mark Blocked, retry another day (b-trend 2026-07-04).

- Landing on **"Hat mit deiner Bewerbung alles geklappt?"** after "Ich bin interessiert" = NOT submitted; it is an external redirect. Click the **"Unternehmenswebsite" BUTTON** (not a link) on that page to open the company portal (e.g. Barmag → careers.barmag.com/SuccessFactors, Charles Real Estate → Kenjo, igus → rexx-systems). Follow that ATS's section.

- Real smart-apply forms (URL ends `/application/smart-apply`, not an immediate redirect) use plain native `<select>` elements for Anrede/Bildungsabschluss/etc. — coordinate-clicking the visible option row is unreliable (silently no-ops); read `select.options` for the `value`, then set via the native setter + `input`/`change` events. A section still showing "Aktion erforderlich" after filling everything else usually means one of these selects didn't actually register — recheck every select's displayed value before submit, not just the text-input fields.

- Some smart-apply forms have a dedicated required **"Anschreiben*"** upload input separate from the optional "Zusätzliche Dateien" one — check for both; uploading only under "Zusätzliche Dateien" leaves the required slot empty and blocks submit.

- 2026-07-14 — On **employer-direct** postings, "Ich bin interessiert" often redirects to the company's own ATS (e.g. Atlas Copco → SAP SuccessFactors **easyapply** `easyapply-*.dispatcher.eu2.hana.ondemand.com`). This SF easyapply is a **guest form, no login**: `input[name="CVFileUpload"]` (required, replaces nothing — fresh), `CLFileUpload`/`additionalFileUpload` optional; text `#idIptFirstName-inner`/`idIptLastName-inner`/`idIptEmail-inner`/`idIptTelefon-inner`/`idIptZIPCode-inner`/`idIptCity-inner` fill via `fill_input`; recruiter-visibility radios `#option1/2/3-RB` (pick `option3` = most privacy-preserving); Country + "How did you hear" are `sap.m.Select` (id `#idSelCountry`/`#idSelApplicationsource`) — NOT typable and `.click()` won't open them reliably. **Working method (2026-07-15): drive them via the UI5 API** — `const core=sap.ui.getCore(); const sel=core.byId('idSelApplicationsource'); const item=core.byId('__itemN-idSelApplicationsource-K'); sel.setSelectedItem(item); sel.fireChange({selectedItem:item});`. Read the option ids/labels first with `querySelectorAll('[id*="idSelApplicationsource"]')` (they persist in DOM even closed; the popover-visibility approach fails because the huge country `<li>` list is always in the DOM and swamps the query). Source options incl. **"Job Board/Job Website"** (= StepStone); Country "Germany" → hidden value "DE". The **"I have read and accept the Privacy policy"** control is a `sap.m.Switch` (id `privacy`), required, defaults OFF (shows red ✗) — turn on via `core.byId('privacy').setState(true); ...fireChange({state:true})` (green ✓). Visibility radios are a `sap.m.RadioButtonGroup` id `visibleTo` — `core.byId('visibleTo').setSelectedIndex(2)` = most private ("Only recruiters managing jobs I apply to"). Send button bottom-right via `click_at_xy` (~1289,527) → "Thank you for your application" checkmark page. Upload works via `upload_file('input[name="CVFileUpload"]', path)`.

- 2026-07-14 — **Daemon instability**: after an apply-button click the heavy application SPA (SF UI5, employer portals) repeatedly wedged the CDP `Runtime.evaluate` (times out) while `capture_screenshot` still worked — JS-first extraction became impossible on that tab. Also the StepStone header silently dropped from "the user"+avatar to "MK Mein Konto" (logged out) mid-batch, so quick-apply stopped proceeding. Rule: if `Runtime.evaluate` times out 2× on a tab but screenshots work, the tab/daemon is wedged — don't keep retrying; and re-confirm the StepStone header still shows "the user" before each smart-apply (session can drop mid-batch).

- 2026-07-21 — **Smart-apply "Bewerbung abschicken" stays `disabled` until the prefilled contact fields are "touched" in React.** Profile-prefilled `firstName`/`lastName`/`email`/phone don't count as filled — the button never enables and clicking it early triggers the "hang" (button disables, no nav, "Bewerbung fortsetzen" draft on reload). **Reliable enabler:** native-setter re-set every field, then fire input+change+blur: `var s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; [firstName,lastName,email,tel].forEach(e=>{var v=e.value;s.call(e,'');e.dispatchEvent(new Event('input',{bubbles:true}));s.call(e,v);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));e.dispatchEvent(new Event('blur',{bubbles:true}));})`. Then enumerate ALL buttons (there can be a hidden disabled twin) and click the visible one with `!b.disabled`; poll `page_info().url` for `/application/confirmation/success?...&applicationId=<uuid>` = SUBMITTED (this URL + applicationId is the proof; the confirmation email went to the `.kv` inbox at the time — since 2026-07-24 it goes to primary Gmail and is checkable). The **CV is already attached from the StepStone profile** ("Lebenslauf_… Hochgeladen am … • 0.8MB") — no upload needed; these minimal forms have no CL slot. (4/4 this way: Autohaus, Speed4Trade, Startup Insider, FLECS.)

- 2026-07-21 — **Smart-apply "Zusätzliche Fragen" (Aktion erforderlich)** block the button until answered. Seen at FLECS: (1) **Deutschkenntnisse*** = 7-option `<select>` (Keine/Grundkenntnisse/Gute/Fließend/Verhandlungssicher/Muttersprache) → set `Grundkenntnisse` for B1 (truthful, does NOT gate submit); (2) **frühestmögliches Startdatum** = `input[type=date]` (name `atsiQuestions.id:<n>.id:<n>`) → set `2026-08-01` (yyyy-mm-dd); (3) **"aktuelle Erlaubnis in Deutschland zu arbeiten?"** = unnamed radio pair value `TRUE`/`FALSE` → check `TRUE` (has student permit). Set select/date via native setter; radio via `checked` native-setter + click/change event. Section flips off "Aktion erforderlich" and button enables.

- **The greyed-out E-Mail field on smart-apply is the profile email and cannot be edited in the form** — it is the single clearest demonstration of why one address everywhere matters: you cannot correct it per-application, only in the profile.

- 2026-07-22 - **Two-stage smart-apply (mirage.at-ats.com)**: on some employer-direct postings the StepStone smart-apply form is only stage 1. After clicking "Bewerbung abschicken" the page shows "Wir bereiten Ihre Bewerbung vor" for ~20-40s, then navigates to `mirage.at-ats.com/?conversationUuid=...&jb=stepstone_de&ou=<base64 employer apply URL>` which hosts the employer's REAL form (TK Elevator -> jobs.tkelevator.com). Fill that second form too; only its submit produces `/application/confirmation/success?...&applicationId=<uuid>&status=SUCCESS` back on stepstone.de. Do NOT treat the stage-1 click as submitted. Second-form fields seen at TK: `first_name`/`last_name`/`e-mail_address` prefilled, `custom_question_*` (Wunscheinkommen = **numeric only**, Kuendigungsfrist optional), two required `<select>` (Wie aufmerksam geworden -> StepStone option value ends `_stepstone_de`; Mitarbeiter-Empfehlung -> `_nein`), a free `input[type=file]` for the CV, and TWO `name="dps"` selects: dps[0] required = `true` (application processing), dps[1] optional marketing = `false` (decline).

- 2026-07-23 — **StepStone smart-apply: `fill_input` corrupts `input[type=date]`.** Keyboard-level typing lands in the wrong date segment (DOB `2000-07-02` came out as `22000-02-07`). Use the native setter with the ISO value (`'2000-07-02'`) + input/change/blur. Conversely, when a whole "Zusätzliche Fragen" section stays on "Aktion erforderlich" after native-setter fills, re-fill the plain text inputs with `fill_input` — that is what flipped HPA's 12-question section to done.

- 2026-07-23 — **Some StepStone employers reject PDF CVs.** Stadtwerke Stuttgart's smart-apply showed "Der gewählte Dateityp 'pdf' wird leider nicht unterstützt. Unterstützte Dateiformate: .odt, .xls, .xlsx, .txt, .rtf" against both the profile CV and a fresh upload, keeping Submit disabled. Not a bug to debug — it's the employer's allowed-filetype config; needs an .rtf/.odt CV (we only have PDFs) → Blocked.

- 2026-08-01 — **The `Bewerbung abschicken` button's `.disabled` reads TRUE in JS until it is scrolled into view and React reconciles.** Do NOT conclude "stuck disabled" from the first check after filling — `button.scrollIntoView({block:'center'})`, wait ~2s, re-read `.disabled` (it flips to false), then `.click()`. This was the whole "disabled after touch" mystery on Systecs/zebotec/RECONIQ; all three submitted once scrolled-to. Still do the 2026-07-21 contact re-touch first. Genuine submit = URL `/confirmation/success?...&applicationId=<uuid>` + "deine Bewerbung ist raus" + a `info@email.stepstone.de` "your application ... has been sent" mail (now to primary Gmail). 8/8 smart-applies converted this way on 2026-08-01.

- 2026-08-01 — **Zusatzfragen: text questions (hours/study-end/salary/city) resist `fill_input`** (leave blank) — use the **native-setter** + input/change/blur. A "Wie gut sprichst du Deutsch?" radio group (C2..A1) answered **B1 truthfully** shows a soft yellow warning "Deine Deutsch-Kenntnisse entsprechen nicht den Anforderungen" but does NOT hard-disable submit — it still went through (RECONIQ). Don't treat that warning as a gate.

- 2026-08-01 — **Two-stage mirage.at-ats.com → onlinebewerbungsserver.de is a CDP-upload dead end.** Its document step's "Datei hinzufügen" is an ASP.NET postback that ignores CDP `setFileInputFiles` ("Ihre hochgeladenen Dateien: Keine Dateien hinzugefügt" no matter how many retries), and its `chkReadDS` DS-consent must be genuinely `.click()`ed (default value="on" ≠ checked; a modal "Sie müssen die Datenschutzbestimmungen akzeptieren" blocks otherwise). Fill everything, then NeedsUser (the user does the upload+submit). CemeCon 2026-08-01.

- 2026-08-24 (connectiv! eSolutions) — **"Zusaetzliche Dateien -> Hinzufuegen" opens a modal whose upload input is `input[type=file]` INDEX 1; index 0 is still the CV slot.** Uploading the Anschreiben with a bare `upload_file('input[type=file]', ...)` silently REPLACED the profile CV with the cover letter (the CV card then read "Anschreiben_...pdf" and the fit badge flipped to "Job-Abgleich nicht moeglich"). Collect the inputs into `window.__fi` and target `__fi[1]` via `Runtime.evaluate` + `DOM.setFileInputFiles(objectId=...)`; then **screenshot the CV card** to confirm which file sits in which slot before submitting. Recovery is simply re-uploading the Lebenslauf to `__fi[0]`.

- 2026-08-24 — **`Bewerbung abschicken` can stay `.disabled === true` in JS forever and still submit on a coordinate click.** After the 2026-07-21 contact re-touch and a `scrollIntoView`, the property never flipped, but the button rendered solid teal in a screenshot and one `click_at_xy` on its real position produced `/confirmation/success?userFlow=ApplyExpress&applicationId=<uuid>`. Trust the pixels over `.disabled`.

- **StepStone** — the bare slug `stepstone.de/jobs/<slug>` is the reliable form. `ag=age_7` and
  `am=INTERNAL` have each silently returned zero results while the facet count said otherwise; if a
  sweep comes back empty, drop the params rather than concluding the pool is dry. `am=INTERNAL`
  ("Schnelle Bewerbung"), when it works, is the highest-yield filter — every card is an inline apply.
  Rate-limits after ~20–30 searches in a session.

**StepStone "Ich bin interessiert" is mostly a router, not a submit.** A `/confirmation/success`
that offers "Unternehmenswebsite" and had no form step did **not** submit — but it is a route, not a
dead end: follow that button and it lands on the employer's ATS often enough to have carried whole
batches. A genuine submit is `/confirmation/success?...applicationId=<uuid>` plus "Bewerbung ist
raus"; `/confirmation/pending` must be polled (it resolves to success, unknown-but-real, or error).
After an `/error`, StepStone permanently re-routes that job externally.

- **Never force-click a `disabled` StepStone submit.** One forced click permanently poisons the
  application — the button never re-enables and "Bewerbung fortsetzen" restores the draft without
  the answers. Poll `.disabled` until false, then click once.

- When two or three smart-applies in a row refuse to enable, **switch channel** rather than
  debugging the fourth. Both roles that hung this way converted via the employer's own board.

- 2026-07-01 — StepStone: the user is logged in; detail pages show a "Passt hervorragend/weniger" fit badge computed against his uploaded Lebenslauf — useful pre-filter signal. Many listings are "inline" (employer-posted, quick-apply via "Ich bin interessiert").

- 2026-07-01 — StepStone smart-apply mechanics: "Ich bin interessiert" needs a JS .click() (coordinate clicks often ignored, submit button too). Text fields need the React native-setter pattern (fill_input helper is flaky). First input[type=file] = CV slot (uploading there REPLACES the CV). Extra docs: click "Hinzufügen" → upload via the modal's file input → confirm "zu deiner Bewerbung hinzufügen". Some forms have a dedicated required "Anschreiben*" slot under Bewerbungsfragen — check before attaching the letter under Zusätzliche Dateien.

- 2026-07-01 — StepStone rejects uploads under 8 KB. Word's default PDF export of a 1-page letter is ~7 KB → always export via ExportAsFixedFormat with PDF/A (UseISO19005_1) → ~200 KB with embedded fonts.

- 2026-07-01 — Some StepStone postings ("Hat mit deiner Bewerbung alles geklappt?" page) are external redirects, not smart-apply: Charles Real Estate → Kenjo (numeric-only salary field, CV-only upload), igus → rexx-systems (hidden file inputs upload via AJAX and clear themselves — check page text for the filename, not input.files; consent checkbox agbs_check required).


- 2026-07-01 — StepStone fit badge ("Passt hervorragend") as pre-filter; check German postings' language line FIRST (~half die on C1 requirements).

- 2026-07-02 — StepStone "Ich bin interessiert" landing on "Hat mit deiner Bewerbung alles geklappt?" = NOT submitted; it is an external redirect. Click the "Unternehmenswebsite" BUTTON (not a link) on that page to open the company portal (e.g. Barmag → careers.barmag.com/SuccessFactors).

- 2026-07-04 — StepStone "Send application" hung silently (button disabled, not in applied list); portal-sent UI trusted too early. Rule: after every StepStone submit, confirm `/confirmation/success?userFlow=ApplyExpress` or the applied list — recovery via "Continue application" (see howtologin.md § StepStone).

*StepStone smart-apply — required date / select are NOT unfillable (CORRECTION 2026-08-14)*

The 2026-08-04 verdict that required `input[type=date]` and required `<select>` fields "resist ALL programmatic input" was **wrong**, and it cost 6 rows a NeedsUser label. What actually works:

1. native setter with the **ISO** value (`'2026-09-01'`) + `input`/`change`/`blur` — the date lands and React accepts it;

2. `button.scrollIntoView({block:'center'})`, **wait ~3s**, THEN re-read `.disabled` (the 2026-08-01 reconcile rule — the first read lies);

3. only if still disabled, hunt for the genuinely-missing required item — it is usually a *different* field than the one blamed. At ASMPT the blocker was a required **Anschreiben upload slot**, not the consent radio the notes accused. At Weber a single date + scroll was the whole fix.
Rule: before writing NeedsUser on a smart-apply, scan the page text for `Aktion erforderlich` and read which SECTION carries it.

*StepStone `am=INTERNAL` sweep + multi-slot uploads + pending/error routing (2026-08-19)*

- **Search:** `https://www.stepstone.de/jobs/<slug>?ag=age_7&am=INTERNAL&wp=1&page=N` — `am=INTERNAL` is the "Schnelle Bewerbung" facet, i.e. **only inline smart-apply jobs**. (`am=EXTERNAL` is the opposite.) Extract cards with `article[data-at="job-item"]` → `a[data-at="job-item-title"]` / `[data-at="job-item-company-name"]` / `-location` / `-timeago`, accumulate across pages in `localStorage.__JOBS`. Always navigate from the stored card `href` — a re-typed job ID silently serves a DIFFERENT job (14375070 vs 13907202 on 2026-08-19); verify `document.querySelector('h1').innerText` before clicking apply.

- **Multi-slot document uploads** (forms with Zeugnisse / Zusätzliche Unterlagen / Bewerbungsanschreiben*): `upload_file()` with `input[type=file]:nth-of-type(N)` is a **silent no-op** (`files.length` stays 0). Working method:
  `res=cdp("DOM.performSearch", query="input[type=file]")` → `ids=cdp("DOM.getSearchResults", searchId=res['searchId'], fromIndex=0, toIndex=res['resultCount'])['nodeIds']` → `cdp("DOM.setFileInputFiles", files=[abs_path], nodeId=ids[k])`. Slot index follows page-text order; index 0 is the profile-CV replace slot. Verify by the filename + "Heute hochgeladen" text.

- **Submit outcomes:** the button click lands on `/application/confirmation/**pending**` first. Poll `page_info()['url']` every 5s (up to ~50s). It resolves to:
  - `/success?...&applicationId=<uuid>` + "Bewerbung versendet!" = done;
  - `/unknown?...&applicationId=<uuid>` + "Deine Bewerbung ist auf dem Weg" = **also a real submit** — confirm via `stepstone.de/membersarea#applications` ("Beworben Heute") and/or the employer's receipt mail (Instone's SuccessFactors mail arrived ~30 s later);
  - `/error` = failed. **After an `/error` StepStone re-routes that job to the employer site permanently** — reloading the posting and clicking "Ich bin interessiert" now yields "Hat mit deiner Bewerbung alles geklappt?"; the recovery is the **"Unternehmenswebsite"** button, not "Bewerbung fortsetzen" (Züblin 2026-08-19 → jobboerse.strabag.at → talentacquisition.strabag.com, submitted first try).

- 2026-08-22 — **StepStone smart-apply date fields need a real click + typed input.** On logen.ai the JS native-setter wrote `2026-09-01` into the date input and it *displayed* correctly, but React never registered it and "Bewerbung abschicken" stayed **disabled with no error and no aria-invalid** — indistinguishable from a hung form. Coordinate-clicking the field and typing via `Input.insertText` enabled the button instantly. Text inputs and `<select>`s on the same form are fine with the native setter; only the date field behaves this way.

- 2026-08-22 — **Never click StepStone's `Bewerbung abschicken` while it reads `disabled` — it permanently poisons that application.** Confirmed on WEH FluidTech and Mayfair: after one forced click (`removeAttribute('disabled')` + `.click()`) the button never enabled again, and the documented recovery (reload job page → "Bewerbung fortsetzen") restores the draft **without** the answers, so everything has to be re-typed and still fails. The 2026-07-21 note said this; this batch proved the damage is not recoverable the same day. Poll `.disabled` (and `React props.disabled` via `__reactProps$*`) until false, then click once.

- 2026-08-22 — **A StepStone smart-apply submit button that stays disabled is sometimes an external-redirect button.** On Testo the forced click did not submit on StepStone — it navigated to `jobs.testo.com/.../job_application/new` (softgarden), where the real 1-page form lives. So "disabled forever + no Aktion erforderlich" has two possible meanings: employer-side hang, or a redirect. Check the URL after the click before concluding either.

- 2026-08-22 — **StepStone express-apply is not reliable at volume.** Of 10 quick-apply targets, 4 submitted and 6 (WISAG, WEH, SUBSEQ, Mayfair, DIN Solutions, ESB) never enabled their submit button, several with every section showing "Bereit" and `Kontaktdetails` carrying no badge at all. No 429s in the network log, fresh tab made no difference. When two or three smart-applies in a row refuse to enable, **stop and switch channel** (employer-direct via the "Unternehmenswebsite" button on the phantom `/confirmation/success` page) instead of debugging the fourth.

*Search-URL params (2026-08-23 — CHANGED, breaks old sweeps)*

`?ag=age_7`, `?ag=age_14`, `?am=INTERNAL` and friends now return **zero results** on
`stepstone.de/jobs/<slug>` — the page renders "Es passt gerade kein Job zu deiner Suche" and echoes the
raw param (`age_30`) back as a filter chip. The `am=INTERNAL` quick-apply trick from 2026-08-19 is dead
in that form. **Sweep the bare slug** (`https://www.stepstone.de/jobs/masterarbeit`) — it returns ~126
cards and each card carries its own freshness text (`vor 3 Tagen`) and `Schnelle Bewerbung` badge, so
filter in JS after extraction instead of in the URL.

Two more things about the bare-slug results:

- A stale saved search can pin a location ("Suchst du noch nach Software Engineer Intern in 09111?") —
  it does not filter the results, but it does appear in the page text.

- Cards from the "Entdecke Jobs, die zu deiner Erfahrung passen" carousel are interleaved with real
  results and share the `article` selector; drop any card whose text starts with that phrase.

**Open a posting by id alone:** `https://www.stepstone.de/stellenangebote--x--<id>-inline.html` resolves
correctly — the slug segment is ignored, so only the numeric id has to be carried between steps.

- 2026-08-23 — **Batch finished 10/10 submitted, but only 4 of them came from StepStone.** Once StepStone smart-apply stopped enabling its submit button, the productive pattern was: StepStone posting → "Ich bin interessiert" → phantom `/confirmation/success` → **Unternehmenswebsite** button → employer ATS. That path produced Testo (softgarden), Otto ×2 (own guest portal), FIEGE (karriere.fiege.com), OSCAR (HR4YOU) and, via the arbeitnow feed and a `jobs.personio.de` web search, E.ON Drive Infrastructure and dida (both Personio guest forms). **Personio guest forms remain the single most reliable channel — two attempts, two submissions, both confirmed by email within minutes.**

- 2026-08-23 — **StepStone's React apply button ignores coordinate clicks now.** `click_at_xy` on "Ich bin interessiert" silently did nothing on three postings (elementFromPoint confirmed no overlay, and the CDP Input pipeline was fine — `Input.insertText` worked). A JS `.click()` opened smart-apply every time. Related and still true: StepStone date fields still need focus + `Input.insertText`, not the native setter.

- 2026-08-23/24 — **StepStone's thesis pool is now genuinely drained for this profile; XING is carrying thesis search alone.** Seven StepStone slug sweeps (`masterarbeit`, `abschlussarbeit`, `master-thesis`, `masterarbeit-informatik`, `masterarbeit-ki`, `abschlussarbeit-kuenstliche-intelligenz`, `master-thesis-artificial-intelligence`) produced **3 genuinely new postings, all dupes or capped**. XING paginated (`&page=2..4`, 20 cards/page) is the productive move and is what filled the batch. Language gate killed 10 of ~30 evaluated, and the "requirements block, not the title" rule earned its keep three more times (ELSSSER "App-Entwicklung" is a BWL market-analysis thesis that explicitly says *"programmierst du nicht selbst"*; Ingenics "Smarte Automatisierung" is a strategy study; Göhring/DE-group/Computer-LAN are generic initiative posts).

*StepStone smart-apply — `fill_input` re-touch enables what the native setter cannot (2026-08-29, SUBSEQ)*

The 2026-07-21 native-setter contact re-touch left `Bewerbung abschicken` `.disabled === true`, and a
screenshot confirmed it was **genuinely greyed** (not the 2026-08-24 pixels-lie case) — the same wall that
produced a `Blocked` row for this job on 2026-08-22. What actually flipped it: **`fill_input('[name="email"]', "")`
then `fill_input` the real value, plus `fill_input('input[type=tel]', ...)`**. Real key events on the
prefilled contact fields are what React counts as "touched" on these minimal forms; the native setter is not.
Note the email reads back UPPERCASE from the profile and stays uppercase — that is cosmetic, not the blocker.
Order to try on a stuck minimal smart-apply: native-setter re-touch -> scrollIntoView + 3 s -> screenshot ->
**fill_input re-touch** -> only then Blocked.

- (2026-08-29) **StepStone detail pages carry a `Schon beworben` badge** on jobs already applied to, and the apply
  button is replaced by it. Grep the page text for it *before* packaging — it caught ABP Induction and
  KNOWYOURCHAT in one batch. It is a second signal, not a replacement for `tracker.py check`: Otto's two
  roles showed no badge yet were both Submitted a week earlier, and D-LABS showed none while JOIN's own
  dashboard had it "In Review".

*StepStone — router-vs-form ratio and dead employer links (2026-08-30)*

Of 5 "Ich bin interessiert" clicks this batch, **only 1 opened a real inline form** (sitec systems, submitted); the
other 4 went straight to `/application/confirmation/success?locale=de_DE` showing **"Hat mit deiner Bewerbung alles
geklappt?"** with no form step — the router, not a submit. Following the **"Unternehmenswebsite"** button from there
resolved to: freudenberg.wd3 Workday (submitted), nxp.wd3 Workday (submitted), textron.taleo.net (submitted as
guest), `karriere.mainzer-stadtwerke.de/…/not-found` (dead) and `jobs.cpp.canon/…` ("You can't view this job because
it's not available at this time"). **Treat the router as normal, not as failure — but verify the employer link
resolves before packaging**, because a StepStone `Bewerbungsschluss` in the future does not mean the employer's own
posting is still live (Canon's board returned "No jobs found" for the same title).

*Smart-apply "submit never enables" = a REQUIRED hidden document slot (2026-08-31, root cause)*

This is the cause of the whole 2026-08-22 failure class (6 consecutive jobs: SUBSEQ, Mayfair, DIN
Solutions, ESB, BWT, WEH) where every field was filled, sections read "Bereit", and
`Bewerbung abschicken` stayed `disabled` forever. **The contact re-touch (2026-07-21) and the
scrollIntoView wait (2026-08-01) do nothing against it** - verified live on TransnetBW 14438036,
all three enablers applied with zero change.

The form carries a **`Zusaetzliche Fragen` block with up to 7 `Weitere Dokumente` slots**. Some are
optional; the required ones are marked **only by an asterisk in the label** (`Weitere Dokumente*`).
The slot's `<input type=file>` is:

- **hidden** (`offsetParent === null`, behind a styled "Datei auswaehlen" control), and

- **`required === false`** in the DOM - the requirement lives purely in the React layer.

So any "enumerate visible inputs and check `.required`" pass reports the form complete while React
blocks submit. That is why six jobs looked finished and none could be sent.

**Procedure:**

1. `document.querySelectorAll('input[type=file]')` - index 0 is the CV slot, 1..N are the
   `Weitere Dokumente` slots in DOM order. Discriminate by `accept`: the CV slot is
   `.pdf,.docx,.jpg,.jpeg,.png,.xlsx`; the document slots are the longer list with `.pptx`/`.mp4`.

2. Read `body.innerText` from `Zusaetzliche Fragen` and list the `Weitere Dokumente` lines **in
   order**. The Nth such line maps to file input N. Lines ending in `*` are the required ones.
   Do NOT try to find the input inside the label's container - the inputs are portaled out, so
   every ancestor walk lands on `<body>` and returns all 8 inputs (this cost two wrong guesses).

3. Fill each asterisked slot with `cdp("DOM.setFileInputFiles", files=[abs_path], objectId=...)`
   on that exact index. On TransnetBW slots 5/6/7 were required -> `disabled` flipped
   `true -> false` and `Aktion erforderlich` went to 0 the moment the third landed.

4. **Verify by the UI text ("Heute hochgeladen"), never by `input.files.length`** - the component
   consumes the FileList and the input reads back `0` even on a successful upload.

**Which documents (`Other Docs/`):**

- **`Weitere_<Name>.pdf` = the user's earned certificates. Attach it WHENEVER a document
  slot exists**, required or optional, on any portal - it is a positive differentiator, not filler.
  This is the one document to add proactively. (It is also the bundle the Arbeitszeugnis was
  extracted from, pages 12-13.)

- For slots that are **required**, in order: Immatrikulation -> Transcript of Records ->
  Aufenthaltstitel -> B.Tech degree. These four are compliance documents: fill only slots actually
  marked required, and on other portals attach them only when asked for or clearly beneficial.

- With several free slots, lead with the certificates, then the required four in order.

**Aim carefully - index 0 is the CV.** Writing to it silently replaces the profile CV on the draft
(seen 2026-08-31: the CV became `Immatriculation...pdf`, "Job-Abgleich nicht moeglich"). Restore by
uploading `application/CV/Ai/Lebenslauf_<Name>.pdf` to index 0. There is **no remove
control** for an uploaded document, so a wrong file can only be overwritten, not deleted.

*"confirmation/success" WITHOUT an applicationId is a router, not a submit (2026-08-31)*

Clicking `Ich bin interessiert` on a router posting lands on
`/job/<uuid>/application/confirmation/success?locale=de_DE` and renders
"Hat mit deiner Bewerbung alles geklappt?" - **nothing was submitted** (confirmed: no
`info@email.stepstone.de` mail for OKAPI:Orbits 13986392). The discriminator is the
**`applicationId` query parameter**, not the word "success" in the path. Polling for "success"
alone logs phantom submissions.

*StepStone smart-apply — TEXTAREA questions need `fill_input`, and the id is not a valid selector (2026-08-31, REWE)*

Generalises the 2026-08-29 SUBSEQ note from contact fields to the whole "Zusätzliche Fragen" block.
On REWE's form every one of the 20 `atsiQuestions.*` fields held the right value, `aria-invalid` was
null everywhere, no error node existed, `document.hidden` was False and the honeypot was cleared — and
the section still read **Aktion erforderlich** with `Bewerbung abschicken` disabled. Native setter,
real `Input.dispatchKeyEvent` chars into each textarea (they *did* land), and a full
`_valueTracker.setValue('')` re-commit on all 20 fields all failed. What worked on the second sitting:

- **Give every React field a clean id first.** Their generated ids look like `genesis-form-element-:r13:`
  and the colons make `querySelector('#...')` throw *"is not a valid selector"* — so `fill_input` can
  never target them. Do `e.setAttribute('id','q_'+name)` in a JS pass, then address `#q_<name>`.

- **`fill_input` every text input AND every textarea**; keep the native setter for `<select>` only.
  The section flipped to *Bereit* and the button enabled immediately.

- Keep the answers short — `fill_input` types character by character.

Three more traps on this class of form:

- **"Bewerbung fortsetzen" restores the draft with every answer EMPTY** (files and CV survive). Budget a
  full refill, do not assume the draft carries answers.

- **The FIRST `input[type=file]` is the CV slot and uploading there REPLACES the profile CV** — a
  certificate went in as the CV. Extra documents go through the **`+ Hinzufügen`** button, which appends a
  *new* input; re-reading `querySelectorAll('input[type=file]')` and using the last index without clicking
  Hinzufügen just overwrites the same slot.

- **Starred upload slots are enforced without a `required` attribute.** TransnetBW's three
  `Weitere Dokumente*` and Taunus Sparkasse's `Anschreiben*` / `Arbeitszeugnis*` /
  `Schul(abschluss)zeugnis*` each kept the submit disabled until filled. Scan the page **text** for `*`
  and diff against what you uploaded.

- **The last `<textarea>` is a honeypot** (`aria-hidden="true"`, `tabindex="-1"`, `visibility:hidden`) and
  arrives pre-filled with `x`. Clear it before submit.

*StepStone — `/confirmation/unknown` is a real submit (2026-08-31)*

Four submits this batch resolved to `/application/confirmation/unknown?...&applicationId=<uuid>` with
"Deine Bewerbung ist auf dem Weg. Leider dauert der Versand manchmal etwas länger." Every one of them was
genuine: WISAG, ADAC, TransnetBW and Taunus all produced the employer's own Eingangsbestätigung within
minutes, and REWE showed **Beworben** in `stepstone.de/membersarea#applications`. Treat `unknown` +
applicationId as Submitted and verify in Gmail; it is not the `/error` case.

- (2026-08-31) **The native value-setter does not work on StepStone's question TEXTAREAS, and the failure is silent.**
  REWE burned ~half the batch's browser budget: 20 fields all holding correct values, no `aria-invalid`, no
  error, honeypot cleared, and the section still said *Aktion erforderlich*. `fill_input` on every text field
  **and textarea** fixed it in one pass. The blocker to knowing this earlier: React's generated ids contain
  colons (`genesis-form-element-:r13:`), so `querySelector('#…')` throws and `fill_input` cannot target them —
  **set a clean id first**, then fill. Generalise: when a section is "complete" by every readable signal but
  the button disagrees, the fields are DOM-filled and React-empty.

*2026-09-01 — smart-apply forms with a document QUESTION have TWO file inputs*

When an employer question is itself an upload ("Bewerbunsgsanschreiben*", leasyro), the page holds two
`input[type=file]`. **Index 0 is the stored-CV slot, index 1 is the question's slot.** Uploading the
cover letter to index 0 silently REPLACED the CV (the "Berufserfahrung / CV" card then showed
`Anschreiben_….pdf`) and left the question unanswered. Fix: index 0 = Lebenslauf, index 1 = the
question's document, wait ~8 s between the two, then re-read the section badge.

Also: the `document.hidden` wedge blocks the *first* "Ich bin interessiert" click on the job page too —
it silently does nothing and leaves you on `…-inline.html`. Un-wedge (minimize→restore
`Browser.setWindowBounds`) and click again rather than hunting for a different selector. This is what
had kept BWT (14372093) "Blocked / Kontaktdetails never gets a badge" for two batches: after the
un-wedge the badge appeared immediately and every question accepted its value.

- (2026-09-01) **"One failure class" was four different things.** Of 12 rows carrying near-identical
  smart-apply notes: **4 postings had simply EXPIRED** (DIN Solutions, ESB, b-trend-setting,
  Stadtwerke Stuttgart — "Diese Stellenanzeige ist nicht mehr verfuegbar"), **1 was a phantom**
  (Tomorrow Bird: StepStone shows "Schon beworben"; Gmail shows it was applied to BY EMAIL on
  2026-03-30 and rejected 2026-03-31 — the July "submit hang" was StepStone refusing a duplicate),
  **1 was dead employer-side** (Canon), **2 are genuine employer-side server faults**
  (DIAS, 3dvisionlabs: instant `/application/error`, reproduced a month apart), and only **2 were
  actually fillable — both submitted**. Re-check liveness and Gmail BEFORE opening a form: 5 of 12
  needed no browser work at all.

- (2026-09-01) **Check "Schon beworben" on the posting page before anything else.** It is StepStone's own
  already-applied badge and it explains a missing apply button instantly.

- (2026-09-01) **StepStone "Schon beworben" caught two duplicates the tracker could not** (Mayfair, DaphOS.ai) — one of them
  because the card's employer byline was the PRODUCT name ("ShiftPlan") rather than the company. Add the
  badge check to the pre-packaging step, and `tracker.py check` the ATS/product name too.

- (2026-09-03) **StepStone `/confirmation/unknown` with an applicationId IS a real submit.** Drees & Sommer landed on
  `unknown` ("Deine Bewerbung ist auf dem Weg"), and both the StepStone "has been sent" mail and the
  SmartRecruiters acknowledgement arrived within three minutes. Log it Submitted and verify in Gmail;
  do not treat it as a failure.

- (2026-09-03) **StepStone's quick-apply pool is now small and heavily gated.** 22 slug sweeps (~3,000 cards) yielded
  81 unique `Schnelle Bewerbung` jobs, 24 fresh after ref-dedupe, 13 student/tech-titled, and only **2
  applied to** — the rest died on named C1/B2 or on fit (SharePoint/Excel/documentation roles).

*StepStone smart-apply — 2026-09-04 additions (wenglor, ADAC, Machineseeker all submitted)*

- **"Zusaetzliche Dateien -> Hinzufuegen" can be a PICKER of documents already in the StepStone profile**,
  not an upload target (wenglor). Its modal lists profile files with "Auswaehlen" buttons; a
  `DOM.setFileInputFiles` into the modal's input attaches nothing. The modal also **overlays the submit
  button** - `elementFromPoint` on "Bewerbung abschicken" returns the modal DIV and the click no-ops until
  "Dismiss popup" is clicked. When the cover letter is optional, dismiss and submit with the profile CV.

- **Required "Weitere Dokumente" slots are `multiple=false`.** Machineseeker's
  "vollstaendige Zeugnisse inkl. Notenuebersichten (Studium/Ausbildung/Abitur)*" takes ONE file - merge
  Transcript + B.Tech degree + HighSchoolReport with `pypdf.PdfWriter` first. Target file-input **index 1**
  (index 0 is still the CV-replace slot) via `Runtime.evaluate` -> objectId -> `DOM.setFileInputFiles`;
  `DOM.performSearch` returned nodeIds `[0,0]` here and threw "Could not find node with given id".

- **atsiQuestions ids contain colons**, so `fill_input('#genesis-form-element-:r13:')` throws. Tag them
  first (`document.querySelectorAll('input[name^="atsiQuestions"]').forEach((e,i)=>e.setAttribute('id','q_'+i))`)
  and then `fill_input('#q_0', ...)`. Worked on wenglor's Wochenstunden/Startdatum pair.

- **The Bahlsen-class address block is alive and well** (ADAC): `input[name*="street"]`, `[name*="plz"]`,
  `[name*="ort"]`, `select[name*="country"]`, `input[name*="date_of_birth"]` (ISO via native setter).
  ADAC's extra required selects use opaque `VORGABEWERT_*` values - match by option **text substring**.

- **Hit-test the submit button and treat `hit: null` as an off-screen button, not a broken form.** The real
  viewport can stay 1034x523 even after a `Browser.setWindowBounds` un-wedge; fix it with
  `cdp("Emulation.setDeviceMetricsOverride", width=1500, height=1300, deviceScaleFactor=1, mobile=False)`.

- `/confirmation/unknown?...&applicationId=<uuid>` + "Deine Bewerbung ist auf dem Weg" was again a REAL
  submit (wenglor) - the softgarden receipt and the StepStone "has been sent" mail both arrived ~3 min later.

- (2026-09-04) **StepStone "Ich bin interessiert" -> router -> Unternehmenswebsite converted again** (Octapharma ->
  `octapharma-plasma.softgarden.io`, submitted). The **coordinate** click on that button opens the tab;
  a later JS `.click()` on the same button opened nothing because the tab already existed. Check
  `list_tabs()` for an employer-domain tab before re-clicking.

- (2026-09-04) **A StepStone "Zusaetzliche Dateien -> Hinzufuegen" control can be a PICKER, not an upload target.**
  On wenglor it opens a modal listing documents already in the StepStone profile with "Auswaehlen"
  buttons; a `DOM.setFileInputFiles` into the modal's file input attaches nothing to the application.
  Worse, **the modal overlays the submit button** - `elementFromPoint` returned the modal DIV and the
  click did nothing until "Dismiss popup" was clicked. When the CL is optional, dismiss and submit.

*2026-09-06 - "Ich bin interessiert" needs a JS `.click()`, not a coordinate click*

On both Stryker (14453602) and OEDIV (14462738) the coordinate click hit-tested correctly
(`elementFromPoint` -> `SPAN|Ich bin interessiert`) and did **nothing** - no form, no URL change, over
16 s of polling. `element.click()` on the enclosing `BUTTON` (filter `rect.width>300 && rect.y>0`; the
header copy sits under the sticky bar and a third copy is off-screen at negative y) fired immediately.
Same for the **"Unternehmenswebsite"** button on the `/confirmation/success` router page.
Coordinate-clicking remains correct for the *submit* button inside the smart-apply form.

Router vs. real submit reconfirmed: Stryker -> `/confirmation/success` with **no** `applicationId`
(router; followed it to careers.stryker.com -> Workday). OEDIV -> `/confirmation/pending` ->
`/confirmation/success?userFlow=ApplyExpress` + "Bewerbung versendet!" (real; Eingangsbestaetigung from
`Bewerbung@oediv.de` arrived 23:37 the same evening).

OEDIV's inline form uses the `atsiQuestions.id:<field>.id:<field>` naming: `street` / `plz` / `ort` /
`country` (a real `<select>`, option text `Deutschland`) / `eintrittsdatum` (`type=date`, ISO
`2026-09-15`) / `freifeld3_ta` (Stundenanzahl) / `vordef_bew_feld_12` (Verbleibende Studiendauer).
The **native setter works on all of them** - no `fill_input` needed - and contact details plus the CV
come pre-filled from the user's StepStone profile.

*2026-09-09 - "submit stays disabled" is `document.hidden`, before it is anything else*

Three smart-applies (conlab 14250707, SYNGENIO 14483236, ONEJOON 14120892) showed
`Bewerbung abschicken` with `.disabled === true` after every field was filled, every section read
`Bereit`, and the 2026-07-21 contact re-touch plus the 2026-08-01 `scrollIntoView` wait had both been
applied. In all three the cause was the tab being backgrounded. **Un-wedge first, re-read second:**

```
wid = cdp("Browser.getWindowForTarget")['windowId']
cdp("Browser.setWindowBounds", windowId=wid, bounds={"windowState":"minimized"}); sleep(1.5)
cdp("Browser.setWindowBounds", windowId=wid, bounds={"windowState":"normal"});    sleep(3)
js("document.hidden")   # must read False
```

`Page.bringToFront` on its own was NOT enough whenever another tab kept re-activating itself; the
minimize/restore always worked. Only after `document.hidden` reads False is a still-disabled button
evidence of a missing required field.

*2026-09-09 - the employer's own duplicate check*

`[data-at="apply-now-section"]` rendering a **disabled "Schon beworben" button** (or being empty
altogether) is StepStone telling you the user already applied / the posting was withdrawn. Read that
section before packaging - it caught a duplicate the tracker check had missed (Autohaus W. Schouren)
and a dead GIZEH req.

- (2026-09-09) **Per-job tailored CVs are worth it where the CV is actually re-uploadable.** 3 of today's 10 got
  one (Atruvia, MTU, Airbus) — all three are portals with a real upload slot. StepStone smart-apply
  serves the *profile* CV and has no CV slot on a minimal form, so a tailored CV there is wasted work.

- (2026-09-09) **StepStone rate-limits the whole daemon, not just search.** After ~40 page loads the harness began
  returning `TimeoutError: timed out` from `Page.navigate` and `Runtime.evaluate` on stepstone.de.
  That is not a wedged tab and not a broken form — wait, or switch source. XING Easy-apply carried
  the last job of the batch once StepStone was unusable.

- (2026-09-10) **StepStone "Ich bin interessiert" on an external job is a router — and `/confirmation/unknown` is real.**
  Four of today's jobs routed through it (ZEISS → Workday, Quantum → Recruitee, Brainlab → SmartRecruiters,
  KNDS → appcast). Where it produced an inline smart-apply (Syneco), the end state was
  `/confirmation/unknown?...applicationId=<uuid>` + "Bewerbung ist auf dem Weg" — and both the StepStone
  "has been sent" mail and the employer's own softgarden confirmation arrived within the minute. `unknown`
  is a submit, not a failure.

- (2026-09-25) A StepStone apply button reading 'Ich bin interessiert' (data-testid=harmonised-apply-button) is NOT an application - clicking it lands on /job/<uuid>/application/confirmation/success whose text is 'Hat mit deiner Bewerbung alles geklappt? Falls nicht, kannst du deine Bewerbung jetzt auf der Unternehmenswebsite starten.' That URL contains both 'confirmation' and 'success' and will be logged as Submitted by anyone matching on the URL. It is an interest ping plus a router: the real route is behind the 'Unternehmenswebsite' BUTTON (no href - it must be clicked, and it opens a NEW TAB). Liebherr-Werk Ehingen 14500547 routed this way to SuccessFactors career5 ?company=LiMySLive. Always read the page TEXT, and treat 'Ich bin interessiert' as an external-redirect posting during EVALUATE, not an inline smart-apply.

## SuccessFactors

### SuccessFactors — General

*SAP SuccessFactors*

**Used by:** SAP, Siemens, Bosch, BMW, BASF, Bayer, Deutsche Telekom, Allianz, Continental, Henkel, Merck, ThyssenKrupp, many large German employers.

**How to recognize:** URL contains `successfactors.eu`, `successfactors.com`, `jobs.sap.com`, or the page has SAP branding with a career portal login.

*Common Quirks*

- Some instances have separate "Internal" and "External" candidate portals — always use **External**.

- Session timeout is typically 30 minutes.

*Quick-apply (Barmag career74.sapsf.eu, CLAAS career2.successfactors.eu pattern)*

- No `input[type=file]` exists until you click the `N:_attachIcon` element; that creates input `(N+1):_file`, which accepts CDP `DOM.setFileInputFiles` and auto-uploads.

- Picklists (`N:_input` + `N:_selectButton`) open an overlay of `<a>` options — JS `.click()` on the option works after `scrollIntoView`.

- The "Datenschutzerklärung/Nutzungsbedingungen" row must be clicked → modal → "Akzeptieren", otherwise "Bewerben" stays disabled.

- After login, old profile documents pre-attach to the new application: replace the CV via the pencil icon, delete stale cover letters via the trash icon (confirm "OK"); a new "Dokument hinzufügen" icon then appears. Pre-filled profile data (address!) may be stale — re-check against resume.md.

*SAP BTP recruiting quick-apply widget (`<company>-hr-rec-<hash>.cfapps.<region>.hana.ondemand.com`)*

- No login/account — reached via StepStone's "Hat mit deiner Bewerbung alles geklappt?" redirect page, click the **"Unternehmenswebsite" button** (not link).

- Single long scrollable page; the "PERSONAL DATA / ADDITIONAL INFORMATION / ATTACHMENTS / DATA PRIVACY STATEMENT" tabs are scroll anchors, not separate panels — clicking a tab label via JS `.click()` does nothing, use `element.scrollIntoView({block:'center'})` on a field inside that section instead.

- Every field variant (Mandatory/Collapsed/MandtSource/etc.) exists in the DOM for every possible form config; only one set is on-screen. Filter by `getBoundingClientRect()` — inactive duplicates sit at large negative coordinates (e.g. x:-9967).

- Country/source ComboBoxes: set value via native setter + `input` event to trigger the suggestion `<li>` list, `scrollIntoView({block:'center'})` the matching `<li>`, then **coordinate-click it** (JS `.click()` on the `<li>` does not register the selection).

- File uploads: plain `input[type=file]`, CDP `setFileInputFiles` works directly, no attach-icon step needed.

- The floating "Send Application" footer button needs a **coordinate click**, not JS `.click()` — a JS click silently no-ops (page looks unchanged, no error). Confirm via a "Success" overlay ("Thank you for your application/registration...") that appears ~1-2s after a real click.

*SAP EasyApply (ea-<company>.cfapps.hana.ondemand.com)*

**Used by:** Lidl Stiftung (ea-lidl.cfapps.eu20.hana.ondemand.com) and other SAP-cloud-hosted quick-apply widgets, usually reached via a StepStone "Ich bin interessiert" → "Unternehmenswebsite" redirect.

**How to recognize:** URL contains `cfapps` + `hana.ondemand.com` + `/easyapply/`.

*Flow (no login)*

1. No login/account needed — a single-page SAPUI5 form.

2. The page's own `<html>` has `overflow:hidden`; the real scroll container is `#__page1-cont` (`section.sapMPageEnableScrolling`) — set `.scrollTop` on it directly, `window.scrollBy` does nothing.

3. Don't trust input DOM order for address fields (Strasse/Hausnummer/Postleitzahl/Ort) — the `__inputN-inner` ids are NOT in visual/label order. Read each input's `getBoundingClientRect()` and match by (x,y) position against the visible labels before filling; verify with a screenshot after.

4. Dropdowns (`__selectN-hiddenInput`) are SAPUI5 comboboxes — clicking opens a `.sapMPopover`; multiple stale popovers stay in the DOM, so filter `document.querySelectorAll('.sapMPopover')` for the one with a nonzero bounding rect, find the `<li>` by text, `scrollIntoView`, then coordinate-click it. Typing into the hidden input does not filter the list.

5. File uploaders are named inputs (`EACVUploader`, `EACoverLetterUploader`, `EAOtherDocumentUploader`) — `upload_file(selector, path)` (CDP setFileInputFiles) works directly, no click-to-reveal needed.

6. Submitting ("Bewerben") does a full top-level navigation to `jobs.<company>.de/danke-fuer-deine-bewerbung?career_job_req_id=...` — that URL is the confirmation (screenshot it), the ea-cfapps form itself never shows a success state in place.

*SAP SF Quick Apply (*.p78quickapply.com) — document types don't commit*

2026-07-23 (1&1) — Guest 3-step widget (`index.html?Reqid=<n>`). Step 1 multi-upload via `#container-quickapplyUI---attachments--fileUploader-fu` works, but each file must then be tagged Anschreiben / Lebenslauf / Immatrikulationsbescheinigung. Those tags are `sap.m.ToggleButton`s (`__button5..__button10-container-quickapplyUI---attachments--UploadAttachmentList-<row>`; 5–7 = hidden responsive twins, 8–10 = visible). `getPressed()` reports `true` after `firePress()` / `setPressed(true)` / coordinate-clicks, but "Weiter" still fails with "Erforderliche(s) Dokument(e)" — **the model never receives the selection**. Treat as automation-proof: upload the files, park the tab, NeedsUser. (Note: `getBoundingClientRect` y-values below the ~551px viewport need `Emulation.setDeviceMetricsOverride` before coordinate clicks; the page has no window scroll.)

- 2026-07-02 — SAP SuccessFactors quick-apply (Barmag career74.sapsf.eu, CLAAS career2.successfactors.eu): no input[type=file] exists until you click the `N:_attachIcon` element; that creates input `(N+1):_file` which accepts CDP DOM.setFileInputFiles and auto-uploads. Picklists (`N:_input` + `N:_selectButton`) open an overlay of <a> options — JS .click() on the option works after scrollIntoView. The "Datenschutzerklärung/Nutzungsbedingungen" row must be clicked → modal → "Akzeptieren", otherwise "Bewerben" stays disabled. Quick-apply also creates an account with the standard credentials.

*SF document widgets: TWO kinds, only one takes a CDP file (2026-08-23)*

Both live on SuccessFactors, both look like "attach a document", and they behave differently:

1. **`NN:_attachIcon` + "Select a source for your file upload" dialog** (SAP career5, 50Hertz career2). Works: `cdp("Page.enable")` -> `cdp("Page.setInterceptFileChooserDialog", enabled=True)` -> click `NN:_attachIcon` -> click **"Upload from Device"** in the dialog -> `DOM.setFileInputFiles` on the dynamic input -> disable intercept. Confirms with "File is uploaded successfully" and the filename replacing the "Attach a ..." label. **Writing straight into `(NN+1):_file` without the Upload-from-Device click stages the file but never uploads it** (input.files.length becomes 1, `NN:_attachLoading` stays visible forever, synthetic change/input events do nothing).

2. **`NN:_uploadButton` + "Upload <Doc>" modal with "Choose File" and "Upload"** (career4 beldeninc / Belden-Hirschmann). **This one resisted every CDP route tried** — direct `setFileInputFiles`, Choose-File-with-intercept, and a synthetic `change` — the input holds the file, the Upload button clicks, the modal stays open and "Last Updated" never changes. Treat as a **human handoff** after 2-3 attempts; do not keep debugging it. Its modal also warns "Your current Cover Letter will be overwritten", i.e. it replaces the **profile** document that earlier submitted applications may reference.

Also: 50Hertz (`company=eliasystem`) warns **"do not include any special characters (. - _) in the title"** — upload as `Lebenslaufthe user<Name>.pdf`. Its Salutation is a typeahead (`9:_input`): focus, type, then click the `li` (`10:item2`; the English portal renders "Mr", not "Herr").

- 2026-08-23 — **`DOM.setFileInputFiles` on SF's dialog-based document widget stages the file but never uploads it.** `input.files.length` goes to 1, the "Uploading..." div stays visible forever, and synthetic `change`/`input` events do nothing, because the widget drives the upload from its own "Select a source for your file upload" dialog. The documented `Page.setInterceptFileChooserDialog` + "Upload from Device" route is the only one that works — I skipped straight to the input and burned ~8 calls plus, indirectly, the session. **Read the portal's section BEFORE improvising on an upload, not after two failures.**

- 2026-08-24 — **A SuccessFactors "Session Information - your session will expire in 6 minutes" dialog blocks every click via a `#NNN:shim` overlay, and looks exactly like dead input.** Detector: `document.elementFromPoint(...)` over a field returns `DIV#...:shim`. Fix: click "Keep Working". Cost ~6 calls on Fraunhofer before I screenshotted. Also on SF: fields scrolled with `block:'center'` end up UNDER the sticky header - `scrollBy(0,-140)` after, then click.

*2026-09-01 — RMK `jobs.<company>.com`: test `/search/` before blaming hydration*

A job DETAIL page that paints and then collapses to ~300-400 chars with no apply control is usually a
DEAD REQUISITION, not an RMK outage. Load `https://jobs.<company>.com/search/?q=<keyword>` (or
`join.<company>.com/search/?q=…`): the search page renders normally on the same tenant in the same
minute. SCHOTT's Data-Science Werkstudent was gone that way (search listed only 2 unrelated Werkstudent
roles) — while adesso's req WAS listed as live and only its detail template failed, on the bare URL,
on `/apply/`, and with `?src=`. Two different diagnoses, one cheap test.

- (2026-09-01) **SuccessFactors RMK (`jobs.<company>.com`) failed tenant-wide today.** join.schott.com and
  jobs.adesso-group.com both painted a full job page and then collapsed to 288/380 chars of body text with **no
  apply control**, on first load, after consent, and after a clean reload. Two different employers, same hour,
  same symptom = an RMK-wide render failure, not an employer problem. **Two in a row is the signal to switch
  channel** (the existing 3-4 attempt cap) rather than debug a third.

- (2026-09-01) **A dead SuccessFactors RMK detail page is usually a dead requisition — test `/search/`.** SCHOTT and adesso
  produced identical 300-400-char collapsed detail pages this morning and were both written up as one
  "RMK-wide outage". They were two different things: SCHOTT's req is withdrawn (its `/search/` renders and no
  longer lists it), adesso's is live and only its detail template fails. One cheap query separates them.

*SuccessFactors RMK (jobs.<company>.com / careers.<company>.com) — 2026-09-02*

- **The `Jetzt bewerben` link must be CLICKED, not navigated to.** `goto_url("<host>/talentcommunity/apply/<id>/?locale=de_DE")`
  bounces to the site homepage on both `jobs.dlr.de` and `careers.mahle.com`; a coordinate click on the button
  routes correctly to `career5.successfactors.eu/portalcareer?company=<tenant>`.

- Document slots are `NN:_attachIcon` → click → **"Von Gerät hochladen"** in the source dialog → the dynamic
  `(NN+1):_file` input then takes `DOM.setFileInputFiles` by objectId. Confirmation text is
  "<filename> Datei erfolgreich hochgeladen."

- **Uploads and job-specific answers are NOT persisted until Bewerben succeeds.** After a tab recovery the
  Anschreiben upload and both picklists had to be redone; only profile-level documents survived.

- **`ui5-date-picker-xweb-calendar-widget` fields:** `document.querySelector` returns the FIRST picker
  (Geburtsdatum) — index them. Setting `.value` + `change` passes DOM inspection and still fails server
  validation. Working method: walk `shadowRoot` to the inner `<input>`, coordinate-click **its** rect,
  `Input.insertText`, then **Tab** (never Enter — Enter wedged `Runtime.evaluate` target-wide; `Page.*` kept
  responding and only `close_tab` + reopen recovered it).

- (2026-09-02) **The SuccessFactors RMK apply link only works when CLICKED.** On both jobs.dlr.de and careers.mahle.com,
  `goto_url("<host>/talentcommunity/apply/<id>/")` bounces to the site homepage; coordinate-clicking
  *Jetzt bewerben* on the job page routes correctly to `career5.successfactors.eu/portalcareer?...`. Do not
  reconstruct that URL.

- (2026-09-07) **Profile documents leak between applications on SuccessFactors.** Job 2's form opened holding job
  1's tailored CV *and* job 1's German Anschreiben. Per-job tailoring is worthless unless you replace
  both slots every time and read the filename back. Give cover letters job-specific filenames — both
  letters were `Cover_Letter_<Name>.pdf`, so the only way to verify the swap was to confirm
  the slot went empty between delete and upload.

- (2026-09-10) **Groz-Beckert / EDAG-class SF forms put the submit far below a 551px viewport** — `scrollIntoView`,
  then re-measure and click, or the click lands on empty page and nothing happens (twice today).

*Allianz (career5 `company=AZGROUPPROD`) - logged-in portal apply (2026-09-11, submitted)*

- CV upload auto-parses into the profile and leaves broken required fields: truncated employer names, empty Job Title/Industry/Country per employment row, empty education rows. Re-check every parsed field.

- School picklists rarely contain the actual university → choose "Other" + fill "If other, please specify". Industry list has no Education option → "Other" for university employers.

- **SF doc-upload wipes unsaved fields (critical):** uploading the Lebenslauf triggers an AJAX refresh that CLEARS every not-yet-persisted field (city, all custom textareas, custom picklists) while keeping standard profile fields (name/address/zip/phone/email) and the uploaded doc. **Order: upload the CV FIRST, then fill all custom fields, then Bewerben.** (Standard-profile fields and the submit-validation reload preserve values; only the upload reload wipes.)

- **SF custom picklists are fuzzy-typeahead** (`input[name="<id>:_input"]`, shown as "Keine Auswahl ▾"): clicking alone doesn't render options reliably — click the input, `type_text` the answer, then click the matching item in the list that appears. Setting `.value` via JS does NOT register the selection.

- **SF file upload = native picker, no static DOM input.** Working method: `cdp("Page.enable")` → `cdp("Page.setInterceptFileChooserDialog", enabled=True)` → click the "+" upload button → the dynamic `input[type=file]` now exists, grab it via `Runtime.evaluate`(returnByValue=False) walking shadow roots and `DOM.setFileInputFiles(objectId=...)` → disable intercept. Verify by the filename text appearing in the upload box.

- Praktikum screening Qs assume a mandatory internship; for the user's **freiwilliges Praktikum** answer the "Pflichtpraktikum?/Semester/vorgeschriebene Dauer/Studienordnung hochladen" free-text boxes with "Nein, freiwilliges Praktikum …". Deutsch-Niveau field → "B1 (GER)".

*SuccessFactors portal — 2026-09-14 session and upload failures (E+H SICK ehsP, E.ON EonProd, IAV iavgmbh)*

- **CV upload stuck at "Hochladen..." / "Uploading..." with no network request** on ehsP and EonProd: the file
  reached `(N+1):_file` (files.length 1) but SF never POSTed; a synthetic `change` did not help and the widget stayed
  locked. The same code worked on mahleinter and kraussma01 the day before. Budget one attempt, then hand the
  upload to the user (one click + file pick) and fill everything else afterwards.

- (2026-09-16) (2026-09-16) On Provinzial (company=provinzial, career5) the Usercentrics consent modal renders INSIDE A SHADOW ROOT (<usercentrics-cmp-ui>), so it is invisible to querySelectorAll('[role=dialog],.modal') and to a fixed-position div scan - the page looks clean while every click on the login form is swallowed. Walk shadowRoots to find its buttons ('Nur erforderliche verwenden' / 'Alle akzeptieren'); their getBoundingClientRect values are already in page coordinates and coordinate-click normally. Shared career5 credential: rejected here (tally now clearly a coin flip).

- (2026-09-25) On SuccessFactors RMK application pages the question fields can be COLLAPSED, and a collapsed section's combobox inputs have getBoundingClientRect() of 0x0 at top 0 - so every click, pick_option and Input.insertText silently no-ops and the field keeps reading ''. There is no error and nothing looks wrong. Click 'Expand all sections' FIRST; the fields then get real geometry (210x36) and commit normally. Second trap: each combobox appends its option list to the DOM and LEAVES IT THERE, so reading '[role=option]' after touching two fields returns a merged list and pick_option reports {'missing': ...} with another field's options - press Escape and re-tag the options per field, or match against the list owned by the field's aria-owns id. The Apply control is a SPAN (id <n>:_submitBtn), not a button or input, so a /Submit|Apply/ scan over button/input finds nothing.

## Taleo

### Taleo — General

*Taleo (Oracle)*

**Used by:** Mercedes-Benz (tas-daimler.taleo.net), Deutsche Bank, Siemens Energy, Rolls-Royce, Johnson & Johnson, many legacy enterprise employers.

**How to recognize:** URL contains `taleo.net`, `oracle.com/careers`, or the form has the classic Taleo layout (left sidebar navigation, tabbed sections).

*Common Quirks*

- Taleo is **slow** — pages can take 5–10 seconds to load. Wait for full page load before interacting.

- The "Attach Resume" step often requires marking documents as **"relevant for this application"** — always check this box per document.

- File size limit is typically **5 MB per file**.

- Mercedes-Benz Taleo specifically requires: CV + cover letter + certificates + enrollment certificate + proof of standard study period.

- Some Taleo instances have a **"Candidate Profile"** vs **"Job-Specific Application"** flow — fill the profile first, then apply to the specific job.

## Teamtailor

### Teamtailor — General

*Teamtailor*

**Used by:** elunic (elunic.teamtailor.com), other `<company>.teamtailor.com` career sites.

**How to recognize:** URL contains `teamtailor.com`.

- Rails form (not React): plain value setters OK, but **consent checkbox is duplicated** — a hidden `input[name="candidate[consent_given]"][type=hidden][value=0]` comes FIRST in DOM; always select `input[type=checkbox][name="candidate[consent_given]"]` or clicks/readbacks hit the hidden one.

- **File inputs: the FIRST unnamed `input[type=file]` is the optional VIDEO question** — resume slot is `#candidate_resume_remote_url`, extra docs `#candidate_file_remote_url` (these are ids, not names). CDP `DOM.setFileInputFiles` works and auto-uploads (AJAX); verify by filename chip text. Wrong upload: chip has an icon-only remove `<button>` inside the slot container.

- Submit via `form.requestSubmit()`; success = redirect to `/applications/<uuid>/thanks/...` ("Vielen Dank für deine Bewerbung").

- Custom multi-pick questions ("Option auswählen") are not native selects; optional ones can be skipped.

- (2026-09-24) Teamtailor can gate submit behind EMAIL VERIFICATION: requestSubmit redirects to /applications/email_verification_... and the application is NOT filed until the link in the mail (from no-reply@<tenant>.teamtailor-mail.com, subject "Complete the application for <role>") is opened. Pull the URL from Gmail and goto_url it; the page then shows "We have received your application". Never log Submitted off the redirect alone. Also on the Huawei tenant: a 1x1 unnamed required text input inside the custom "How did you hear" widget shows up in an empty-required scan - it is a widget artifact, the real answer is the radio group candidate[answers_attributes][0], and it does not block submit.

## umantis

### umantis — General

*umantis (Haufe)*

**Used by:** EUROGATE (recruitingapp-346.de.umantis.com) and other German mid-size employers.

**How to recognize:** URL contains `umantis.com` / `recruitingapp-NNN.de.umantis.com`.

*Flow (no login despite "CheckLogin" URLs)*

1. Plain form with real file inputs.

2. Required Datenschutz checkbox + Datenfreigabe radio (choose "nach aktuellem Verfahren löschen").

3. Submit button: **"Bewerbung definitiv einreichen"**.

## WordPress forms

### WordPress forms — General

*Elementor forms with reCAPTCHA v3 (jatosha.com and similar WordPress sites)*

- Recognise: `div.elementor-field-type-recaptcha_v3` + `script src=recaptcha/api.js?render=explicit`. There is **no visible challenge** — nothing to solve, so filling and submitting is legitimate.

- It still blocks automation on score: submit returns `.elementor-message` = "Invalid form, reCAPTCHA validation failed." / "reCAPTCHA V3 validation failed, suspected as abusive usage". Do not retry or work around — park the tab.

- **All field values and the attached file survive the failed submit**, so a fully prefilled tab is a real handoff: the user only clicks the submit button once.

- Textareas: `fill_input` strips newlines. Use `js()` focus + `setSelectionRange(0,len)` then `cdp("Input.insertText", text=...)` to keep line breaks. Same trick avoids the umlaut/escape mangling — read the text from a UTF-8 file instead of inlining it.

## Workday

### Workday — General

*Workday*

**Used by:** Amazon, Visa, Netflix, Salesforce, Airbus, Accenture, Deloitte, PwC, Unilever, Spotify, Zalando, HelloFresh, many mid-to-large companies.

**How to recognize:** URL contains `myworkdayjobs.com`, `wd3.myworkdaysite.com`, `workday.com`, or the page structure shows a Workday-branded application form.

*Common Quirks*

- **Nested "How Did You Hear About Us?" dropdowns need coordinate clicks and a screenshot.** `js()` only ever saw 2 of 6 categories (the list virtualizes), and `.click()`, `promptOption` clicks, typing-to-filter and ArrowDown+Enter all failed to commit. What works: coordinate-click the input, **screenshot** to read the real category list, coordinate-click the category row (chevron `>` = expandable: `c. Job Sites` → `a. Stepstone / b. LinkedIn / … / e. Glassdoor / Xing`), then coordinate-click the leaf radio. Confirm via `[data-automation-id="selectedItem"]` — the search input's own `.value` stays empty even when the choice is committed (same for Country Phone Code, which renders as a pill in the parent div).

- Workday often auto-parses uploaded CVs to pre-fill form fields — review every pre-filled field for accuracy before submitting.

- CV-parser education mangling (seen 2026-07-05, NXP tenant): with two degrees on the CV, the parser can produce one Education row with the wrong school/degree/date combo (e.g. Bachelor's university name paired with the Master's start year) and silently drop the other degree entirely. Always re-derive education dates/schools from the source CV text (`pypdf` extract), not from what the form pre-filled, and add a second Education entry via "Add Another" if one is missing.

- CV-parser also drops "Company" on the most recent Work Experience row (parses Job Title + Location but leaves Company blank) — check every work-experience row, not just the first.

- A Phone Number field pre-filled with the country code baked in twice (e.g. "<phone>" when Country Phone Code is already a separate "Germany (+49)" field) fails validation — strip the leading `(+49)`/`0` and re-enter digits only.

- The "My Experience" section can be left as-is if a CV is uploaded (do not duplicate entries).

- Some Workday instances have a **"How did you hear about us?"** dropdown — select "Company Website" or "Job Board" as appropriate.

- Workday forms sometimes have hidden required fields that only appear after scrolling — always scroll to the bottom and check for validation errors.

- **Reliable text-field setter for Workday inputs:** `el.focus(); el.setSelectionRange(0, el.value.length)` in `js()`, then `cdp("Input.insertText", text=...)`. `fill_input` silently no-ops on these fields, and coordinate-click-then-type sent all three values into whichever field kept focus (the phone field ended up as `<phone><street><phone>`). Always read the value back after each set.

- **"Use My Last Application" also restores MANGLED CV-parser data into My Experience (Cadence, 2026-08-14).** Both work-experience rows had `currentlyWorkHere` wrongly checked and junk dates (1/2002–1/2009 for a Sep 2023–Feb 2024 job; 1/2001–1/2005 for Jan–May 2021), education start was 2003 instead of 2023, and a stray GPA 2.3 sat in a field `resume.md` says to leave blank. Submitting as-prefilled would have claimed he currently works a job started in 2002. **Always dump every `workExperience-*`/`education-*` value and diff against `resume.md` before continuing.**

- **Workday month/year sections clobber their neighbours.** Setting the year then the month (or vice versa) repeatedly overwrote the other section (`endDateMonth` flipped to 12 three times). Set ONE section, read the whole row back, then set the next; expect 2-3 passes. Rows created fresh via "Add Another" are far worse — a new row's year field refused every method (native setter, char events, insertText, click+Backspace+insertText) and settled on 2007/2012. **If a newly added row won't take its dates in ~3 attempts, delete the row** (`Delete` button at the row header, coordinates from a screenshot) — the uploaded CV already carries that entry, and howtologin's own rule says the section may be left as-is when a CV is attached.

- **"Meine letzte Bewerbung verwenden" / "Use My Last Application" prefills a STALE profile.** It carried a 13-month-old address (Gymnasiumstr. 11, <postcode2>) and re-attached the **old CV file** (171 KB vs the current 796 KB). Always diff the prefilled address/phone against `resume.md` and the attached file size against the package CV; delete via `button[data-automation-id="delete-file"]` and re-upload package-local files (`upload_file` on `input[data-automation-id="file-upload-input-ref"]`, `multiple=true`, one call per file).

- **Workday form inputs expose `id`, not `data-automation-id`** (`#address--addressLine1`, `#phoneNumber--phoneNumber`, `[id="primaryQuestionnaire--<hash>"]`) — `input[data-automation-id=...]` selectors fail. Only buttons/containers carry automation ids.

- **Date fields (`[id$="dateSectionMonth-input"]` etc.) are the biggest trap.** Each section keeps only the LAST character typed, and keyDown+char dispatch double-types (`7` → `77`). Native-setter + input/change **displays** the value but may not commit — the DOB was rejected as "erforderlich" while visibly showing 07/02/2000. Working method: coordinate-click the section, then `cdp("Input.insertText", text="2000")`. Single `type="char"` events work for 1-digit month/day; `insertText` is reliable for all three.

- **`pageFooterNextButton` clicks silently miss** if the coordinates are read in the same `js()` call as `scrollIntoView` — the rect is stale. Scroll first, `sleep(2)`, then re-read the rect (or screenshot once and click the pixel). A missed click looks exactly like a validation failure: same step, no error.

- Questionnaire dropdowns are nested (`Sonstiges >` expands to a radio list) — click the category, then the option row. Options render ~2-3 s after the click; a `find()` immediately after returns nothing.

*Workday / SuccessFactors deep-link + tenant-path notes (2026-08-15)*

- `eppendorf.wd502.myworkdayjobs.com` root returns **HTTP 406**; the working site path is `/de-DE/Eppendorf`. Probe candidate paths rather than concluding the tenant is dead.

- BMW SF: `careers?company=bmwag&career_job_req_id=<id>` bounces to the 857-job search. Adding `career_ns=job_listing` opens the posting directly: `careers?company=bmwag&career_ns=job_listing&career_job_req_id=<id>`.

- 2026-08-24 — **Workday's CV autofill actively corrupts the experience section; check it before continuing.** It wrote "Softwareentwickler, Alphapark..." into *Unternehmen* and left *Tätigkeitsbezeichnung* empty, and dumped BOTH education entries (<your university>, <your prior university>) into *Berufserfahrung* as jobs with empty required fields. Correct fix: delete the mis-parsed blocks (the per-block "Löschen") and retype title/company from `resume.md` - do not invent company names to satisfy the required marker. Also: Workday rejects the pre-filled `<phone>` phone format - enter the national number alone.

*Workday — 2026-08-30 (Freudenberg guest submit, NXP already-signed-in)*

- **"Sponsoring/Visum? = Ja" spawns a REQUIRED free-text explanation** (Freudenberg
  `primaryQuestionnaire--…39350003`) that only appears after the Yes is committed, so the first Weiter fails.

- **`How Did You Hear About Us?` differs per tenant**: Freudenberg is a flat list (pick "Job Board"); NXP is a
  nested multi-select where the search box needs **Enter** to filter (typing alone re-renders the categories) —
  type "Step", press Enter, and "Web - StepStone" is selected directly.

- **Umlaut button labels break `js()` string equality** — `'Übermitteln'` arrives as `'Ãœbermitteln'`. Match
  `.indexOf('bermitteln')>-1` instead.

- (2026-08-30) **Workday's "Use My Last Application" is not the only stale-data risk — the signed-in PROFILE is too.** NXP's
  profile still held Gymnasiumstr. 11 / <postcode2> as read-only text on step 1, with no inline edit, and it went out on
  the application. The CV carried the right address. If a tenant shows a read-only stale address, either fix the
  profile via Candidate Home *before* starting the flow, or accept it and record it in the row.

- (2026-08-31) **Workday month/year date pairs only take `Input.insertText`, and only in the right order:** coordinate-click
  the MONTH box, insert the month, then insert the year in the same focus (the widget auto-advances). Clicking the
  year box directly and typing writes nothing; the native setter fills the DOM but leaves React empty; typing "02"
  as two `dispatchKeyEvent` digits produced "12" and "0002".

- (2026-09-04) **Workday typeaheads reject `Input.insertText` and only take real key events.** `fieldOfStudy`,
  `jobTitle`, `companyName` and the month/year boxes all stayed empty under insertText but filled
  reliably with a per-character `Input.dispatchKeyEvent` (keyDown with `text`, then keyUp, ~40 ms
  apart). Backspace loops from the end of the field are the way to clear them.

- (2026-09-24) apobank.wd103 (Manuell bewerben guest path, no password) has a required prompt multiselect Wie haben Sie von uns erfahren? that refuses every automation route: element.click(), CDP mousePressed/Released on the inner [data-automation-id=promptLeafNode], type-to-filter, ArrowDown+Enter and Space all leave aria-label "<x> not checked" and the field on "0 items selected", while Input.insertText fills the plain text fields on the same page normally - so this is NOT a wedged Input pipeline and NOT document.hidden (both verified false/focused, keep_rendering on). Options carry aria-label "<name> not checked"/"checked" and data-automation-selected, which is the only reliable readback. Budget one or two tries on a Workday prompt multiselect, then prefill the rest and hand off.

- (2026-09-24) SOLVED the prompt-multiselect that blocked apobank.wd103 earlier the same day: Workday prompt options ignore element.click() and CDP mouse events, but they DO respond to a full SYNTHETIC event sequence dispatched in JS on the options inner [data-automation-id=promptLeafNode] - pointerover, pointerenter, pointerdown, mousedown, pointerup, mouseup, click, each with bubbles+cancelable+composed and view:window. Two further traps: (a) top-level entries can be CATEGORIES, not values - clicking Stellenboerse replaced the list with its children (Indeed, Stepstone, StudyDrive...), and the list is VIRTUALIZED so scroll the [role=listbox] to see them all; readback is the options aria-label, which flips from "<x> not checked" to "<x>, press delete to clear value", and the field text goes to "1 item selected, <x>". (b) A plain text questionnaire field filled with Input.insertText read back correct but arrived as "Keine Antwort" on the Pruefen page - only a CDP mouse click into the field followed by per-character dispatchKeyEvent type=char committed it. ALWAYS diff the Pruefen page against what you filled before Uebermitteln.

- (2026-09-24) jj.wd5 questionnaire specifics worth reusing: the base-salary question is a NUMERIC-ONLY text field that silently strips letters and concatenates the remaining digits (an answer giving an annual and an hourly figure arrives as the two numbers run together) - triple-click, Delete, assert empty, then type digits only. The How Did You Hear prompt nests LinkedIn under Job Board, not Social Network (which only holds Facebook/Instagram). The Degree prompt has 47 entries dominated by medical degrees; pick the generic entry (e.g. Masters Degree or Equivalent), and option aria-labels go EMPTY once the virtualized listbox is scrolled far, so collect option text with innerText and reset scrollTop to 0 before searching. School and Field of Study accept free text: type the value then press Enter and the field commits as 1 item selected.

- (2026-09-25) Workday 'Application Questions' pages CASCADE: answering one question injects a new required field below it, so the page cannot be completed in one pass - a Yes on 'Do you currently hold a Visa or Work Permit' adds 'expiration date of your Visa or Work Permit', a Yes on 'final year of your degree' adds 'graduation date', and a Yes on 'previously completed an internship' adds 'previously completed an internship AT <employer>' (Stryker). Save and Continue, read the Errors Found block, answer what it names, repeat. Second trap: NEVER location.reload() mid-flow - it dropped the signed-in session back to 'step 1 of 7 Create Account/Sign In' AND blanked every answer on the questions pages (My Information and the CV upload survived). If Workday shows 'Something went wrong, please refresh', expect to re-enter the question pages after signing in again. Third: match dropdowns by their question label, not by a tagged id - reusing one id leaves the OLD element in the document and getElementById returns the first match, so readbacks report the wrong field's value and answers look committed when they are not.

## XING

### XING — General

*XING (as source)*

- **Employer name: use the canonical link, never a body regex.** The job header renders "Similar jobs" cards into the same text block, so a `\n[A-Z]...GmbH\n` style match silently returns a *different* company. Reliable sources, in order: `document.querySelector('a[href^="/pages/"]')` (the employer's XING page slug), else the text immediately following the `<h1>`. Getting this wrong hides duplicates from `tracker.py check` — on 2026-08-23 five of ten picks were misattributed and three were already-applied roles.

- **"Visit employer website" is a `<button data-testid="apply-button">` with no href.** Capture the target by stubbing `window.open` before clicking:
  `window.open=function(u){window.__cap=u; return {focus(){},close(){}}}` → click the button → read `window.__cap`. No new tab, no popup blocker.

- **Already-applied detection is free:** an applied posting renders "You applied for this job on <date>" in the body — cheaper than a tracker lookup for XING-sourced roles.

- Many XING externals hop through **studyflix.de/jobs/angebote/<id>**, whose "Jetzt bewerben" href is often **stale** (umantis 403, SF 404). When it dies, search the employer board itself (`<board>/search/?q=<keyword>`) — the posting is usually live under a different id.

- Scroll-based extraction: job links are `a[href^="/jobs/"]` ending in `-<6+ digits>`; the anchor's innerText is empty, so filter on the **slug**, not the text.

*XING quick-apply ("Easy apply") — the "Application submitted" page can be a LIE*

2026-07-23 — XING quick-apply is a 3-step wizard (contact → employer questions → documents → review → **Send application**) and ends on "Application submitted", followed by a XING email "Your application was sent". **For employers whose ATS is JOIN, that is NOT a submission.** JOIN simultaneously emails "**Complete your application** — your application is almost complete but it will not be submitted until you finalize it", and `join.com/talent/applications` lists the row as **Incomplete application**. Seen on 3 of 4 XING quick-applies in one batch (Interaktiv, mtc commerce, Stella.Coach); Eggersmann went straight to "Submitted" because that employer's JOIN flow needed nothing extra.
**Finish it:** open the JOIN "Complete application" link from the email (it is a magic link that logs into the user's existing JOIN account — no password), or go to `join.com/talent/applications` → the Incomplete row → **Complete application**. The flow is: `/cv` (confirm parsed CV → *Weiter*) → `/coverLetter` (**Anschreiben upload is required**, *Weiter* stays disabled until a file is attached) → `/review` → **"Bestätigen & bewerben"** → `/success` "Bewerbung gesendet". JOIN then sends a real "Wir haben deine Bewerbung erhalten" email.
**Rule: after every XING quick-apply, check Gmail for a JOIN "Complete your application" mail before recording Submitted.**

2026-07-23 — XING quick-apply can also hard-fail: email "**Your application didn't arrive** — due to a technical error, <company> didn't receive your application". Retrying produced the same error. Root cause at IUNA AI Systems: **the user had already applied to that exact JOIN posting ~9 months earlier**, and JOIN rejects the duplicate. `tracker.py check` returned 0 rows because the application predates the tracker. **Rule: when XING quick-apply reports "didn't arrive", check `join.com/talent/applications` for an existing application before retrying — treat it as a dedupe hit, not a portal bug.**

2026-07-23 (extension-only session) - **Direct URL: `https://www.xing.com/jobs/quick-apply/<city-slug-id>`** opens the wizard without touching the job page. **The first 'Send application' click after load is always swallowed** (React handler not yet bound) - take a screenshot after a ~5 s wait, then click: the button sits at y=498 when the panel says 'Please contact the company directly for their privacy policy' and at y=521 when it lists Terms & Conditions / Privacy Policy links. The stored profile CV (Lebenslauf_<Name>.pdf) is attached automatically, so **quick-apply needs no file upload and works fully without CDP**. Success page: 'Application submitted'. A job page revisited later shows 'You applied for this job on <date>' - use that as fallback proof when the confirmation email does not arrive.
XING search from the extension: use `?keywords=<kw>&page=N` pagination (20 cards/page); scroll-based extraction does NOT work through the extension because synchronous/awaited scrollTo never re-renders the virtualised list. Accumulate results in `localStorage.__JOBS` - window variables are lost on every navigation.

XING search note (2026-07-23): the scroll-extract method works just as well for **Werkstudent/Praktikum** terms as for thesis terms — 10 keyword searches → 161 cards → **96 role-matched**, far richer than the thesis-only pass. Walk each `a[href*="/jobs/"]` up to its `article`/`li`, step `window.scrollTo(0, 0..11000)` in ~1300px increments, re-extract after each step, dedupe by href.

*XING custom-apply ("Easy apply", `xing.com/jobs/custom-apply/<slug>`)*

2026-08-30 — Distinct from quick-apply ("Apply without docs", `/jobs/quick-apply/<slug>`). **A quick-apply
URL built for a custom-apply job returns "Sorry… Something went wrong"** — that is the wrong URL, not an
outage. Use `/custom-apply/<slug>`; the page's own "Easy apply" button routes there too.

- 4 steps, all plain inputs that take the native setter: (1) `firstName.value`, `lastName.value`,
  `email.value`, `phone.value.countryCode` select (`Germany (+49)`), `phone.value.phoneNumber` **without**
  the country code; (2) `standardQuestions.0.value` = country of residence; (3) `customQuestions.N.value` —
  `input[type=date]` takes `YYYY-MM-DD` via the native setter, radios need a coordinate click, and the
  German-level select runs *Keine / Grundkenntnisse / Gute Kenntnisse / Verhandlungssicher / Fließend /
  Muttersprache* (B1 → **Grundkenntnisse**); (4) documents — the XING profile CV is pre-attached and the
  **cover-letter input is the last `input[type=file]`**, which takes a package-local PDF.
  2026-09-11: some employers make it REQUIRED - aicorn's step 4 bounced with "Please upload your cover
  letter." while U-Glow's was "(optional)". Read the label before Continue.

- Review → **Send application** is swallowed by coordinate clicks (the hit target is an inner `SPAN`); a
  JS `.click()` on the button submits. Success text: "Application submitted".

- Confirms twice: XING "Your application was sent" **and** the employer's ATS (often JOIN,
  `no-reply@msg.join.com`, "Eingang Ihrer Bewerbung"). A JOIN *"Complete your application"* mail instead
  would mean not submitted.

*The custom-apply wizard, step by step*

1. **Personal information** — first/last name, e-mail and country code come prefilled; only
   `phone.value.phoneNumber` is usually empty. `fill_input` works.

2. **Additional information** — one `<select>`, "Which country do you live in?" → *Germany*. Native
   value-setter + input/change.

3. **Info for the employer** — the employer's own questions. Types seen: `input[type=date]`,
   free-text, radio pairs (Yes/No), and a German-level `<select>`.
   **TRAP: the German-level select's visible label sits OUTSIDE its parent chain**, so a
   label-substring matcher misses it — identify that select by its OPTION SET
   (*Keine (Kenntnisse) / Muttersprache oder zweisprachig / Grundkenntnisse / Verhandlungssicher /
   Gute Kenntnisse / Fließend*) instead. **B1 = Grundkenntnisse.** English-language employers use an
   ILR-style scale instead (*None / Elementary / Limited working / Professional working / Full
   professional working / Native or bilingual*) where **B1 = Limited working proficiency**.

4. **Uploaded documents** — the CV is the XING profile CV and cannot be swapped here. To attach a
   tailored cover letter: enable `Page.setInterceptFileChooserDialog`, click **Upload file**, take the
   `backendNodeId` from `Page.fileChooserOpened` (`mode: selectSingle`), then `DOM.setFileInputFiles`.

5. **Review** → **Send application**. Success = "Application submitted" plus, within ~2 minutes,
   `jobs@mail.xing.com` "Your application was sent: <role>" and usually a JOIN/employer ack.

**Read the ack SUBJECT during verification** — it carries the employer's real job title, which can differ
from the card's (AccountOne's "Werkstudent Softwareentwickler" ack arrived as "Werkstudent PHP-Entwickler").

A reusable driver lives in the session scratchpad as `xing_apply.py` (`xing_apply(slug, cover_letter=,
answers={label-substring: value})`); it handles steps 1-5 but still needs the German-level select set by hand.

- **XING** — paginate `&page=2..4` (20 cards/page) or scroll-extract. Best source for thesis roles,
  and its thesis pool barely overlaps StepStone's — run both. The Werkstudent/AI pool refills weekly;
  the thesis pool much more slowly.

- **XING → JOIN incomplete-trap:** a XING "sent" mail with a co-arriving JOIN
  "Vervollständigen Sie Ihre Bewerbung" means **not submitted**. Finish the JOIN wizard the same
  minute — the token logs in without a password, and a 7-day-old one is dead *and* the application
  purged.

- 2026-07-02 — XING "application sent" UI is not reliable: SANOVIO application showed as sent but XING later emailed "Your application didn't arrive" (technical error) plus an expired JOIN sign-in link. After every batch, check Gmail for per-company confirmation emails and treat missing/failure emails as not submitted.

- 2026-07-13 — XING custom-apply "Send application" failed all attempts ("Something went wrong", Osbra + Quasiris) while XING quick-apply (STI) worked fine the same hour. Rule: if custom-apply errors twice, mark Blocked and retry in a later batch; don't burn attempts.

- 2026-07-13 — XING job pages: innerText extraction can grab "Similar jobs" sidebar cards; two listings were misattributed to the wrong company (Estateanfrage→Exxeta, Caya→Transdev, the latter almost re-applying to a fresh rejection). Rule: always read the h1 + the company line under it before recording company/qualifying.

- 2026-07-13 — window.open interception (override window.open, click "Visit employer website", read captured URL) reliably gets XING external apply URLs; XING popups are blocked in the harness browser.

*XING quick-apply — 2026-07-24 CDP-session mechanics*

- Direct `xing.com/jobs/quick-apply/<slug>` navigation now returns "Sorry... Something went wrong" in the CDP browser. Working flow: job page → click **Easy apply** (lands on `/jobs/custom-apply/<slug>` with ZERO inputs) → `goto_url` that same custom-apply URL → wizard renders ("Step 1 of 3"). Employers without questions render the one-pager "Apply with CV" after the click instead.

- Wizard step 3 has a real `input[type=file]` — `upload_file` works and **replaces the stored default CV for ALL future quick-applies** (after uploading the EN CV at deepeye, WeSort/Areus one-pagers carried CV_<Name>.pdf). **Always read which CV is attached before sending**; the one-pager has no swap control ("Edit your application" is a no-op).

- First "Send application"/"Continue-to-review" click after load is still swallowed — click twice.

- Canonical slug can differ from the search-card slug (Recall Space id 146666653 = "mannheim-werkstudent-marketing-content-creation") — trust the id, verify the h1.

*XING "Easy apply" — 2026-08-07 language-prescreen modal + wizard mechanics*

- **Classify first, don't guess:** open the job page (`xing.com/jobs/<slug>`), wait ~3s, read primary button. **"Easy apply" = applyable; "Visit employer website" = external (skip or chase the employer ATS).** Search-card badges are unreliable; the job-page button is authoritative. Some job pages render the button below the fold / after full load — a `?` on first check often becomes Easy-apply on a 3.5s re-check.

- **Direct `quick-apply/<slug>` URL still throws "Something went wrong"** — always go via the job page's Easy-apply button (`button.click()` in JS; the FIRST click is sometimes swallowed, re-click).

- **NEW gate: clicking Easy apply often pops a "What we need to know first" PRESCREEN modal** before any apply flow: EU work-auth radio (Yes preselected) + two `<select>`s "How good are your German/English language skills?" with options `A1–A2 (Basic) / B1-B2 (Good) / C1 (Fluent) / C2 (Expert/native)`. Set via native-setter+change (matching option `.text`). Truthful: **German = "B1-B2 (Good)", English = "C1 (Fluent)"**. The modal has an INNER scroll container — scroll it to reveal the green **"Save and continue to application"** button. It then routes to quick-apply OR the custom-apply wizard.

- **Two destinations after prescreen:** (1) **quick-apply** one-pager → CV pre-attached (Lebenslauf_<Name>.pdf), JS `button.click()` on "Send application" → "Application submitted". (2) **custom-apply** JOIN wizard: Step1 contact (phone empty → `fill_input('input[name="phone.value.phoneNumber"]','<phone>')`, country +49 preset) → Step2 employer questions → Step3 docs (CV present) → review → "Send application".

- **Step-2 answer conventions (fields are `customQuestions.N.value`):** date (Startdatum) native-setter `2026-09-01`; salary "jährliche Gehaltserwartung" `15000`; **radios need `el.click()`** (coordinate-click misses below-fold, native-set doesn't reconcile) — find the all-unchecked group and click its first (Yes) option: on-site "vor Ort"=Yes, "umzuziehen"=Yes; **Pflichtpraktikum = No** (resume line 53: freiwilliges Praktikum). Wizard language `<select>`s: German=`Grundkenntnisse` (B1), English=`Verhandlungssicher`/`Fließend`.

- **Required doc slot "Leistungsnachweis Hochschule" appears as `req=false` but blocks Continue ("Please add a file")** → `upload_file('input[type=file]', r"...\Other Docs\TranscriptofRecords_<Name>.pdf")`.

- **STOP condition — grade gate:** if Step2 has a required "Notenschnitt im Studium" that demands a whole number, do NOT fabricate (resume line 39/45: confirm GPA with the user) → Skip the role (plus10 died here 2026-08-07).

- Verify every submit in Gmail: XING `jobs@mail.xing.com` "Your application was sent" (+ usually JOIN `no-reply@msg.join.com` "erhalten"). Watch the JOIN "**Complete your application**" incomplete-trap (none this batch). XING/JOIN funnel can retitle the confirmation to a generic role (Platri IT showed "Product Owner"/"Jahrespraktikum") — the application still reached the employer.

*XING → JOIN incomplete-trap — HOW TO BEAT IT (2026-08-15)*

Some employers (Himbeer Media reproducibly, both roles) funnel XING Easy-apply into JOIN, where XING mails "Your application was sent" while JOIN mails "Vervollständigen Sie Ihre Bewerbung / Complete your application" **one second later** — the application does NOT exist until the JOIN form is finished. **Beat it in the same session:** right after the XING send, check Gmail for the JOIN completion mail and open its `join.com/auth/candidates/complete-application/<token>` link immediately. A fresh token **logs you straight into JOIN's talent area** (no password) and opens the wizard: `/cv` (Bestätige deinen Lebenslauf → Weiter) → `/coverLetter` (optional upload) → `/review` → **"Bestätigen & bewerben"** → `/success` "Bewerbung gesendet". Verify at `join.com/talent/applications` (status flips Incomplete → Submitted).
**The token dies fast — and so does the application:** the 2026-08-07 Himbeer token was invalid by 08-14, and by then the incomplete application had been **purged from the JOIN list entirely** (not resumable, not recoverable). XING will then refuse re-apply ("Application submitted"), and join.com's public board is login-walled — but the role stays applyable via its direct company URL `join.com/companies/<company>/<id>-<slug>` once a JOIN session exists. Rule: **never end a XING batch without checking for JOIN completion mails; treat the JOIN mail, not the XING mail, as the source of truth.**

- 2026-08-23 — **XING's job header leaks "Similar jobs" employer names; 5 of 10 picks had the WRONG company.** Reading the employer off the text near the `<h1>` returned Leica for io-consultants, TKMS for HELLA, Weber Food for dotsource, ITCS for Radio Tele FFH, Schwer Fittings for Groz-Beckert. Correcting them exposed **3 duplicates the wrong names had hidden** (HELLA and dotsource were the *same XING ids* already applied to; io-consultants was a title+location repost of a Rejected row). **Rule: take the employer from the canonical `a[href^="/pages/"]` link, or the text immediately after the h1 — never from a regex over the page body — and run `tracker.py check` only after that.** This is the XING twin of the 2026-08-23 StepStone "card lines misattribute employers" lesson.

- 2026-08-23 — **XING "Visit employer website" is a JS button with no href; hook `window.open` to read the target.** `window.open=function(u){window.__cap=u; return {focus(){},close(){}}}` then `.click()` the button and read `window.__cap` — returns the employer URL with no tab churn and no popup blocking. Resolved all 5 remaining employers in one pass (studyflix.de aggregator links, softgarden, bmwgroup.jobs, jobportale-frankfurt.de). Note the studyflix hops are often **stale**: technotrans returned umantis "403 Fehlende Berechtigung" and IAV/Groz-Beckert's deep links 404'd — the live posting was on the employer board's own search both times.

- 2026-08-24 — **The Werkstudent/AI pool on XING has refilled** (it was called drained on 08-23): 6 keywords x 2 pages returned 132 fresh candidates, and paginating (`&page=2..4`) is what makes XING productive. The thesis pool did NOT refill — this batch found essentially one thesis role worth taking. **Language gate killed 10 of 16 in wave 1 and 8 of 14 in wave 2 — budget for roughly 60%.** New gate phrasings to reject on sight: "Exzellente Deutschkenntnisse", "Deutschkenntnisse ab B2", "sicheres Deutsch (C2)", "Native-level German or C1+", "muttersprachlichem Niveau". Acceptable: "gute Deutsch- und Englischkenntnisse", "Good language skills in German and English which allow you to…" (functional, no level).

- 2026-08-25 — **XING's "Application submitted" page lied again, and only the batch-end Gmail check caught it.** Luelf+ Premergency showed the full success screen; 6 minutes later `jobs@mail.xing.com` sent **"Your application didn't arrive — due to a technical error, Luelf+ Premergency GmbH didn't receive your application."** Same class as the 2026-07-23 IUNA failure. The employer has no careers page and only a `vertrieb@` address, so there was no recovery route; recorded **Blocked**, and a replacement role (FES Frankfurt) was applied to instead so the batch still landed 10. **Never close a batch without the Gmail sweep — the portal UI is not evidence.**

- (2026-08-30) **XING: "Easy apply" and "Apply without docs" are different channels.** Only *Apply without docs* has a
  `xing.com/jobs/quick-apply/<slug>` URL (stored-profile CV, one click). *Easy apply* is
  `xing.com/jobs/custom-apply/<slug>` — a real 4-step wizard (contact+country code → country of residence →
  employer questions → CV/cover-letter upload → Review → **Send application**) that accepts a package-local
  Anschreiben. Hitting `/quick-apply/` on a custom-apply job returns "Sorry… Something went wrong", which is the
  **wrong URL, not an outage** — three roles were nearly written off this way. Employer questions there include a
  German-level select: on the scale *Keine / Grundkenntnisse / Gute Kenntnisse / Verhandlungssicher / Fließend /
  Muttersprache*, B1 = **Grundkenntnisse**.

- (2026-08-30) **"Visit employer website" on XING means there is NO apply control** — five roles this batch (Pirelli, Framatome,
  Radio FFH, digitalklang, VW) had only that button. It is not a dead end: FFH and digitalklang converted via the
  employer's own site/email. Budget one employer-site hunt per such row, and expect ~50% to end as NeedsUser.

- (2026-08-30) **"Visit employer website" on XING is worth the hunt more often than the 50% in the earlier note** - 3 of 5 converted
  this batch (WiBU -> HRworks, STERNAUTO -> concludis, VEMA -> mailto). The reliable route is the employer's own careers
  page -> its job board, and the role is frequently live there under a slightly different title. **Employer boards also
  hide behind a filter**: WiBU's portal showed one "Werkstudent" string until the Arbeitsverhältnis filter was applied,
  then the role appeared.

- (2026-08-31) **XING quick-apply's one-pager sends the STORED profile CV and offers no swap** ("Edit your application" is a
  no-op) — so a tailored package CV cannot be attached there. Only the `/custom-apply/` wizard has a real file
  input. Record which CV actually went out.

- (2026-08-31) **Two aggregator misattributions again, both from the same cause: the XING apply button is not unique.**
  `document.querySelector('button[data-testid="apply-button"]')` matches the *similar-jobs* cards too
  (5 nodes on the CONZE page), so a blind `[0].click()` captured a different employer's URL twice — AMCON
  resolved to *agmadata* on homepagerecruiter, CONZE to *FAKT GmbH*. **Read the captured URL's domain against
  the employer before packaging**, and prefer the employer's own careers page over the captured link.

*XING apply channels — `/custom-apply/` vs `/quick-apply/` (2026-09-01, 6 submitted through them)*

**Read the card's label; it decides the URL.**

| Card label | URL | What it sends |
|---|---|---|
| `Easy apply` | `xing.com/jobs/custom-apply/<full-slug>` | 4-step wizard, stored profile CV **+ optional cover-letter upload** |
| `Apply without docs` | `xing.com/jobs/quick-apply/<full-slug>` | one-pager, **stored profile CV only**, no cover letter |

Using the wrong one returns "Sorry… Something went wrong. Please try again later." — that string means
*wrong URL*, not an outage. The same string is what produced the whole 2026-07 "XING custom-apply is
broken" Blocked class, together with the placeholder-slug bug: **always take the full slug from a search
result**, never reconstruct it.

- (2026-09-01) **A wrong XING slug is indistinguishable from a dead posting.** `xing.com/jobs/x-<id>` (placeholder slug)
  renders "This job ad isn't available" for a job that is perfectly live — verified by loading the same id with
  its real slug seconds later. This produced **7 consecutive false "expired" verdicts** on the blocked-row
  backlog before I sanity-checked the URL form against a known-live job. StepStone ignores the slug segment;
  **XING does not**. Never conclude a XING posting is dead without the real slug, and keep the full slug in the
  tracker ref rather than the bare id.

- (2026-09-01) **XING's "Visit employer website" button is frequently a DEAD CLICK** — it opened zero new tabs and did not
  navigate on 5 of 5 attempts this batch (OpenKnowledge, Deutsche Börse, MAC IT-Solutions, Miele, nextbike). It
  is not a signal that no route exists: every one of those five had a live employer route found by going to the
  company's own careers page directly. Budget one employer-site hunt and skip the button entirely.

- (2026-09-01) **A thesis with no apply channel can still have a door: the employer's own Initiativbewerbung.** Pan Dacom's
  KI-Wissensassistent thesis exists only on XING (dead "Visit employer website", `/custom-apply/` and
  `/quick-apply/` both error) and is not on the employer board — but pandacom.de invites a speculative
  application, and the portal's Anschreiben field let me name the XING id and the exact topic. Ack mail arrived
  in 4 minutes. Use this only when the role is genuinely unreachable, and say so in the row.

- (2026-09-01) **XING search PAGE 1 is the duplicate graveyard; the fresh pool starts on page 2.** Every keyword's page 1
  was ~100% already-applied, and the whole batch's fresh finds came from `&page=2..4`. The earlier
  "the clean pool is dry" verdicts in this file were partly a pagination failure, not an empty market.
  **Always sweep pages 2-4 before concluding a source is mined.** StepStone, by contrast, really was dry:
  every student-titled `am=INTERNAL` result across 6 slugs was already applied to.

- (2026-09-01) **"Easy apply" and "Apply without docs" are DIFFERENT URLs, and the wrong one looks like an outage.**
  `Easy apply` → `xing.com/jobs/custom-apply/<slug>` (4-step wizard, real cover-letter slot).
  `Apply without docs` → `xing.com/jobs/quick-apply/<slug>` (one-pager, stored CV only). Driving DSA's
  quick-apply job through `/custom-apply/` returned "Sorry… Something went wrong" — read the card's label
  and pick the URL from it.

- (2026-09-01) **The old "XING custom-apply is broken" Blocked class was the WRONG-SLUG bug all along.** Quasiris
  (Blocked 2026-07-13 and again 2026-08-19 on "Something went wrong") submitted first try today through
  the real slug, and SPiNE's route works too (it is now skipped only on a named B2). Re-check every
  remaining XING Blocked row by finding its real slug in a search result rather than reconstructing a URL.

- (2026-09-01) **When a XING card is a dead end, the employer's board usually has a BETTER live req — retarget, don't
  drop.** Three for three today: Primetals' missing "Werkstudent KI" → live `Werkstudent DevOps/MLOps`
  (submitted); RENK's "Digital Technology" → live `Werkstudent Softwareentwicklung und KI` (submitted);
  FZI's missing Datenarchitektur thesis → live KIMONO imaging thesis (packaged). Record the retarget in the
  row so the ref still traces back to the card that found it.

- (2026-09-01) **Read the confirmation mail's SUBJECT, not just its existence.** AccountOne's XING card said
  "Werkstudent Softwareentwickler (m/w/d)" and the ack said **"Werkstudent PHP-Entwickler (m/w/d)"** — a
  stack that is not in resume.md. The verification sweep is also a last fit check.

*XING custom-apply — employer question caps (2026-09-02)*

`customQuestions.N.value` inputs can be **length- and type-capped without any visible hint**: Leisure One's
"jährliche Gehaltserwartung" is `maxlength=16` AND numeric-only ("Enter a whole number"). Read `.maxLength`
before composing an answer. `Input.insertText` CONCATENATES onto an existing value — clear with a loop of
~20 `Input.dispatchKeyEvent` Backspaces from the field end; triple-click + insertText does not replace.
Employer ATS behind the wizard is worth recording: KlimaInvest → **Factorial**, Leisure One → **JOIN**
(so the latter shows on `join.com/talent/applications` for future dedupe).

- (2026-09-02) **XING is still the thesis engine; LinkedIn is not.** A 6-keyword x 3-page XING sweep on thesis terms
  (`Masterarbeit KI`, `Abschlussarbeit Machine Learning`, `Master Thesis AI`, `Masterarbeit Softwareentwicklung`,
  `Abschlussarbeit Data Science`, `Masterarbeit Computer Vision`) returned **171 unique thesis slugs, 65 fresh
  by id, 25 clean after the language screen**. The same effort on LinkedIn (`Masterarbeit`/`Abschlussarbeit`/
  `Master Thesis`, Germany, last 7 days, 3 pages each) returned **109 rows of which ~10 were even technical and
  ZERO were real theses** - its relevance ranking ignores the keyword entirely. Use LinkedIn only for
  Werkstudent/Intern titles, never for thesis terms.

- (2026-09-02) **XING `/custom-apply/` employer questions can be silently length- and type-capped.** Leisure One's
  "jaehrliche Gehaltserwartung" is `maxlength=16` **and** numeric-only ("Enter a whole number") - a sentence like
  "ca. 15.000 EUR brutto p.a." is truncated mid-word and then rejected. Read `maxLength` before composing an
  answer, and expect bare numbers on salary fields.

- (2026-09-02) **A req that is not on the employer's live board is a dead repost - especially when the title echoes a
  rejection.** ZEISS's XING card "Internship Multimodal AI for Video Understanding" is absent from
  `zeissgroup.wd3.myworkdayjobs.com/en-US/External` under both `Multimodal` and `Video Understanding`, and
  JR_1049138 "Internship - Deep Learning for Video Understanding" was applied to and rejected 2026-05-19. Two
  signals together = hard skip. (Also: the ZEISS Workday site path is **`/en-US/External`**; `Zeiss_Careers`,
  `ZEISS_Careers`, `Careers` and `zeiss_careers` all 404.)

- (2026-09-03) **THE HEADLINE LESSON: a XING job body can silently OMIT the language line the employer page carries.**
  Five roles passed the language screen on XING and were killed only on the employer's own page:
  nimax (Personio: "mindestens Deutschniveau B2"), webit!/ITsax ("B2-Niveau"), Wilken (Personio:
  "Deutsch- und Englischkenntnisse auf mindestens B2-Niveau"), NewTec (career.newtec.de: "Deutschkenntnisse
  auf C1-Niveau"), WebID (softgarden: "mindestens B2"). XING truncates the description, and the language
  line usually sits at the END of the requirements block, so it is exactly what gets cut. **Never treat a
  clean XING body as a clean language verdict — re-screen on the employer page before packaging.** This
  cost roughly a third of the day's shortlist and is a stronger version of the existing
  "the employer's own posting text beats every aggregator badge" rule.

- (2026-09-03) **The XING "Visit employer website"-only class was 100% of this batch's shortlist** (15 of 15 qualified
  XING rows had no quick-/custom-apply control). Outcome of the 15 employer-site hunts: 4 submitted,
  2 account walls, 5 language gates found only on the employer page, 3 dead reposts, 1 broken tenant.
  Budget one hunt each, and expect the language re-screen to be the main thing it buys you.

- (2026-09-04) **XING's "Visit employer website" button worked 5 of 5 times this batch** (SAP, adesso, VetterTec,
  Krones, TAKTIQ, Debeka, Hartmann) via a coordinate click at the button's own rect, opening a new
  tab whose URL is the real route. That contradicts the 2026-09-01 "dead click" note: click it by
  coordinates from `getBoundingClientRect`, not by `.click()`, and read the new tab's URL. It is also
  the only way to reach a req that the employer's own search does not index - SAP's Signavio req was
  invisible to `jobs.sap.com/search` yet the button produced its exact URL.

- (2026-09-04) **The XING-body language trap struck again, and this time it hid the whole Profil block.** Krones'
  XING card carried no requirements at all; krones.com then showed Maschinenbau/Industrial
  Engineering, "sehr gute CAD-Kenntnisse (Solid Edge)", C# and "Sehr gute Deutsch- und
  Englischkenntnisse". Three disqualifiers, none visible on XING. Same for MTU (Maschinenbau +
  Sinumerik/Heidenhain + Siemens NX). **On XING, an "About this job" body under ~1500 chars with no
  Profil section means the posting is truncated - open the employer page before qualifying.**

- (2026-09-04) **Retarget a dead req to the employer's live board and say so in the row.** Debeka's XING
  "Werkstudent Testautomatisierung" is absent from debeka.wd3 under three searches; the live
  JR11384 "Werkstudent Software-Developer" is a better fit at 20.06 EUR/h and submitted first try
  through the Workday guest path (5 steps, zero password inputs).

- (2026-09-04) **XING card extraction returns EMPTY `innerText` while `document.hidden === true`, but hrefs still
  work.** A sweep that keyed on text length silently stored nothing across 40 pages twice. The slug
  itself carries location + title, which is enough for the whole ROLE/TECH/BAD screen - drive the first
  pass off slugs, and only un-wedge when you actually need body text. 493 slugs came out of 10 keywords
  x 4 pages this way.

- (2026-09-04) **The gate rate was ~60% on XING and ~75% on the StepStone shortlist**, but the *dead-req* rate was the
  real cost this batch: 3 of 12 XING employer routes were filled positions and 2 more had no apply control
  at all (IABG's board is unlistable; BHS has no online form). Budget the employer-site hunt at ~50%.

- (2026-09-05) **The XING apply-button trap bit again in a new way: an EMPTY-text primary button.** On the Mensch und
  Maschine card `button[data-testid="apply-button"]` returned 8 nodes, six with zero size and the first two
  with empty innerText; a blind `[0].click()` captured **REMS**' apply URL. Filter to `width>0` **and**
  non-empty innerText, and verify the captured domain against the employer before packaging.

*2026-09-06 - capture XING's employer/apply URL with a `window.open` hook*

`button[data-testid="apply-button"]` whose label is **"Visit employer website"** opens the employer URL
through `window.open`, and in this harness that popup is **silently blocked**: a hit-tested coordinate
click on the button (`elementFromPoint` correctly returns the SPAN) produces no new tab, no navigation
and no error, and the URL appears nowhere in the DOM or in `__NEXT_DATA__`. Four jobs stalled on this
before the fix. **Hook `window.open` before clicking and read the captured URL:**

```js
window.__opened=[]; const o=window.open;
window.open=function(u){window.__opened.push(u||'(none)');return null;};
```

then JS-`.click()` the button and read `window.__opened`. On Statista this returned
`https://jobs.ashbyhq.com/statista/<uuid>?utm_source=xing.com` in one call - the whole employer-site
hunt collapses to two `js()` calls. Use this **before** guessing career-site domains: karriere./jobs.
subdomain guesses cost several dead navigations each (`karriere.flaschenpost.de` and
`jobs.flaschenpost.de` are both NXDOMAIN; flaschenpost's board is
`flaschenpost.de/unternehmen/jobs/stellenangebote`).

Also: a XING detail page whose `document.body.innerText.length` is ~104/404 has **not** finished
hydrating - that short text is the nav/footer shell, not a dead posting. Poll until `length > 1500`
(up to ~10 s); 14 of 18 pages needed the second pass. This is separate from the `document.hidden`
empty-innerText bug.

- (2026-09-10) **A thesis-only batch needs BOTH XING and StepStone, and the XING thesis pool is largely mined out.**
  86 XING thesis cards over 6 keywords yielded only 4 live candidates — nearly every good one already had a
  tracker row (E-T-A, IAV, BMW, Porsche, FZI, Fraunhofer, MTU, dSPACE all hit a cap, a duplicate or a
  rejection). StepStone's bare `jobs/<slug>` sweeps (14 slugs, 325 cards) supplied the fresh half of the
  batch: Syneco, KNDS, Quantum-Systems, ZEISS 3D Surgical, Brainlab. **arbeitnow is useless for theses** —
  1,659 unique jobs contained exactly 2 thesis titles, against 51 on StepStone.

- (2026-09-11) **XING cards outlive the employer posting.** invenio's XING/studyflix card pointed at an
  invenio.net job id that now 404s; treat "Visit employer website" cards as unverified until the
  employer page loads.

*XING (as source) — 2026-09-14: job pages are curl-able, applyUrl included*

`curl` of `xing.com/jobs/<slug>-<id>` (browser UA) returns SSR HTML with a JSON-LD
`<script data-ch type="application/ld+json">` (title, hiringOrganization.name, datePosted, full description) AND the
Apollo state `"__typename":"UrlApplication","applyUrl":"https://..."` = the real employer route. Collect slugs
in the browser (search pages 1-4, hrefs only), then screen and resolve routes offline - 500 jobs, zero page views.
Note the regex must allow attributes: `<script[^>]*application/ld\+json[^>]*>`. studyflix applyUrls hide the employer
link in the page HTML (grep the employer domain).

- (2026-09-14) **XING via curl is the cheapest discovery path yet**: slugs collected in the browser, then JSON-LD + `applyUrl`
  fetched offline for ~320 jobs - it resolved employer routes (Personio, Rexx, d.vinci, SF RMK, studyflix->Greenhouse)
  that LinkedIn never exposes. Four of today's ten came straight from applyUrl.

- (2026-09-27) XING quick-apply cannot carry tailored documents: its 'Add new document' opens a NATIVE file picker and there is no input[type=file] anywhere in the DOM (checked shadow roots too), so the only attachment is the stored XING profile CV. When the posting names a contact address - Marquardt's did, and XING itself said 'We'll send your application to <address>' - the direct email handoff delivers the same recipient WITH the tailored Lebenslauf + Anschreiben. Prefer email over quick-apply whenever tailored docs matter and the recipient is known.

- (2026-09-27) The XING slug's job id is the LAST '-' segment (/jobs/<city>-<title>-<id>), not the first. A sweep that parsed the FIRST segment read the city as the id and returned ZERO slugs across 8 keywords x 2 pages - which reads exactly like 'the XING thesis pool is dead' and would have written the only live thesis source off for a second time. Fixing the parse turned 0 slugs into 213. Also: XING now redirects /jobs/search?keywords=X to /jobs/search/ki?... but the result cards still render, so the redirect is not the failure. Rule from section 3 confirmed again - when a source returns zero, suspect the extractor before the pool.

- (2026-09-27) A live XING 'Visit employer website' button does NOT prove the employer req is alive. Roche's 'Internship/Thesis in Global Engineering Automation' (157543731) still rendered a working apply button; it hopped via studyflix.de/jobs/angebote/497685 to roche.wd3.myworkdayjobs.com/.../202608-121014-2 which returned 'The page you are looking for doesn't exist', and a CXS API search of the Roche board ('Thesis' = 13 hits, 'Internship Engineering' = 12) had no twin. Verify the route through to the EMPLOYER page during EVALUATE, not just that XING renders a button - and use the window.open stub on apply-button INDEX 1, because index 0 belongs to a 'similar jobs' card and clicking it navigated to a completely different posting.
