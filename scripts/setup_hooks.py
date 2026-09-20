"""Per-clone local git setup: the dashboard rebuild hooks.

The hooks live under `.git/`, which git never clones or pushes, so every
clone that wants a dashboard has to run this once.

progress.html is gitignored (it embeds the full tracker, so it is never
pushed) - which means it can only be rebuilt where it lives. post-merge and
post-commit run `build_dashboard.py --if-stale`, so a `git pull` that brings
in the routine's overnight Outcome updates, or a local batch commit, refreshes
the dashboard on the spot. The hook is a no-op in clones that have no
progress.html - including the daily email-check routine's checkout.

Idempotent: safe to run at the top of any session or CI job.

This script used to register a cell-level merge driver as well, because the
tracker was a binary xlsx that two writers shared. The tracker became two
CSVs split by writer on 2026-09-07 - applications.csv is written by local
batches, outcomes.csv by the routine - so git merges them as ordinary text
and no driver is needed.
"""
import os
import stat
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKER = "# managed by scripts/setup_hooks.py"
HOOK_BODY = """#!/bin/sh
{marker}
# Rebuild the gitignored dashboard whenever this checkout's tracker CSVs
# changed - a pull from the daily email-check routine, or a local commit.
# --if-stale makes it a no-op when nothing moved or no dashboard exists.
exec python scripts/build_dashboard.py --if-stale
""".format(marker=MARKER)
HOOKS = ("post-merge", "post-commit")
# the marker written by the pre-2026-09-07 version of this script
OLD_MARKER = "# managed by scripts/setup_merge_driver.py"


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args],
                          capture_output=True, text=True)


def install_hooks():
    hooks_dir = git("rev-parse", "--git-path", "hooks").stdout.strip()
    hooks_dir = os.path.join(ROOT, hooks_dir)
    os.makedirs(hooks_dir, exist_ok=True)
    for name in HOOKS:
        path = os.path.join(hooks_dir, name)
        if os.path.exists(path):
            body = open(path).read()
            if MARKER not in body and OLD_MARKER not in body:
                print(f"WARN: {name} hook exists and is not ours - left untouched")
                continue
        with open(path, "w", newline="\n") as fh:
            fh.write(HOOK_BODY)
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP)
        print(f"dashboard hook '{name}' installed")


def drop_stale_merge_driver():
    """Remove the xlsx merge driver this script used to register.

    Harmless if left behind - nothing carries `merge=tracker-xlsx` any more -
    but it points at a script that no longer exists, so clear it.
    """
    if git("config", "--get", "merge.tracker-xlsx.driver").returncode == 0:
        git("config", "--remove-section", "merge.tracker-xlsx")
        print("removed the obsolete tracker-xlsx merge driver")


def main():
    if git("rev-parse", "--git-dir").returncode:
        sys.exit("not a git repository")
    install_hooks()
    drop_stale_merge_driver()


if __name__ == "__main__":
    main()
