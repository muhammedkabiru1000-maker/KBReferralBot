from .start import router as start_router
from .referrals import router as referrals_router
from .admin import router as admin_router
from .help import router as help_router
from .chat_member import router as chat_member_router
from .inline_buttons import router as inline_buttons_router

__all__ = ["start_router", "referrals_router", "admin_router", "help_router", "chat_member_router", "inline_buttons_router"]
