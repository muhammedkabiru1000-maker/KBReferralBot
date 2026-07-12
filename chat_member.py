from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
import logging

from config import CHANNEL_USERNAME
import database

router = Router()
logger = logging.getLogger(__name__)


@router.chat_member()
async def on_chat_member(update: ChatMemberUpdated, bot: Bot):
    try:
        # Ensure this update is for the configured channel
        chat = update.chat
        if CHANNEL_USERNAME:
            cfg = CHANNEL_USERNAME.lstrip("@")
            if not getattr(chat, "username", None) == cfg:
                return

        new_status = getattr(update, "new_chat_member", None)
        if not new_status:
            return

        status = new_status.status
        if status in ("member", "administrator", "creator"):
            user = new_status.user
            user_id = user.id
            referrer = await database.mark_user_joined(user_id)
            if referrer:
                try:
                    await bot.send_message(referrer, f"🎉 Good news! Your referral <{user_id}> joined the channel and was counted.")
                except Exception:
                    logger.exception("Failed to notify referrer %s", referrer)
    except Exception:
        logger.exception("Error handling chat_member update")
