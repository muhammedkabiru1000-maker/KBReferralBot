from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

import database
import io
from handlers.admin import is_admin

router = Router()


def build_navigation_keyboard(button_rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    if button_rows and isinstance(button_rows[0], tuple):
        button_rows = [button_rows]

    inline_keyboard = [
        [InlineKeyboardButton(text=text, callback_data=f"nav_{action}") for text, action in row]
        for row in button_rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


@router.callback_query(lambda query: query.data and query.data.startswith("nav_"))
async def navigate_callback(query: CallbackQuery):
    action = query.data.removeprefix("nav_")
    user_id = query.from_user.id
    print(f"Inline callback received: {action} from {user_id}")

    if action == "start":
        bot = query.bot
        me = await bot.get_me()
        bot_username = me.username or "<bot>"
        referral_link = f"https://t.me/{bot_username}?start={user_id}"
        await query.message.answer(
            "<b>🎉 Referral Link</b>\n\n"
            "Use your personal link to invite friends and earn rewards.\n\n"
            f"<b>Your link:</b>\n<code>{referral_link}</code>\n\n"
            "Share it anywhere and start climbing the leaderboard!",
            parse_mode="HTML",
            reply_markup=build_navigation_keyboard([
                [("My referrals", "myreferrals"), ("Leaderboard", "leaderboard")],
                [("Help", "help")],
            ]),
        )
    elif action == "myreferrals":
        refs = await database.get_my_referred_users(user_id)
        if not refs:
            await query.message.answer(
                "You haven't referred anyone yet. Share your referral link to invite users.",
                reply_markup=build_navigation_keyboard([
                    [("Leaderboard", "leaderboard")],
                    [("Help", "help")],
                ]),
            )
        else:
            lines = [
                "<b>📨 Your referrals</b>",
                "<pre>#  Participant               Status      </pre>",
            ]
            for index, (uid, username, first_name, counted) in enumerate(refs, start=1):
                status = "✅ Confirmed" if counted else "⏳ Pending"
                name = username and f"@{username}" or first_name or str(uid)
                lines.append(f"<pre>{index:>2}. {name:<24} {status}</pre>")
            await query.message.answer(
                "\n".join(lines),
                parse_mode="HTML",
                reply_markup=build_navigation_keyboard([
                    [("Leaderboard", "leaderboard")],
                    [("Help", "help")],
                ]),
            )
    elif action == "leaderboard":
        rows = await database.get_leaderboard(10)
        if not rows:
            await query.message.answer(
                "No referrals yet. Start inviting users with your referral link.",
                reply_markup=build_navigation_keyboard([
                    [("My referrals", "myreferrals")],
                    [("Help", "help")],
                ]),
            )
        else:
            medals = ["🥇", "🥈", "🥉"]
            lines = [
                "<b>🏆 Top 10 Referral Leaderboard</b>",
                "<pre>#  Participant               Referrals</pre>",
            ]
            for pos, (uid, username, first_name, referrals) in enumerate(rows, start=1):
                name = username and f"@{username}" or first_name or str(uid)
                prefix = medals[pos - 1] if pos <= 3 else f"{pos:>2}."
                lines.append(f"<pre>{prefix:<3} {name:<24} {referrals:>3}</pre>")
            if len(rows) < 10:
                for pos in range(len(rows) + 1, 11):
                    lines.append(f"<pre>{pos:>2}. {'-':<24} {'0':>3}</pre>")
            await query.message.answer(
                "\n".join(lines),
                parse_mode="HTML",
                reply_markup=build_navigation_keyboard([
                    [("My referrals", "myreferrals")],
                    [("Help", "help")],
                ]),
            )
    elif action == "help":
        buttons = [
            [("Start", "start")],
            [("My referrals", "myreferrals"), ("Leaderboard", "leaderboard")],
        ]
        if is_admin(user_id):
            buttons.append([
                ("Stats", "admin_stats"),
                ("Export CSV", "admin_exportcsv"),
            ])
            buttons.append([("Reset contest", "admin_resetcontest")])
        await query.message.answer(
            "<b>🤖 KB Referral Contest Help</b>\n\n"
            "Tap the buttons below to quickly move between sections.\n"
            "Use /start if you want to refresh your referral link or join again.\n\n"
            "<b>/start</b> - join the contest and get your referral link\n"
            "<b>/myreferrals</b> - show users you referred\n"
            "<b>/leaderboard</b> - top 10 referrers\n"
            "<b>/help</b> - show this menu\n\n"
            "Admin only buttons appear below if you are authorized.",
            parse_mode="HTML",
            reply_markup=build_navigation_keyboard(buttons),
        )
    elif action == "admin_panel":
        if not is_admin(user_id):
            await query.answer("Unauthorized.", show_alert=True)
            return
        await query.message.answer(
            "<b>🛠️ Admin Control Panel</b>\n\n"
            "Use the buttons below to manage the contest.",
            parse_mode="HTML",
            reply_markup=build_navigation_keyboard([
                [("Stats", "admin_stats"), ("Export CSV", "admin_exportcsv")],
                [("Reset contest", "admin_resetcontest")],
                [("Help", "help")],
            ]),
        )
    await query.answer()


@router.callback_query(lambda query: query.data and query.data.startswith("admin_"))
async def admin_callback(query: CallbackQuery):
    action = query.data.removeprefix("admin_")
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Unauthorized.", show_alert=True)
        return

    if action == "stats":
        total_users, total_referrals = await database.get_stats()
        await query.message.answer(f"Total users: {total_users}\nTotal referrals: {total_referrals}")
    elif action == "resetcontest":
        await database.reset_contest()
        await query.message.answer("Contest reset: all user data removed.")
    elif action == "exportcsv":
        data = await database.export_csv()
        bio = io.BytesIO(data)
        bio.name = "referrals.csv"
        await query.message.answer_document(FSInputFile(bio, filename="referrals.csv"))
    await query.answer()
