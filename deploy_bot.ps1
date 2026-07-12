$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-ErrorAndExit($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Info "Project path: $ScriptDir"
Write-Info "Running as administrator: $IsAdmin"

# Check .env
$envPath = Join-Path $ScriptDir '.env'
if (-not (Test-Path $envPath)) {
    Write-ErrorAndExit "Missing .env file. Create one with BOT_TOKEN, CHANNEL_USERNAME, ADMIN_ID."
}

# Create venv if missing
$venvPath = Join-Path $ScriptDir 'venv'
$pythonExe = Join-Path $venvPath 'Scripts\python.exe'
if (-not (Test-Path $venvPath)) {
    Write-Info "Creating Python virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Failed to create venv." }
}

if (-not (Test-Path $pythonExe)) {
    Write-ErrorAndExit "Python executable not found at $pythonExe. Ensure Python is installed and accessible."
}

Write-Info "Installing dependencies..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Failed to install requirements." }

# Create logs folder
$logsDir = Join-Path $ScriptDir 'logs'
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

# Task Scheduler setup
$taskName = 'KBReferralBot'
$botPath = Join-Path $ScriptDir 'bot.py'
$runCmdPath = Join-Path $ScriptDir 'run_bot.cmd'
$runCmdContent = @"
@echo off
cd /d "$ScriptDir"
"$pythonExe" "$botPath"
"@
Set-Content -Path $runCmdPath -Value $runCmdContent -Encoding ASCII

Write-Info "Creating Task Scheduler task '$taskName'..."
$taskCommand = "`"$runCmdPath`""
$taskCreated = $false

if ($IsAdmin) {
    $action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument "-NoProfile -WindowStyle Hidden -Command `"Set-Location '$ScriptDir'; .\\venv\\Scripts\\Activate.ps1; python bot.py`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $principal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive -RunLevel Highest
    try {
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force -ErrorAction Stop | Out-Null
        Write-Info "Task Scheduler task created."
        $taskCreated = $true
    } catch {
        Write-Warn "Could not create scheduled task with Register-ScheduledTask: $_"
    }
}

if (-not $taskCreated) {
    Write-Info "Trying schtasks.exe fallback for current user."
    $debugPath = Join-Path $ScriptDir 'deploy_task_debug.txt'
    Write-Info "Schtasks debug log: $debugPath"
    try {
        $result = schtasks.exe /Create /TN "$taskName" /TR $taskCommand /SC ONLOGON /RL LIMITED /F 2>&1
        $result | ForEach-Object { Write-Info "schtasks: $_" }
        $result | Out-File -FilePath $debugPath -Encoding utf8 -Force
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Task Scheduler task created with schtasks.exe."
            $taskCreated = $true
        } else {
            Write-Warn "schtasks.exe returned exit code $LASTEXITCODE"
        }
    } catch {
        Write-Warn "Could not create scheduled task with schtasks.exe: $_"
    }
}

if (-not $taskCreated) {
    Write-Warn "Task Scheduler deployment failed. Run PowerShell as Administrator or create the task manually."
}

# NSSM setup
$nssmExe = Get-Command nssm.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue
if (-not $nssmExe) {
    if ($IsAdmin) {
        Write-Info "Installing NSSM..."
        $zipPath = Join-Path $env:TEMP 'nssm-2.24.zip'
        $extractPath = Join-Path $env:TEMP 'nssm-2.24'
        Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
        $nssmExe = Join-Path $extractPath 'win64\nssm.exe'
        Copy-Item -Path $nssmExe -Destination 'C:\Windows\System32\nssm.exe' -Force
        $nssmExe = 'C:\Windows\System32\nssm.exe'
    } else {
        Write-Warn "NSSM is not installed and admin privileges are required to install it. Skipping NSSM setup."
    }
}

# Only error if admin tried to install NSSM but failed
if ($IsAdmin -and -not (Test-Path $nssmExe)) { Write-ErrorAndExit "NSSM installation failed." }

$serviceName = 'KBReferralBot'
$botPath = Join-Path $ScriptDir 'bot.py'
if ($IsAdmin -and $nssmExe -and (Test-Path $nssmExe)) {
    Write-Info "Configuring NSSM service '$serviceName'..."
    & $nssmExe install $serviceName $pythonExe $botPath
    & $nssmExe set $serviceName AppDirectory $ScriptDir
    & $nssmExe set $serviceName AppStdout (Join-Path $logsDir 'out.log')
    & $nssmExe set $serviceName AppStderr (Join-Path $logsDir 'err.log')
    & $nssmExe set $serviceName AppRotateFiles 1

    try {
        & $nssmExe start $serviceName
        Write-Info "NSSM service '$serviceName' started."
    } catch {
        Write-Warn "Could not start NSSM service: $_"
    }
} else {
    Write-Warn "Skipping NSSM service setup because NSSM is unavailable or admin privileges are missing."
}

Write-Info "Deployment complete."
if ($taskCreated) {
    Write-Info "Verify Task Scheduler task: Get-ScheduledTask -TaskName $taskName | Format-List"
} else {
    Write-Warn "Task Scheduler task was not created. Create it manually or rerun this script as Administrator."
    Write-Warn "If you are not an administrator, open PowerShell as admin and run the script again."
}
if ($IsAdmin -and $nssmExe -and (Test-Path $nssmExe)) {
    & $nssmExe status $serviceName
} else {
    Write-Warn "NSSM status skipped. Install NSSM and run as admin to configure the service."
}
Write-Info "Tail logs with: Get-Content .\logs\out.log -Tail 50 -Wait"