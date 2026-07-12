from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import database
from handlers.inline_buttons import build_navigation_keyboard

router = Router()


def format_user_name(uid: int, username: str | None, first_name: str | None) -> str:
    if username:
        return f"@{username}"
    if first_name:
        return first_name
    return str(uid)


@router.message(Command(commands=["myreferrals"]))
async def my_referrals(message: Message):
    user_id = message.from_user.id
    refs = await database.get_my_referred_users(user_id)
    if not refs:
        await message.answer("You haven't referred anyone yet. Share your referral link to invite users.")
        return

    confirmed = sum(1 for _, _, _, counted in refs if counted)
    pending = len(refs) - confirmed

    lines = [
        "<b>📨 Your referral dashboard</b>",
        "<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>",
        f"<pre>Total referred: {len(refs):>2}   Confirmed: {confirmed:>2}   Pending: {pending:>2}</pre>",
        "<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>",
        "<pre>#  Participant               Status      </pre>",
    ]

    for index, (uid, username, first_name, counted) in enumerate(refs, start=1):
        status = "✅ Confirmed" if counted else "⏳ Pending"
        name = format_user_name(uid, username, first_name)
        lines.append(f"<pre>{index:>2}. {name:<24} {status}</pre>")

    lines.append("<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>")
    lines.append("<i>Share your link and climb the leaderboard.</i>")

    keyboard = build_navigation_keyboard([
        [("Leaderboard", "leaderboard")],
        [("Help", "help")],
    ])
    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=keyboard)


@router.message(Command(commands=["leaderboard"]))
async def leaderboard(message: Message):
    rows = await database.get_leaderboard(10)
    if not rows:
        await message.answer("No referrals yet. Start inviting users with your referral link.")
        return

    medals = ["🥇", "🥈", "🥉"]
    top_rows = rows[:3]
    table_rows = rows[:10]

    lines = [
        "<b>🏆 Referral Contest Leaderboard</b>",
        "<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>",
    ]

    if top_rows:
        lines.append("<b>Top performers</b>")
        for pos, (uid, username, first_name, referrals) in enumerate(top_rows, start=1):
            name = format_user_name(uid, username, first_name)
            medal = medals[pos - 1]
            lines.append(f"<pre>{medal} {pos}. {name:<22} {referrals:>4} invites</pre>")
        lines.append("<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>")

    lines.append("<pre>#  Participant               Invites</pre>")
    lines.append("<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>")

    for pos, (uid, username, first_name, referrals) in enumerate(table_rows, start=1):
        name = format_user_name(uid, username, first_name)
        rank = medals[pos - 1] if pos <= 3 else f"{pos:>2}."
        lines.append(f"<pre>{rank:<3} {name:<24} {referrals:>5}</pre>")

    if len(rows) < 10:
        for pos in range(len(rows) + 1, 11):
            lines.append(f"<pre>{pos:>2}. {'-':<24} {'0':>5}</pre>")

    lines.append("<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>")
    lines.append("<i>Tap Help for contest commands, or refresh with Start.</i>")

    keyboard = build_navigation_keyboard([
        [("Start", "start")],
        [("My referrals", "myreferrals"), ("Help", "help")],
    ])
    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=keyboard)
