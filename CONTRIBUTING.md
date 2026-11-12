# Contributing

Thanks for helping. The most useful contributions are usually portal lessons: a short, specific note
about how a job portal behaves that would have saved a failed application.

## Portal lessons

1. Find the right section first:

   ```bash
   python scripts/section.py application/feedback.md --list
   ```

2. Add the lesson with the script so it lands under the right heading with a date:

   ```bash
   python scripts/addlesson.py feedback "<Portal>" "General" "<what happened and what works>"
   python scripts/addlesson.py login    "<Portal>" "General" "<login-related lesson>"
   ```

Guidelines:

- **Login lessons go in `howtologin.md`; everything else goes in `feedback.md`.** Never both.
- **Submit portal-wide lessons only** (`### <Portal> — General`). Company-specific sections stay in
  your own fork, because they tend to identify the applicant.
- **One portal, one `##` heading.** Add to the existing section instead of creating a second one.
  If a bullet is out of date, fix it where it is instead of adding a contradicting one.
- **Be concrete.** Name the field, the selector or the error, and what fixed it.
- **No personal data.** No names, email addresses, application IDs, phone numbers or screenshots of
  filled-in forms.

## Code changes

- Keep the tracker, discovery and browser-helper scripts dependency-free (standard library only).
- Do not reformat, re-sort or re-quote the tracker CSVs. They are kept to one line per record so
  that git merges stay clean.
- Each fact has one home (see the table in `CLAUDE.md`). If a change would put the same rule in two
  files, choose one.
- Run the tests before opening a pull request:

  ```bash
  PYTHONUTF8=1 python tests/test_strip_marks.py
  PYTHONUTF8=1 python tests/test_cv_build.py
  ```

  If you changed `scripts/bh_helpers.py`, also run `tests/bh_selftest.py` with a browser harness.

## Pull requests

Keep pull requests small and focused, and explain in the description what failed and how the change
fixes it. Changes that make the agent skip a trust boundary (passwords, account creation, SSO,
CAPTCHAs) or invent candidate facts will not be accepted.
