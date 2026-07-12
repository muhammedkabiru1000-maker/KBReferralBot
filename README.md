KB Referral Contest Bot
=======================

This is a Telegram referral contest bot built with Python and aiogram 3. It stores users and referral data in SQLite and supports unique referral links using `/start <user_id>`.

Features
- SQLite database using aiosqlite
- Unique referral links: `https://t.me/<bot_username>?start=<user_id>`
- Prevents self-referrals and double-counting
- Checks whether referred users joined a channel (configured in `.env`) before counting
- Commands: `/start`, `/myreferrals`, `/leaderboard`, `/help`
- Admin commands: `/stats`, `/resetcontest`, `/exportcsv`

Setup
1. Create and activate a Python virtualenv (Python 3.11+ recommended):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create a `.env` file with these variables:

```
BOT_TOKEN=123:ABC
CHANNEL_USERNAME=@KB_FOREXXX
ADMIN_ID=123456789
```

4. Run the bot:

```powershell
python bot.py
```

## Docker deployment

1. Install Docker Desktop.
2. Copy your `.env` next to `docker-compose.yml`.
3. Build and start the bot:

```powershell
docker compose up -d --build
```

4. Check logs:

```powershell
docker compose logs -f
```

5. Stop the bot:

```powershell
docker compose down
```

Notes
- The bot checks channel membership via `get_chat_member`. For this to work the bot must be able to see membership of the channel (public channel or the bot added to the channel).
- Docker volume `./referrals.db:/app/referrals.db` keeps your database persistent.
