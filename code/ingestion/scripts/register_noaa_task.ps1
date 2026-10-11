# Registers the 30-minute NOAA SWPC live collector in Windows Task Scheduler for the current user.
# Run once in PowerShell:  powershell -ExecutionPolicy Bypass -File code\ingestion\scripts\register_noaa_task.ps1
# Remove with:            Unregister-ScheduledTask -TaskName "NOAA SWPC live collector" -TaskPath "\space-weather-explainer\"
$ErrorActionPreference = "Stop"
$cmd = (Resolve-Path (Join-Path $PSScriptRoot "noaa_live_task.cmd")).Path

# conhost --headless keeps a console window from flashing up every hour.
$action = New-ScheduledTaskAction -Execute "conhost.exe" -Argument "--headless `"$cmd`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(7) `
    -RepetitionInterval (New-TimeSpan -Minutes 30)
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20) `
    -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "NOAA SWPC live collector" -TaskPath "\space-weather-explainer\" `
    -Action $action -Trigger $trigger -Settings $settings `
    -Description "Every-30-minute archive of NOAA SWPC live files (space-weather-explainer, code/ingestion)" -Force
