# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Report them privately through
[GitHub's private vulnerability reporting](https://github.com/kelvinvaddoriya/job-application-agent/security/advisories/new).

Include what you found, how to reproduce it, and what an attacker could do with it. You should get a
reply within a week.

## Scope

Reports are especially welcome for:

- Any path by which `scripts/creds.py` could read, decrypt or output a stored password
- Personal data (resume content, documents, tracker rows, account lists) that could end up committed
  despite `.gitignore`
- Prompt content that could cause the agent to enter credentials, create accounts or submit
  information that is not in `resume.md`
- Text from an untrusted job posting or web page that could steer the agent into actions outside the
  pipeline

Bugs in third-party job portals are out of scope. Report those to the portal's operator.
