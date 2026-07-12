# Deployment Guide

## Local Python 24/7 Deployment (Windows)

This bot can run without Docker by using Python and a Windows service or Task Scheduler.

### 1. Create Python virtualenv

```powershell
cd C:\Users\hp\Desktop\KBReferralBot
python -m venv venv
```

### 2. Install dependencies

```powershell
.\\venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Create `.env`

Create a `.env` file in the project root with:

```text
BOT_TOKEN=123:ABC
CHANNEL_USERNAME=@YourChannel
ADMIN_ID=123456789
```

### 4. Run the bot manually

```powershell
.\\venv\\Scripts\\Activate.ps1
python bot.py
```

### 5. Run the bot automatically with Task Scheduler

Open Task Scheduler and create a task:

- Trigger: At log on or At startup
- Action: Start a program
- Program/script: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
- Add arguments:
  ```powershell
  -NoProfile -WindowStyle Hidden -Command "Set-Location 'C:\Users\hp\Desktop\KBReferralBot'; .\venv\Scripts\Activate.ps1; python bot.py"
  ```
- Start in: `C:\Users\hp\Desktop\KBReferralBot`
- Run whether user is logged on or not (optional)

### 6. Run the bot as a Windows service with NSSM

1. Download and install NSSM using `install_nssm.ps1`.
2. Create the service:

```powershell
nssm install KBReferralBot
```

3. In the NSSM GUI, set:

- Path: `C:\Users\hp\Desktop\KBReferralBot\venv\Scripts\python.exe`
- Arguments: `C:\Users\hp\Desktop\KBReferralBot\bot.py`
- Startup directory: `C:\Users\hp\Desktop\KBReferralBot`

4. Start the service:

```powershell
nssm start KBReferralBot
```

### 7. Verify the bot

- Check logs if the app prints or use the Telegram bot itself.
- If the bot is not responding, confirm `.env` values and that the bot is an admin in the channel.

## Notes

- Docker is optional; local deployment works without virtualization.
- Keep `referrals.db` in the project root to preserve your data.
