# Resume Knowledge Base — TEMPLATE

**Fill this in before your first batch.** This file is the *only* source of candidate facts for
the whole pipeline: SEARCH scores against it, EVALUATE rejects against it, the cover letter draws
every claim from it, and a form field with no answer here becomes `NeedsUser`, never a guess.

Keep it factual and complete. Detail that is missing here is missing from every application.
If you use the CV generators, `application/cv_data.py` repeats these facts in print-ready wording:
change a fact here first, then there, and never the other way round.

---

# Candidate

**Name:** <Full Name>
**First Name:** <First>
**Last Name:** <Last>

Current Location:
<Country>

Address:
<Street, Postcode City, Country>

Phone:
<+CC number>

Email:
<you@example.com>

Links (only URLs that actually resolve — forms ask for these and a broken one is worse than blank):
- LinkedIn: <https://linkedin.com/in/handle>
- GitHub: <https://github.com/handle>
- Portfolio: <https://your-site>

Education:

- **<Degree>**, <Institution>, <Country> (<MM/YYYY> – <present|MM/YYYY>)
  Coursework: <comma-separated>
- **<Prior degree>**, <Institution>, <Country> (<MM/YYYY> – <MM/YYYY>)
  Coursework: <comma-separated>

Expected Graduation:
<Month YYYY>

Current Status:
<e.g. Enrolled full-time and eligible for Internship, Thesis, and Working Student positions.>

Earliest Start Date:
<date or "immediately">

Notice Period:
<none | N weeks>

---

# Work Authorization and Legal

These answers get typed into forms verbatim. Every one must be **true** — a truthful answer that
looks like a disadvantage is still the answer. Leave a line blank rather than guessing it.

- Work permit for <country>: <Yes/No — permit type>
- Visa sponsorship required now: <Yes/No>
- Visa sponsorship required in future: <Yes/No>
- Age 18+: <Yes/No>
- Driving licence: <class or None>
- Criminal record / clearance: <as applicable>

---

# Languages

State the CEFR level you can defend, not the one you wish you had. The language gate is the single
biggest filter in the pipeline (see `feedback.md` § EVALUATE) and a false level ends in a failed
interview, not a job.

- <Language>: <A1–C2 / Native>
- <Language>: <A1–C2 / Native>

---

# Skills

**Primary:** <the stack you would be hired for>
**Secondary:** <what you can work in>
**Tools:** <version control, cloud, CI, etc.>

Only list what you could answer a question about. EVALUATE scores a job against this list, so
padding it here produces bad matches, not more offers.

---

# Experience

Repeat this block per role. One line of context, then what you actually built and what it did.

## <Job Title> — <Employer>, <Location> (<MM/YYYY> – <MM/YYYY>)

- <What you built, the technology, and the measurable result.>
- <Second responsibility or outcome.>

---

# Projects

Repeat per project. Cover letters lean on these hardest, so write the *decisions*, not the
technology list — "chose X over Y because Z" is what makes a paragraph readable.

## <Project Name> (<YYYY>)

- Problem: <what it solves>
- Built: <architecture, models, datasets, stack — be specific>
- Result: <metric, deployment, or what you learned>
- Link: <repo or demo, if public>

---

# Certifications and Publications

- <name, issuer, year>

---

# Supporting Documents

Files kept in `Other Docs/`, copied into a package folder by `mkpkg.py --docs`. Map the key to the
filename you actually have:

| Key | File |
|---|---|
| `transcript` | <TranscriptOfRecords.pdf> |
| `immat` | <EnrollmentCertificate.pdf> |
| `zeugnis` | <References.pdf> |
| `degree` | <DegreeCertificate.pdf> |

---

# Standing Answers

The questions every second form asks. Decide them once here so no batch has to ask you mid-run.

- Preferred role types: <Working Student / Internship / Thesis / Full-time>
- Hours per week available: <N>
- Willing to relocate: <Yes/No>
- Remote / hybrid / on-site: <preference>
- Salary or wage expectation: <figure or range, per hour or per year>
- "How did you hear about us?": <any — pick whatever the dropdown offers>
- Target locations: <cities or "anywhere in X">
