from aiogram import Router, Bot
import logging
import asyncio
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import CHANNEL_USERNAME
import database
import utils
from handlers.admin import is_admin
from handlers.inline_buttons import build_navigation_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    # Parse start payload (deep link) from message text, compatible across aiogram versions
    text = message.text or message.caption or ""
    parts = text.split(maxsplit=1)
    args = parts[1].strip() if len(parts) > 1 else ""
    referrer = None
    if args and args.isdigit():
        referrer = int(args)

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    logger.info("/start received from %s args=%s", user_id, args)
    # Prevent self-referral
    if referrer == user_id:
        referrer = None

    # Immediate reply: quick welcome card and command suggestions
    me = await bot.get_me()
    bot_username = me.username or "<bot>"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    keyboard_rows = [
        [("My referrals", "myreferrals"), ("Leaderboard", "leaderboard")],
        [("Help", "help")],
    ]
    if is_admin(user_id):
        keyboard_rows.append([("Admin panel", "admin_panel")])

    logger.info("/start inline buttons rows: %s", keyboard_rows)
    keyboard = build_navigation_keyboard(keyboard_rows)

    await message.answer(
        "<b>🎉 Welcome to the Referral Contest!</b>\n\n"
        "Use your unique link below to invite friends and earn rewards.\n\n"
        f"<b>Your link:</b>\n<code>{referral_link}</code>\n\n"
        "<i>Inline button mode is active.</i> Tap a button below to check your standings.",
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    # Schedule background processing to avoid blocking the handler
    async def background_register():
        try:
            exists = await database.user_exists(user_id)
            joined = await utils.is_user_in_channel(bot, CHANNEL_USERNAME, user_id)
            if not exists:
                added = await database.add_user(user_id, username, first_name, referred_by=referrer, joined_channel=joined)
                if added:
                    logger.info("Added user %s referred_by=%s joined=%s", user_id, referrer, joined)
                    if referrer and joined:
                        await bot.send_message(user_id, "✅ Your referral was recorded because you are a member of the channel. Welcome!\nYou can now invite more users with your link.")
                    elif referrer and not joined:
                        await bot.send_message(user_id, f"👋 You were referred by {referrer}. Please join {CHANNEL_USERNAME} to validate the referral.\nOnce you join, your referrer will receive [...]")
                    else:
                        await bot.send_message(user_id, "🎉 You joined the contest. Share your referral link to earn points.")
            else:
                await bot.send_message(user_id, "👋 Welcome back! Use /myreferrals or /leaderboard to check your progress.")

            # Optionally notify the user about current confirmed referrals
            referrals = await database.get_referrals_count(user_id)
            await bot.send_message(user_id, f"You have <b>{referrals}</b> confirmed referrals. Use /leaderboard to see the top 10.", parse_mode="HTML")
        except Exception:
            logger.exception("Error registering user in background")

    asyncio.create_task(background_register())
