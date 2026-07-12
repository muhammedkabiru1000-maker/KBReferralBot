$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $ScriptDir 'venv\Scripts\python.exe'
$bot = Join-Path $ScriptDir 'bot.py'

if (-not (Test-Path $python)) {
    Write-Error "Python virtual environment not found at $python. Run `python -m venv venv` first."
    exit 1
}

Set-Location $ScriptDir
Write-Host "Starting bot from $bot..."
& $python $bot
