# How to log in — lessons by portal (generalized)

Login lessons only: guest vs. account walls, sign-in paths, saved passwords and autofill, magic
links, sessions, SSO. Everything else lives in `application/feedback.md`, organised the same way.

Read one section at a login wall:
`python scripts/section.py application/howtologin.md "<Portal>"` (`--list` shows every heading).
File a new lesson with `python scripts/addlesson.py login "<Portal>" "<Company|General>" "<text>"`.

## General

*General Login Rules*

1. **Credentials** — Use only the credentials from the designated credentials file. Never invent or guess passwords. **Before any login attempt run `python scripts/creds.py check <job-url>`**: it reports whether Chrome has a saved credential for that host, which identity it is under. **Apply under ONE address everywhere** (`JOBAGENT_EMAIL`) — `check` flags a saved username that is not it, because an account created under some other address sends its confirmations to a mailbox the batch-end check cannot read. `check` also says whether the host is per-tenant (a hit proves an account) or shared (a hit proves nothing until the login is submitted). Record the outcome with `creds.py note`.

2. **Prefer guest/no-account paths** — If a site allows applying without login, skip login entirely.

3. **Account creation** — If no account exists and sign-up is straightforward (email + password, no phone verification), create one using the standard credentials. If sign-up requires phone/SMS verification or postal address verification, mark as `blocked_signup` and move on.

4. **Email verification** — If the site sends a verification link/code to email, check the inbox for it. Wait up to 60 seconds, then retry once. If still missing, mark `blocked_email_auth`.

5. **MFA / CAPTCHA** — Stop immediately. Mark `blocked_mfa` or `blocked_captcha`. Do not attempt to solve.

6. **SSO / "Sign in with Google"** — Do not use social/SSO login. Always use the email + password path.

7. **Cookie banners** — Dismiss with "Accept necessary only" or the minimal option. If only "Accept all" exists, click it and proceed.

8. **Session expiry** — If redirected to login mid-application, re-login and navigate back to the form. If the form data is lost, restart the application.

*Generic / Unknown ATS Login*

If you encounter a login page for an ATS not listed above:

1. **Look for "External Candidate" or "Externer Bewerber"** — always choose the external path.

2. **Find the email/username field** — look for `input[type=email]`, `input[name*=email]`, `input[name*=user]`, or labels containing "Email", "E-Mail", "Benutzername".

3. **Find the password field** — look for `input[type=password]`.

4. **Enter credentials** from the designated credentials file.

5. **Click the submit button** — look for buttons with text "Login", "Sign In", "Anmelden", "Log In", "Einloggen".

6. **Wait for redirect** — the site should redirect to the application form or dashboard.

If login fails:

- Check for error messages ("Invalid credentials", "Account not found").

- If "Account not found" — look for a registration/sign-up link and create an account.

- If "Invalid password" — do NOT retry more than twice. Mark `blocked_login` with the error message.

- If redirected to SSO/corporate login — mark `blocked_login` with reason "internal SSO required".

*Troubleshooting*

| Problem | Action |
|---|---|
| Login page does not load | Wait 10 seconds, reload once. If still broken, mark `blocked_login`. |
| "Account locked" message | Mark `blocked_login` with reason "account locked". Do NOT attempt reset. |
| Password reset required | Mark `blocked_login` with reason "password reset required". Ask the user. |
| Redirected to corporate SSO | Mark `blocked_login` with reason "internal SSO / corporate login required". |
| CAPTCHA appears | Mark `blocked_captcha`. Do NOT attempt to solve. |
| MFA / 2FA prompt | Mark `blocked_mfa`. Do NOT attempt to solve. |
| Email verification code needed | Check email inbox, wait up to 60 seconds. If code not found, mark `blocked_email_auth`. |
| Session expired mid-application | Re-login and navigate back. If form data is lost, restart the application. |
| "This position is no longer accepting applications" | Mark `blocked_expired` and move to next job. |
| Login works but application form does not load | Retry once. If still broken, mark `blocked_form_load_failure`. |

- **After a human hands over an authenticated tab, treat it as read-only navigation-wise:**
  `switch_tab` only, never `goto_url`, never reload. Session tokens are one-shot; reloading one
  logged the user out and cost him a second sign-in.

- **An account the user creates for one role clears the whole tenant.** Before re-treating a tenant as
  walled, load the apply URL and look for Logout / Mein Profil / Dashboard and
  `input[type=password].length`.

- **Before an APPLY cycle, dump Chrome's account-store origins** and prefer tenants he already has
  an account for — that converts the recurring Workday/SF wall class into submits. Autofill only
  fires after a real coordinate-click into the field, never on page load.

- 2026-07-14 — the user: he already has accounts on most job portals (incl. SuccessFactors career5, umantis, Workday tenants). Rule: at any ATS, try the logged-in path FIRST — open the portal and check for an active session (profile name/logout link); if a login form appears, let Chrome's saved-password autofill fill it and submit. Only if no session AND no autofill exists, mark NeedsUser (the agent itself must never type passwords or register accounts). Yesterday's 3 password-wall NeedsUser rows (technotrans, Fraunhofer SIT, DLR) were all completed by the user within hours — his accounts existed.

- 2026-08-24 (post-crash rebuild) — **Once the user creates an account on an ATS tenant, the wall is gone for every later role there — check for a live session before re-treating it as NeedsUser.** After he completed the FZI OCT application, `/Application/CheckLogin/1` for a *second* FZI role routed to `/FurtherApplication/Apply/1` with the profile prefilled and **`pw=0`**, so the agent submitted it end-to-end unaided. Same at Prodware: the iCIMS tenant that had demanded `Passwort*` + hCaptcha showed "Dashboard | Abmelden" and an already-submitted application. **Rule: at the start of any handoff rebuild, load the apply URL and read the page for Logout/Mein Profil/Dashboard and `input[type=password].length` BEFORE assuming the recorded blocker still applies — an account created for one role clears the tenant.** Note the FurtherApplication form uses DIFFERENT `form_data<N>` indices than the anonymous one, so re-map by label every time.

- (2026-08-30) **"No autofill in the email field" does NOT mean "no account".** Three NeedsUser rows (ZEISS, NXP, ABB) were
  written up as *account walls* on that inference, and all three were wrong: ~~Chrome's password store holds no ATS credentials at all (15 saved origins)~~ — **that count was
  wrong and is what produced all three rows.** It came from Chrome's *device* store (9 entries). The
  **account** store (`Login Data For Account`) holds 632, of which **83 are career portals — ~35 Workday
  tenants, incl. all three of ZEISS, NXP and ABB**. Never count origins by hand or from `chrome://settings`:
  run `python scripts/creds.py check <job-url>`, which reads every profile and both stores and also tells you
  whether a hit is trustworthy (per-tenant host) or meaningless (shared SuccessFactors host). The second test
  is **Gmail**, which proves accounts Chrome never saved: `from:myworkday.com` / `system@successfactors.eu` acknowledgements
  enumerate exactly which tenants the user already has a candidate account on (abb, nxp, zeissgroup, trumpf, turck,
  delo, kiongroup, elobau, ag/Airbus, mbda, ing, bayware, borgwarner, qualcomm, steeleurope, freudenberg,
  heidelberg, eppendorf, rosennxt, flender …). **That list is loose — verify before acting on it:**
  a 2026-08-31 sweep of `from:myworkday.com` found NO ack for bmwgroup or MULTIVAC, so two of the named
  tenants do not exist as Workday accounts at all. The sender subdomain (`<tenant>@myworkday.com`) is the
  authoritative tenant name; the prose list is not. Run that query before writing "account wall" — the row
  then reads "sign in", which is a far smaller ask, and Workday's *Use My Last Application* prefills the rest.

- (2026-08-30) **Two more "account wall" verdicts were wrong, in opposite directions.** NXP (nxp.wd3) needed no login at all —
  the user was *already signed in* and the flow jumped straight to step 1 of 5. Textron/Taleo, recorded in howtologin
  as a hard account wall, has an **"Apply as Guest"** button on the login page. Meanwhile Pirelli's SuccessFactors
  really did reject Chrome's autofilled credentials. Re-test every recorded wall; roughly half are stale.

(2026-09-06) **the user's tip, now the standard recipe: click the PASSWORD field, not the email field.** Every prior
note (creds.py's own HOW line included) said to coordinate-click the *email* input to summon Chrome
autofill. Clicking the **password** field is far more reliable: it filled BOTH fields first try on
Draeger, LEMKEN, MAHLE, HOERBIGER and FC Bayern. Two rows had previously been parked as "autofill was
rejected" when it is now clear autofill had fired correctly and the *credential* was wrong - a
materially different diagnosis. Update creds.py's HOW text to say password field.

(2026-09-06) **But 8 of 8 login attempts still failed, and the pattern is one thing:**

- (2026-09-06) **Gmail can prove an account exists that you still cannot use.** LEMKEN: two `system@successfactors.eu`
  acknowledgements (2026-07-01, 2026-07-14) prove a real lemkengmbh account - and career2 still rejected
  the saved password. FZI: two `fzi-karriereportal-no-reply@fzi.de` acknowledgements on 2026-08-24 prove a
  umantis profile - and Chrome has NO saved entry for karriere.fzi.de, so the password-field click summons
  nothing. In both cases the correct handoff note is "use Forgot password", not "create an account".

- (2026-09-06) **Re-testing did not clear a single row, but it sharpened all six.** The value was in the diagnosis:
  five rows move from "account wall, create an account" to "account EXISTS, reset the password", which is
  a much shorter task for the user. Hamburger Energienetze is worth noting separately - the req (8649) is
  still live after **9 weeks**, so the standing "prefill-then-handoff decays in about a week" rule is about
  the staged form and the session token, not necessarily about the requisition.

- (2026-09-08) **"Password rejected" is a fact with a short shelf life.** These rows carried three separate
  RE-TESTED confirmations that both saved credentials failed. One password reset by the user invalidated
  all of it. When the user says an account is fixed, re-run the login before anything else — and note
  that `creds.py check` showed the store going from 2 entries to 1, which is itself the tell that a
  reset happened.

- (2026-09-10) **The employer's own duplicate check beats the tracker.** SAP's career site answered
  "You already applied for this position" for req 69190 after sign-in, although no tracker row existed -
  an application made outside the tracker. Cost: one login, no wasted package.

- (2026-09-14) **Shared career5 credential: 1 of 1 today** (Everllence `volkswagenT45` logged in). Per-tenant Workday
  (ArianeGroup, STRONG verdict) rejected its password - stopped after one attempt to avoid a lockout.

---

# Portal sections

One `##` per ATS. Company-specific `### <Portal> — <Company>` subsections are where
your own runs accumulate; `addlesson.py` creates them.

## Ashby

### Ashby — General

*Login Flow*

Ashby **does NOT require login**. Direct application:

1. Click **"Apply"** on the job listing.

2. Fill: Name, Email, Phone, LinkedIn (optional).

3. Upload Resume.

4. Answer any custom questions.

5. Submit.

## BambooHR

### BambooHR — General

*Login Flow*

BambooHR **does NOT require login** for external applications:

1. Click **"Apply for This Job"**.

2. Fill: First Name, Last Name, Email, Phone, Address (optional).

3. Upload Resume.

4. Answer any custom questions.

5. Submit.

## Cornerstone (csod)

### Cornerstone (csod) — General

*Cornerstone (csod)*

- Guest flow works: Apply Now → 4 steps (Contact+docs / questions / privacy / submit). No login needed.

- **"You have an existing account in the system. Do you want to login?" modal appears on Next → click Cancel, guest flow continues fine.**

*Login Flow*

No login required — guest application works:

1. "Jetzt bewerben" on the requisition page → 4-step wizard (Kontakt → Fragen → Datenschutz → Senden).

2. Step 1: name/email/phone + CV upload (`input[name="resumeFileUpload"]`), cover letter (`cover_letter_file_upload`) — CDP setFileInputFiles works; filename + size appear in page text.

3. **Trap:** after entering a known email, a modal "Sie verfügen über ein Konto im System" blocks Weiter — click the modal's **Abbrechen** to continue as guest, then click Weiter again.

4. Step 2 custom questions may include required salary expectation (numeric €/year) and source radios.

5. Step 3: required privacy checkbox. Step 4: "Senden" → "Sie haben sich erfolgreich beworben".

6. 2026-09-11 Henkel (`henkel.csod.com/ux/ats/careersite/1/requisition/<id>/application?c=henkel`): single-page
   English form; a REQUIRED textarea asks how many of the 140/280 student working days are still available -
   the user-only fact, so the row went NeedsUser. Other answers: EN level scale 0-5 (4), DE (2), grad MM.YYYY.
   The days answer now lives in resume.md. Form mechanics: its text inputs carry NO `type` attribute, so
   `input[type=text]` misses them - filter on `e.type==='text'`. The CV `resumeFileUpload` input is REPLACED
   once a file lands (the widget re-renders), so re-query each file input right before `DOM.setFileInputFiles`;
   a nodeId cached before the CV upload fails with 'Could not find node'. Extra docs go to
   `attachment_upload_0_<n>_0`. Phone gets reformatted to `(+49) 157...` on its own - that is fine.
   Trap: the source radio "Job Board" opens a REQUIRED follow-up checkbox list (Profesia.sk ... Stepstone DE,
   Other - no XING) that a pre-fill scan cannot see; it only errors ("* This question is required.") after
   Submit. Pick Other, or Stepstone DE when the job came from there. These checkboxes have NO name, and the
   "Consider me for other positions" consent checkbox is in the same nameless pool - match by label text.
   Radio `name`s (`radio_<uuid>`) are REGENERATED on every page load - never replay names saved from an
   earlier load (every lookup silently misses). Resolve each group by its option labels (Henkel Website /
   Male / "...in English" / "...in german" / Germany) or, for Yes/No groups, by a question-text substring.

## Glassdoor

### Glassdoor — General

*Login Flow*

1. Click **"Anmelden"** or **"Sign In"**.

2. Enter email and password.

3. Click **"Anmelden"**.

4. Glassdoor often merges accounts with Indeed — if redirected to Indeed login, follow Indeed's flow.

*Common Quirks*

- Many Glassdoor listings redirect to external career pages — follow the target ATS's login instructions.

- Glassdoor may require an account just to view the application link.

## Greenhouse

### Greenhouse — General

*Login Flow*

Greenhouse **typically does NOT require login**. Most Greenhouse job boards allow direct application with:

- Name, Email, Phone

- Resume upload

- Optional cover letter

- Optional LinkedIn/website

*When Login IS Required*

Some companies add a login step before Greenhouse:

1. This is usually the **company's own account system**, not Greenhouse itself.

2. Follow the generic login flow: find the email/password fields, enter credentials, submit.

3. After login, you'll be redirected back to the Greenhouse application form.

## HRworks

### HRworks — General

*Login Flow*

No login — public one-page Bewerbungsformular reached via "Bewerben".

## iCIMS

### iCIMS — General

*Login Flow*

1. Click **"Apply"** on the job listing.

2. If prompted for login:
   - Enter email and password.
   - Click **"Sign In"**.

3. If no account exists:
   - Click **"Create Account"** or **"Register"**.
   - Fill: Email, Password, Name.
   - Verify email if required.

- 2026-08-24 — **Two iCIMS tenants, two different answers — always retest per tenant.** Prodware (`karriere-prodwaredag`) requires `Passwort*` + confirmation on the Kandidaten-Profil step **and** carries hCaptcha → NeedsUser. Korian (`careers-korian`) needs **no password at all** and its hCaptcha is **passive** (submitted fine with an empty `h-captcha-response`) → fully auto-submitted. The email-first step is identical on both, so the tenant only reveals itself at step 2. Korian's select2 controls: type into `input[aria-label="- Tippe um zu suchen -"]`, then dispatch a pointer-event click on the matching `li`; the native `<select>` stays empty until the option is picked. Korian also separates a *marketing* consent (`gdpr_consent_type` → **Ablehnen**) from the required processing consent (`accept_gdpr` → tick).

## Indeed

### Indeed — General

*Login Flow*

1. Navigate to `indeed.com` or `de.indeed.com`.

2. Click **"Anmelden"** or **"Sign In"**.

3. Enter email → click **"Weiter"** / **"Continue"**.

4. Indeed may send a **verification code to email** instead of asking for a password.

5. Check email for the code, enter it, and proceed.

*Common Quirks*

- Indeed often uses **passwordless login** (email code only) — be prepared to check email.

## Jobvite

### Jobvite — General

*Login Flow*

Jobvite **usually does NOT require login**:

1. Click **"Apply"**.

2. Fill: Name, Email, Phone.

3. Upload Resume.

4. Answer any screening questions.

5. Submit.

## JOIN

### JOIN — General

*Login Flow*

JOIN **does NOT require login** for basic applications:

1. Click **"Apply now"**.

2. Fill: Name, Email, Phone.

3. Upload CV.

4. Submit.

*When Login IS Required*

Some JOIN listings redirect to the company's own application system:

1. If redirected to a login page, check if it's a known ATS (Workday, SuccessFactors, etc.) and follow that ATS's login instructions.

2. If it's an unknown login wall, mark `blocked_login`.

*Common Quirks*

- **Passwordless magic link:** entering the email sends a single-use link to the MAIN Gmail. The Gmail MCP mangles the link (quoted-printable "=XX" corruption) — extract the href from Gmail **in the browser** (Chrome profiles: u/0=<handle>.kv, u/1=<handle-alt>, u/2=<handle> main). Clicking the link inside Gmail can silently consume the token ("Login link expired") — copy the href and `goto_url` it directly.

- 2026-07-02 — JOIN passwordless login: entering the email sends a single-use magic link to the MAIN gmail. The Claude Gmail MCP mangles the link (quoted-printable "=XX" bytes get decoded/corrupted) — extract the href from Gmail in the BROWSER instead (browser Chrome profile: u/0=<handle>.kv, u/1=<handle-alt>, u/2=<handle> main). Clicking the link inside Gmail can silently consume the token ("Login link expired") — copy the href and goto_url it directly. This unblocks JOIN applications (SANOVIO-type failures).

- (2026-09-12) **The JOIN magic link survives the Gmail MCP if you undo the quoted-printable damage.** `=07`, `=16`, `=a2`
  arrive decoded into control characters; re-prepending those two hex digits (`loginToken=07...`,
  `jobId=16685421`, `userRef=a2Vsdmlu...`) reconstructed a working link first try - no browser Gmail needed.

## Kenjo

### Kenjo — General

*Login Flow*

Kenjo **does NOT require login**:

1. Fill out the application form.

2. Salary field is **numeric only** — enter digits without currency symbols or text.

3. CV-only upload in most cases.

4. Submit.

## Lever

### Lever — General

*Login Flow*

Lever **does NOT require login**. Applications are submitted directly:

1. Click **"Apply for this job"**.

2. Fill: Full Name, Email, Phone, Current Company (optional), LinkedIn (optional).

3. Upload Resume.

4. Upload Cover Letter (if applicable).

5. Answer any additional questions.

6. Click **"Submit Application"**.

*Common Quirks*

- No account creation needed.

## LinkedIn

### LinkedIn — General

*Login Flow*

1. Navigate to `linkedin.com/login`.

2. Enter email in **"Email or Phone"**.

3. Enter password in **"Password"**.

4. Click **"Sign in"**.

5. LinkedIn may show a security challenge (CAPTCHA, puzzle, email verification) — if so, mark `blocked_mfa` or `blocked_captcha` as appropriate.

*Application Types*

- **External Apply:** Redirects to company career page. Follow the target ATS's login instructions.

## Oracle Recruiting Cloud

### Oracle Recruiting Cloud — General

*Oracle Recruiting Cloud (ORC, `fa-*.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience`)*

**Used by:** Dürr Gruppe (`Stellenangebote-Durr-Group`), many Oracle-HCM employers. NOT the same as Taleo — this one has a **working guest path, no password**.

## Personio

### Personio — General

*Login Flow*

Personio **does NOT require login** for most applications:

1. Click **"Jetzt bewerben"** or **"Apply for this job"**.

2. Fill: First Name, Last Name, Email, Phone (optional).

3. Upload documents (CV, Cover Letter).

4. Answer custom questions.

5. Check GDPR/privacy consent.

6. Submit.

## Phenom

### Phenom — General

*Phenom / "CSB" career sites (`careers.<company>.com/global/en/...`) — Primetals, MHI Group*

**Recognise:** `careers.<company>.com/global/en/job/<id>/<slug>` and an apply URL
`…/apply?jobSeqNo=<TENANT><id>EXTERNALENGLOBAL`. Guest apply, **no password**.

## Recruitee

### Recruitee — General

*Login Flow*

Recruitee **does NOT require login**:

1. Click **"Apply"** or **"Bewerben"**.

2. Fill: Name, Email, Phone.

3. Upload CV and other documents.

4. Answer custom questions.

5. Submit.

## Rexx

### Rexx — General

*Login Flow*

Rexx-systems usually allows direct application:

1. Fill out the application form.

2. Upload documents — **note:** hidden file inputs upload via AJAX and clear themselves. Check the page text for the filename confirmation, not `input.files`.

3. Consent checkbox (`agbs_check`) is required — always check it.

4. Submit.

## SmartRecruiters

### SmartRecruiters — General

*Login Flow*

1. Click **"Apply"** on the job page.

2. SmartRecruiters shows: **"Apply with"** options — ignore social logins.

3. Click **"Apply manually"** or scroll to the email/password form.

4. If account exists: enter email + password, click **"Sign In"**.

5. If no account: click **"Don't have an account? Sign up"**, enter email + password, verify email.

## StepStone

### StepStone — General

*Login Flow*

StepStone profile login (the user is typically already logged in):

1. Click **"Anmelden"** in the top-right corner.

2. Enter email: your `JOBAGENT_EMAIL` address.

3. Enter password.

4. Click **"Anmelden"**.

*Application Types on StepStone*

- **External redirect:** StepStone links to the company's own career page. Follow the target ATS's login instructions.

## SuccessFactors

### SuccessFactors — General

*Login Flow*

1. Navigate to the company's career portal (usually `<company>.jobs` or a SuccessFactors-hosted URL).

2. Click **"Login"**, **"Anmelden"**, or **"Sign In"** — typically in the top-right corner or on the application page itself.

3. On the login page:
   - Enter email in the **"Email"** or **"Benutzername"** field.
   - Enter password in the **"Password"** or **"Passwort"** field.

4. Click **"Log In"**, **"Anmelden"**, or **"Sign In"**.

5. If the site asks "Remember me" — do NOT check it.

*Account Creation (if no account exists)*

1. Click **"Register"**, **"Registrieren"**, or **"Create Account"**.

2. Fill in: First Name, Last Name, Email, Password.

3. Some instances ask for country — select **Germany**.

4. Submit and check email for verification link.

5. Click the verification link, then return to the career portal and log in.

*Common Quirks*

- Some SuccessFactors instances redirect to a company-specific SSO page — if it asks for a corporate ID or shows a Microsoft/Okta login, this is an **internal-only portal**. Mark `blocked_login` with reason "internal SSO required".

- The "Apply" button sometimes only appears after login.

*Quick-apply (Barmag career74.sapsf.eu, CLAAS career2.successfactors.eu pattern)*

- Quick-apply auto-creates an account with the standard credentials.

- "Konto bereits vorhanden" → an account already exists: log in with standard credentials. **The login dialog wipes JS-native-setter values — type credentials via keyboard events.**

- 2026-08-23 — **SuccessFactors ate three otherwise-good roles in one evening** (Allianz `AZGROUPPROD`, Belden/Hirschmann `beldeninc`, 50Hertz/Elia `eliasystem`) — all sign-in walls with no guest path, all reached from an employer career page that looks like a normal form until you read the "Bewerben" href. **Check the apply link's href for `successfactors` before investing in a posting**; it costs one `js()` call and saves the whole packaging step.

*SuccessFactors RMK (jobs.<company>.com / careers.<company>.com) — 2026-09-02*

- Tenants confirmed 2026-09-02: DLR = `dlrdeutsch` (career5, **account exists**, saved password works),
  MAHLE = `mahleinter` (career5, **no account** — saved career5 credential rejected, no MAHLE mail in Gmail),
  LEMKEN = `lemkengmbh` (career2, **no account**, apply button reads "Registrieren & bewerben!", no guest path).

- (2026-09-02) **Employer-board routes for thesis roles are dominated by ACCOUNT WALLS.** Of the clean shortlist, MAHLE
  (career5 `company=mahleinter`), LEMKEN (career2 `company=lemkengmbh`, button literally reads *"Registrieren &
  bewerben!"*) and Draeger all stopped on credentials, and **all three saved-credential hits were false
  positives** - the two SuccessFactors ones because the host is shared (the documented WEAK verdict), and
  Draeger's per-tenant password (STRONG verdict) is simply **stale**, even though the account provably exists
  (the user registered 27.07 and submitted 2026-08-30). **A STRONG creds.py verdict means the account exists, not
  that the stored password still works.** Package early and plan the handoff.

- (2026-09-03) **`creds.py`'s documented WEAK verdict on `career5.successfactors.eu` was proven wrong TWICE in one day.**
  The saved credential autofilled cleanly and was rejected at both `company=HOEProd` (Hoerbiger) and
  `company=fcbayernme` (FC Bayern). One shared-host credential does not open a second tenant — treat a
  career5 hit as "worth one autofill attempt", never as evidence an account exists. Both rows are recorded
  with `creds.py note --status password_rejected`.

- (2026-09-06) **The shared-SuccessFactors false positive is total, not occasional.** career5 (stromnetzh, mahleinter,
  HOEProd, fcbayernme) and career2 (lemkengmbh) all autofilled and all returned "Invalid email address or
  password". Chrome matches by host and every SF tenant shares one. **Stop treating a career5/career2
  autofill as evidence of anything.**

- (2026-09-09) **The shared `career5.successfactors.eu` credential is a coin flip, not a dead end — always try it.**
  Today it FAILED on `company=EonProd` and `company=schottag` ("Invalid email address or password")
  and SUCCEEDED on `company=mtuaeroeng`, where it opened a real profile holding a CV from 14.07.2026.
  So `creds.py`'s WEAK verdict means *test it*, not *write NeedsUser*. One login attempt costs ~4
  calls and converted a thesis at a 10,000-employee employer. Record each result with
  `creds.py note <url> --status has_account|password_rejected` so the next batch skips the retry.

- (2026-09-10) **The shared `career5.successfactors.eu` credential is a coin flip that PAYS: 2 of 3 today.**
  `company=edagengine` and `company=grozbecker` both logged in and both converted to a submit;
  `company=kraussma01` (KNDS) was rejected. Cost is ~4 calls. Record each with `creds.py note`.

*Allianz (career5 `company=AZGROUPPROD`) - logged-in portal apply (2026-09-11, submitted)*

- **Autofill firing on an SF login proves NOTHING about that tenant (2026-08-15).** Every tenant shares one host (`career5.successfactors.eu`, `career55.sapsf.eu`, …) and Chrome matches saved passwords by *host*, so it happily fills a credential saved for a different company. Funke (`company=funkeservi`) and SIGNAL IDUNA (`company=idunaverei`) both autofilled and both returned "E-Mail-Adresse oder Kennwort ungültig". Contrast Workday, where each tenant is its own hostname and an autofill really does mean an account. **On SF, always submit the login and read the result before concluding an account exists.**

*SuccessFactors portal — 2026-09-14 session and upload failures (E+H SICK ehsP, E.ON EonProd, IAV iavgmbh)*

- **Re-entering the form from the job page does NOT reliably keep the SF session.** It worked on Fraunhofer, but on
  ehsP and iavgmbh the re-entry landed on the login / guest-registration page, costing the user another sign-in.
  Once the user has signed in, never navigate that tab away from `portalcareer`; for a job-specific form, ask the user
  to sign in from the job's own apply link so the tab lands on it directly.

- (2026-09-14) Shared career4/career5 SuccessFactors credential: 2 of 2 logins worked today (Everllence, AGCO). Both profiles held
  stale documents - AGCO's had a May Anschreiben written for another job; delete stale letters before Bewerben.

## Taleo

### Taleo — General

*Login Flow*

1. Click **"Log In"** or **"Anmelden"** on the careers page.

2. On the login form:
   - Enter **"Username"** (usually the email address).
   - Enter **"Password"**.

3. Click **"Log In"** or **"Anmelden"**.

*Account Creation*

1. Click **"Register"** or **"New User"** or **"Registrieren"**.

2. Fill: Username (email), Password, First Name, Last Name, Country.

3. Some Taleo instances also ask: Phone, Address — fill from resume.

4. Accept terms, submit.

5. Check email for verification.

*Common Quirks*

- Taleo sessions expire aggressively (~15–20 min). If you get a session timeout, you must re-login and the in-progress application may be lost.

*Taleo (Oracle, *.taleo.net)*

**Used by:** Oracle Taleo career sections (e.g. Kautex/Textron `textron.taleo.net`). Reached via StepStone external redirect. "Apply Online" → `careersection/iam/accessmanagement/login.jsf`.

## Teamtailor

### Teamtailor — General

*Teamtailor*

- Guest apply works, no login: go DIRECTLY to `/jobs/<slug>/applications/new` — the job page's "Jetzt Bewerben" button only scrolls to a candidate-LOGIN form (`full_email` + Anmelden), don't confuse it with the application.

## umantis

### umantis — General

*Flow (no login despite "CheckLogin" URLs)*

4. Submitting auto-registers a umantis profile with the standard credentials.

- 2026-08-23/24 — **umantis is now a password wall, not the "no login despite CheckLogin URLs" guest flow the playbook describes.** Both tenants hit this batch (FZI `recruitingapp-5583`, Baumann `recruitingapp-5313`) render `Passwort*` as a required field on `/Application/New/1` — the form auto-registers an account on submit. Everything else prefills and uploads normally, so the right move is prefill + park + NeedsUser. **Good news: umantis parks are durable — both tabs still held every field value AND all four staged file uploads after an overnight gap**, unlike softgarden (dies in ~1h). Update to § umantis: expect a password, park confidently.

*2026-08-24 update — umantis now requires a PASSWORD (account creation)*

Two tenants this batch (FZI `recruitingapp-5583`, Baumann `recruitingapp-5313`) render **`Passwort*` as a required field** on `/Vacancies/<id>/Application/New/1`; submitting auto-registers the account. The agent must not set it → prefill everything else, park the tab, mark `NeedsUser`.

- `/Application/CheckLogin/1` **redirects straight to `/Application/New/1`** (the real form). A 403 there means the requisition is delisted, not that login is needed — verify on the employer's own board (`/Jobs/1?lang=ger&...&Search=1`).

- Required fields are marked only by `*` in the label text (`e.required` is false on all of them) — read the lines containing `*` from `document.body.innerText`.

- Field names are `form_data<N>` and **differ per tenant** — map them by walking each input to its `<label>`. Geburtsdatum has no `name` at all; find it via its label.

- Selects (`Bundesland`, `Abschluss`, `Studiengang`, `Wie sind Sie auf uns aufmerksam geworden?`) — **match options by TEXT**, values are opaque.

- Datenfreigabe radio → pick "Ich möchte, dass meine Daten nach dem aktuellen Bewerbungsverfahren gelöscht werden" (privacy-preserving).

- Separate file inputs per document type (`Bewerbungsschreiben` / `Lebenslauf` / `Weitere Dokumente` / `Foto`); `upload_file` works on each and `input.files.length` is reliable here (not AJAX).

- **Parks are NOT durable — corrected 2026-08-24.** The field values and staged uploads DO survive an overnight gap, which is misleading: the **CSRF/security token expires**, and submitting then fails with *"The form was not saved because the security token was not sent. (This also happens if you save twice.)"* — after which the form **resets to blank** and everything must be re-entered. Verified on FZI `recruitingapp-5583`: the user's submit died this way while Baumann `recruitingapp-5313`, completed in the same session it was filled, went through and confirmed by e-mail within a minute. **Rule: a umantis park is good for the current session only — hand it off the same hour, and after any handoff verify the tab reached `/Application/<n>/Confirmation` AND a confirmation e-mail arrived before recording Submitted.** A blank form plus that token error means NOT submitted; reload `/Application/New/1` and refill.

## Workday

### Workday — General

*Login Flow*

1. On the job listing page, click **"Apply"** or **"Jetzt bewerben"**.

2. Workday presents options:
   - **"Sign In"** — use this if an account exists.
   - **"Create Account"** — use this for first-time applications.
   - **"Apply with LinkedIn"** — do NOT use this.

3. If signing in:
   - Enter email in **"Email Address"**.
   - Enter password in **"Password"**.
   - Click **"Sign In"**.

4. If "Sign In" fails with "account not found", switch to **"Create Account"**.

*Account Creation*

1. Click **"Create Account"**.

2. Enter: Email, Password (must meet complexity: 8+ chars, uppercase, lowercase, number, special char).

3. Agree to terms if prompted.

4. Check email for verification — click the link.

5. Return and sign in.

*Common Quirks*

- **Guest apply is the default, not the exception — check `<job-url>/apply` BEFORE ever concluding "account wall."** The job page's "Bewerben"/"Apply" button leads to a chooser with **"Manuell bewerben" / "Apply Manually"**, which runs the full 5-step form (My Information → My Experience → Application Questions → Voluntary Disclosures → Review → "Übermitteln") with no sign-in at all. Verified 2026-08-21 on delo.wd103 (submitted end-to-end), miele.wd3, eppendorf.wd502, elobau.wd502. The `<tenant>/login` page shows empty credential boxes on these tenants and means nothing — four rows were wrongly parked as `NeedsUser` on that signal alone. Note `/apply` must be appended to the **bare** job URL; a trailing `?q=…` search param makes it bounce back to the posting.

- Each company has its own Workday tenant — credentials are **per-tenant**, not global. An account at `amazon.wd5.myworkdayjobs.com` does NOT work at `salesforce.wd1.myworkdayjobs.com`.

- **Saved-password login works end-to-end (verified TRUMPF trumpf.wd3, Cadence cadence.wd1, thyssenkrupp steeleurope.wd3, 2026-08-14).** the user's ATS passwords live in Chrome's **account store** (`Login Data For Account`, ~30 Workday tenants), not the device store — so `chrome://settings` device-password checks look empty. Autofill does **not** fire on page load: open `/<site>/login`, `scrollIntoView` the email input, then **coordinate-click it**; then click "Anmelden"/"Sign In" → `/userHome`.

- **Do NOT judge autofill by `input.value` — Chrome hides autofilled values from JS until the user interacts with the page.** On Cadence the fields read `len0` via `js()` while the screenshot showed both filled (yellow/blue highlight). Verify with ONE screenshot, then click Sign In anyway. Only treat a tenant as credential-less when the screenshot shows empty boxes (Eppendorf/Miele/QIAGEN) → `NeedsUser`.

- 2026-08-21 — **Four "account wall" NeedsUser rows were false blocks.** DELO, Miele, Eppendorf and elobau were all logged as Workday account walls on 2026-08-15/16 because that session probed `<tenant>/login` and found empty credential boxes. Workday's guest path does not live there: opening **the job's own `/apply` URL** offers "Manuell bewerben" and runs the whole 5-step form with no sign-in (DELO submitted end-to-end this way, Eingangsbestätigung received). **Rule: never conclude "Workday account wall" from the /login page — always open `<job-url>/apply` first and look for "Manuell bewerben".** Same shape of error at SIGNAL IDUNA: "results unreachable" was really just the wrong entry point (jobs.signal-iduna.de serves the job page fine; only the apply click hits the account wall).

- 2026-08-25 — **Not every Workday is an account wall — count the steps.** `heidelberg.wd502` ran a **5-step guest flow with zero password inputs** and submitted end-to-end (proof: redirect to `?Job_Application_ID=<uuid>`). The same day `abb.wd3` and `getec.wd103` both opened "Apply Manually"/"Manuell bewerben" onto **step 1 of 6 = Create Account** with 2 password fields -> NeedsUser. **Classify per tenant by the step count and `input[type=password].length` after clicking Apply; do not write off Workday wholesale.**
