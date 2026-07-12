from aiogram import Router
from config import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    try:
        admins = [int(x.strip()) for x in ADMIN_ID.split(",") if x.strip()]
    except Exception:
        admins = []
    return user_id in admins
