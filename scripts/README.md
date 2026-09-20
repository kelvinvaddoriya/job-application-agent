# scripts/

All scripts stay flat in this folder: the prompts, the git hooks and any scheduled task call them
by these paths. Each script's docstring has the full usage — read it once, then call the script.

Stdlib-only except the document scripts, which need `python-docx`, `pypdf` and `Pillow`
(`pip install -r ../requirements.txt`).

## Tracker and dashboard
| Script | Used for |
|---|---|
| `tracker.py` | The only way to read or write the tracker CSVs: `check`, `add`, `update`, `queue`, `stats`, `emails` |
| `build_dashboard.py` | Rebuilds `progress.html` from the CSVs (`--if-stale` is a cheap no-op when nothing changed) |
| `setup_hooks.py` | Run once per clone: installs the git hooks that rebuild the dashboard after a pull or commit |
| `daily_pull.ps1` | Morning `git pull` of the email routine's Outcome updates (run by the scheduled task) |
| `setup_daily_pull_task.ps1` | Registers or updates that Windows scheduled task |

## SEARCH and EVALUATE (no browser)
| Script | Used for |
|---|---|
| `li_jobs.py` | LinkedIn guest-API sweep: `search` → `filter` (tracker dedupe) → `screen` (language gate). Edit `DEFAULT_KW` / `BAD_TITLE` / `TECH` for your market |
| `ats_probe.py` | Public ATS APIs: `boards` finds which ATS hosts a company; `personio` / `workday` / `smartrecruiters` read a posting (Personio also its required form fields) |

## PREPARE (application documents)
| Script | Used for |
|---|---|
| `mkpkg.py` | Creates an `Application_Packages/<Company_Role>/` folder: posting, CV, supporting docs, optional size cap. Map your filenames in its `DOCS` dict |
| `make_cover_letter.py` | Fills the .docx cover-letter template with five tailored paragraphs and prints the body word count |
| `docx2pdfa.ps1` | Converts a .docx to PDF/A through Word COM — plain `SaveAs` produces ~7 KB PDFs that portals reject |

## APPLY (browser)
| Script | Used for |
|---|---|
| `bh_helpers.py` | Form helpers to `exec()` inside the browser harness: `keep_rendering`, `form_snapshot`, `safe_click/fill/select`, uploads, shadow DOM, LinkedIn apply routes. Self-test: `browser-harness < tests/bh_selftest.py` |
| `creds.py` | At a login wall: does Chrome hold a saved password for this portal, and how much that proves. Reads origins and usernames only — never the encrypted password |
| `jstr.py` | Encodes non-ASCII text into a JS expression that survives the harness's encoding |
| `xing_apply.py` | Drives a XING "Easy apply" wizard end to end |

## Knowledge files
| Script | Used for |
|---|---|
| `section.py` | Prints one section of `feedback.md` / `howtologin.md` (`--list` shows all headings) |
| `addlesson.py` | Files a dated lesson under the right portal/company heading |
