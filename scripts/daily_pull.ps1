# Daily catch-up on the email-check routine's overnight push.
#
# The email-check routine writes Outcome columns into
# application/outcomes.csv and pushes to main at ~08:00 Europe/Berlin. It
# cannot refresh progress.html - the dashboard is gitignored and only exists
# in this clone. So: pull, and let the post-merge hook rebuild it.
#
# Registered as the Scheduled Task "JobAutomation daily pull" by
# scripts/setup_daily_pull_task.ps1. Runs at 08:30 local, catch-up enabled.
#
# --ff-only on purpose: if local work is uncommitted or diverged, this stops
# and logs instead of starting a merge nobody is watching. The tracker has two
# writers; an unattended merge is exactly what we don't want.

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$log  = Join-Path $root 'tmp\daily_pull.log'
New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null

function Log($msg) { Add-Content -Path $log -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg" -Encoding utf8 }

Log "--- pull start ---"
Set-Location $root

$before = (& git rev-parse HEAD)
$out = & git pull --ff-only 2>&1 | Out-String
Log ($out.Trim())

if ($LASTEXITCODE -ne 0) {
    Log "PULL FAILED (exit $LASTEXITCODE) - dashboard left as is"
    exit 1
}

$after = (& git rev-parse HEAD)
if ($before -eq $after) {
    Log "already up to date"
} else {
    Log "$before -> $after"
}

# Belt and braces: the post-merge hook already ran build_dashboard.py, but
# --if-stale is a stat call when there is nothing to do, so run it anyway in
# case the hook was missing or the pull was a no-op after a manual edit.
$build = & python scripts/build_dashboard.py --if-stale 2>&1 | Out-String
if ($build.Trim()) { Log $build.Trim() } else { Log "dashboard already current" }
Log "--- pull done ---"
