# Detailed 24/7 Deployment Setup

This guide sets up two Windows deployment methods to keep the bot running continuously:

1. Task Scheduler
2. NSSM Windows service

## Prerequisites

- Python virtual environment created in the project root
- Dependencies installed from `requirements.txt`
- `.env` file configured in project root
- Git not required for runtime deployment

## Task Scheduler setup

1. Open PowerShell as Administrator.
2. Run:
   ```powershell
   cd C:\Users\hp\Desktop\KBReferralBot
   .\setup_task_scheduler.ps1
   ```
3. Verify the task exists:
   ```powershell
   Get-ScheduledTask -TaskName KBReferralBot
   ```
4. Optionally run immediately:
   ```powershell
   Start-ScheduledTask -TaskName KBReferralBot
   ```

This task will run at logon and launch the bot in a hidden PowerShell window.

## NSSM service setup

1. Run the NSSM installer script as Administrator:
   ```powershell
   cd C:\Users\hp\Desktop\KBReferralBot
   .\install_nssm.ps1
   ```
2. Create the service:
   ```powershell
   .\setup_nssm_service.ps1
   ```
3. Start the service:
   ```powershell
   nssm start KBReferralBot
   ```
4. Check service status:
   ```powershell
   nssm status KBReferralBot
   ```
5. View logs:
   ```powershell
   Get-Content .\logs\out.log -Tail 50 -Wait
   Get-Content .\logs\err.log -Tail 50 -Wait
   ```

## Notes

- The service and scheduler both use the same `bot.py` entrypoint.
- `referrals.db` persists in the project root by default.
- For Docker, virtualization is currently blocked, so this local deployment is the best option.
