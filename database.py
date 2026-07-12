import aiosqlite
import csv
import io
from typing import List, Optional, Tuple

DB_PATH = "referrals.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                referred_by INTEGER,
                referrals INTEGER DEFAULT 0,
                counted INTEGER DEFAULT 0,
                joined_channel INTEGER DEFAULT 0
            )
            """
        )
        await db.commit()


async def user_exists(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return bool(row)


async def add_user(user_id: int, username: Optional[str], first_name: Optional[str], referred_by: Optional[int] = None, joined_channel: bool = False) -> bool:
    if await user_exists(user_id):
        return False

    counted = 1 if (referred_by and joined_channel) else 0

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (user_id, username, first_name, referred_by, counted, joined_channel) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, first_name, referred_by, counted, 1 if joined_channel else 0),
        )

        if referred_by and counted:
            await db.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (referred_by,))

        await db.commit()
    return True


async def mark_user_joined(user_id: int) -> Optional[int]:
    """Mark the user as joined; if they were referred and not yet counted,
    increment the referrer's referrals and return the referrer's user_id.
    Otherwise return None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT referred_by, counted FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if not row:
            return None
        referred_by, counted = row
        if referred_by and not counted:
            await db.execute("UPDATE users SET counted=1, joined_channel=1 WHERE user_id=?", (user_id,))
            await db.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (referred_by,))
            await db.commit()
            return referred_by
        else:
            # mark joined_channel even if already counted
            await db.execute("UPDATE users SET joined_channel=1 WHERE user_id=?", (user_id,))
            await db.commit()
            return None


async def get_referrals_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0


async def get_my_referred_users(user_id: int) -> List[Tuple[int, str, str, int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id, username, first_name, counted FROM users WHERE referred_by=?", (user_id,))
        rows = await cur.fetchall()
        return rows


async def get_leaderboard(limit: int = 10) -> List[Tuple[int, Optional[str], Optional[str], int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id, username, first_name, referrals FROM users ORDER BY referrals DESC LIMIT ?", (limit,))
        rows = await cur.fetchall()
        return rows


async def get_stats() -> Tuple[int, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        total_users = (await cur.fetchone())[0]
        cur = await db.execute("SELECT SUM(referrals) FROM users")
        row = await cur.fetchone()
        total_referrals = row[0] if row and row[0] is not None else 0
        return total_users, total_referrals


async def reset_contest() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users")
        await db.commit()


async def export_csv() -> bytes:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id, username, first_name, referred_by, referrals, counted, joined_channel FROM users")
        rows = await cur.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "username", "first_name", "referred_by", "referrals", "counted", "joined_channel"])
    for r in rows:
        writer.writerow(r)

    return output.getvalue().encode("utf-8")