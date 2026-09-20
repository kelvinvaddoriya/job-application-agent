# Register (or re-register) the Windows Scheduled Task that runs
# scripts/daily_pull.ps1 each morning. Idempotent - re-run to update.
#
# Runs as the interactive user, so git reuses the credential helper and
# python is the same one on your PATH. No stored password.

$ErrorActionPreference = 'Stop'
$root   = Split-Path -Parent $PSScriptRoot
$script = Join-Path $root 'scripts\daily_pull.ps1'
$name   = 'JobAutomation daily pull'

$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`"" `
    -WorkingDirectory $root

# 08:30 local - the email-check routine fires 08:00 Europe/Berlin and takes
# a few minutes, so this leaves a comfortable margin.
$trigger = New-ScheduledTaskTrigger -Daily -At '08:30'

# StartWhenAvailable: if the machine was asleep or off at 08:30, run at the
# next opportunity instead of skipping the day.
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal `
    -Description 'Pulls the daily email-check routine''s Outcome updates and rebuilds progress.html via the post-merge hook.' `
    -Force | Out-Null

$t = Get-ScheduledTask -TaskName $name
"registered: $($t.TaskName)  state=$($t.State)"
"next run:   $((Get-ScheduledTaskInfo -TaskName $name).NextRunTime)"
