"""
handlers/stats.py — 📊 Statistics
"""
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.db import get_user, count_user_words, count_learned_words, get_user_accuracy
from keyboards.keyboards import main_menu_kb

router = Router()


async def show_stats(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user    = await get_user(user_id)

    if not user:
        await message.answer("⚠️ No data yet. Use /start first.", reply_markup=main_menu_kb())
        return

    total_words   = await count_user_words(user_id)
    learned_words = await count_learned_words(user_id)
    accuracy      = await get_user_accuracy(user_id)

    filled  = round(accuracy / 10)
    bar     = "🟩" * filled + "⬜" * (10 - filled)

    await message.answer(
        "📊 <b>Your Statistics</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 Total words:    <b>{total_words}</b>\n"
        f"✅ Learned (3+✅): <b>{learned_words}</b>\n"
        f"🔄 In progress:    <b>{total_words - learned_words}</b>\n\n"
        f"🎮 Games played:   <b>{user['games_played']}</b>\n"
        f"👍 Correct:        <b>{user['total_correct']}</b>\n"
        f"👎 Wrong:          <b>{user['total_wrong']}</b>\n\n"
        f"🎯 Accuracy:       <b>{accuracy}%</b>\n"
        f"{bar}\n\n"
        f"🔥 Best streak:    <b>{user['best_streak']}</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
