from aiogram import Bot


async def is_user_in_channel(bot: Bot, channel_username: str, user_id: int) -> bool:
    """Return True if the user is a member of the given channel/username.

    channel_username should be like '@KB_FOREXXX' or 'KB_FOREXXX'.
    """
    if not channel_username:
        return False

    try:
        # normalize
        chat = channel_username
        if channel_username.startswith("@"): 
            chat = channel_username

        member = await bot.get_chat_member(chat, user_id)
        status = member.status  # 'member', 'creator', 'administrator', 'left', 'kicked'
        return status in ("member", "creator", "administrator")
    except Exception:
        return False
