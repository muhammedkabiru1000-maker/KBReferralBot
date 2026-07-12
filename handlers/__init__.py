from handlers.start import router as start_router
from handlers.referrals import router as referrals_router
from handlers.admin import router as admin_router
from handlers.help import router as help_router
from handlers.chat_member import router as chat_member_router
from handlers.inline_buttons import router as inline_buttons_router

__all__ = [
    "start_router",
    "referrals_router",
    "admin_router",
    "help_router",
    "chat_member_router",
    "inline_buttons_router",
]
