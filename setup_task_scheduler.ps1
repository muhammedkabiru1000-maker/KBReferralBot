$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskName = 'KBReferralBot'
$action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument "-NoProfile -WindowStyle Hidden -Command `"Set-Location '$ScriptDir'; .\venv\Scripts\Activate.ps1; python bot.py`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId 'BUILTIN\Users' -LogonType Interactive -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force
    Write-Host "Task '$taskName' created successfully."
} catch {
    Write-Error "Failed to create scheduled task: $_"
    exit 1
}

Write-Host "To verify, run: Get-ScheduledTask -TaskName $taskName"