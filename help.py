from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from handlers.inline_buttons import build_navigation_keyboard

router = Router()


@router.message(Command(commands=["help"]))
async def help_cmd(message: Message):
    keyboard = build_navigation_keyboard([
        ("Start", "start"),
        ("My referrals", "myreferrals"),
        ("Leaderboard", "leaderboard"),
    ])

    await message.answer(
        "<b>🤖 KB Referral Contest Help</b>\n\n"
        "Use these commands to manage your referral activity:\n"
        "<b>/start</b> - join the contest and get your referral link\n"
        "<b>/myreferrals</b> - show users you referred\n"
        "<b>/leaderboard</b> - top 10 referrers\n"
        "<b>/help</b> - show this menu\n\n"
        "Admin only:\n"
        "<b>/stats</b>, <b>/resetcontest</b>, <b>/exportcsv</b>",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
