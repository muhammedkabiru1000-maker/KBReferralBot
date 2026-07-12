$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$serviceName = 'KBReferralBot'
$pythonPath = Join-Path $ScriptDir 'venv\Scripts\python.exe'
$botPath = Join-Path $ScriptDir 'bot.py'

if (-not (Test-Path $pythonPath)) {
    Write-Error "Python executable not found at $pythonPath. Create your virtualenv first."
    exit 1
}

if (-not (Get-Command nssm.exe -ErrorAction SilentlyContinue)) {
    Write-Error "NSSM not installed or not on PATH. Run install_nssm.ps1 first."
    exit 1
}

& nssm install $serviceName $pythonPath $botPath
& nssm set $serviceName AppDirectory $ScriptDir
& nssm set $serviceName AppStdout "${ScriptDir}\logs\out.log"
& nssm set $serviceName AppStderr "${ScriptDir}\logs\err.log"
& nssm set $serviceName AppRotateFiles 1

Write-Host "NSSM service '$serviceName' created. Start it with: nssm start $serviceName"