"""
handlers/profile.py — 👤 Profile — XP, rank, level progress bar.
"""
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import get_level_name, LEVEL_THRESHOLDS, LEVEL_NAMES
from database.db import get_user
from keyboards.keyboards import main_menu_kb

router = Router()


async def show_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user    = await get_user(user_id)

    if not user:
        await message.answer("⚠️ No profile found. Send /start.", reply_markup=main_menu_kb())
        return

    xp    = user["xp"]
    level = get_level_name(xp)
    name  = user.get("first_name") or "Learner"

    # Find next level
    next_xp   = None
    next_name = None
    prev_xp   = 0
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp < threshold:
            next_xp   = threshold
            next_name = LEVEL_NAMES[i]
            # find where current level starts
            prev_xp   = LEVEL_THRESHOLDS[i - 1] if i > 0 else 0
            break

    if next_xp:
        span   = next_xp - prev_xp
        filled = round((xp - prev_xp) / span * 10) if span else 0
        bar    = "🟨" * filled + "⬜" * (10 - filled)
        prog   = f"{bar}  {xp - prev_xp}/{span} XP → {next_name}"
    else:
        prog = "🏆 Maximum level reached!"

    total    = user["total_correct"] + user["total_wrong"]
    accuracy = round(user["total_correct"] / total * 100, 1) if total else 0.0

    await message.answer(
        f"👤 <b>{name}'s Profile</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎓 Level:        <b>{level}</b>\n"
        f"✨ Total XP:     <b>{xp}</b>\n"
        f"🎮 Games:        <b>{user['games_played']}</b>\n"
        f"🔥 Best streak:  <b>{user['best_streak']}</b>\n"
        f"🎯 Accuracy:     <b>{accuracy}%</b>\n\n"
        f"📈 <b>Progress to next level</b>\n"
        f"{prog}",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
