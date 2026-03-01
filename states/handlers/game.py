"""
handlers/game.py — 🎮 Play Game — full quiz loop with scoring and SRS.

Flow:
  1. Topic selection (inline)
  2. Words loaded (DB + built-in fallback), shuffled
  3. Card shown (Russian word) → user types English
  4. Answer checked → feedback → next card
  5. Session ends → save stats, show summary
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import get_level_name
from database.db import (
    get_user, save_session, update_user_after_game,
    update_word_stats,
)
from keyboards.keyboards import main_menu_kb, game_topic_kb, stop_game_kb, cancel_kb
from services.game_engine import (
    check_answer, compute_turn_score, compute_xp,
    build_result_message, load_words_for_game,
)
from states.states import GameStates

router = Router()


# ─── Entry ────────────────────────────────────────────────────────────────────

async def start_game(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(GameStates.choosing_topic)
    await message.answer(
        "🎮 <b>Play Game</b>\n\nChoose a topic:",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )
    await message.answer("👇 Select topic:", reply_markup=game_topic_kb())


# ─── Topic chosen ─────────────────────────────────────────────────────────────

@router.callback_query(GameStates.choosing_topic, F.data.startswith("game_topic:"))
async def topic_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    topic   = callback.data.split(":")[1]
    user_id = callback.from_user.id
    await callback.answer()

    words = await load_words_for_game(user_id, topic)

    if not words:
        await callback.message.edit_text(
            "⚠️ No words available for this topic.\n"
            "Add some with <b>➕ Add Word</b>!",
            parse_mode="HTML",
        )
        await callback.message.answer("Main menu:", reply_markup=main_menu_kb())
        await state.clear()
        return

    await state.update_data(
        topic=topic,
        queue=words,
        done=0,
        total=len(words),
        correct=0,
        wrong=0,
        score=0,
        streak=0,
    )
    await state.set_state(GameStates.playing)

    await callback.message.edit_text(
        f"🚀 <b>{topic}</b> — {len(words)} words\n\n"
        "Type the <b>English</b> translation for each Russian word.\n"
        "Answers are case-insensitive.",
        parse_mode="HTML",
    )
    await _send_card(callback.message, state)


# ─── Answer handler ───────────────────────────────────────────────────────────

@router.message(GameStates.playing)
async def handle_answer(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    # Allow main-menu buttons to abort game naturally
    if text in ("🚫 Cancel", "📚 My Words", "➕ Add Word",
                "❌ Delete Word", "📊 Statistics", "👤 Profile"):
        await _end_game(message, state, aborted=True)
        return

    data     = await state.get_data()
    queue    = data.get("queue", [])
    if not queue:
        return

    current  = queue[0]
    correct  = check_answer(text, current["english_word"])
    streak   = data["streak"]
    pts      = compute_turn_score(streak) if correct else 0
    user_id  = message.from_user.id

    # Update per-word stats (only for words that came from DB, not built-in)
    if current.get("id"):
        await update_word_stats(current["id"], correct)

    # Build feedback message
    new_streak = streak + 1 if correct else 0
    if correct:
        streak_msg = f"  🔥 Streak ×{new_streak}" if new_streak >= 3 else ""
        feedback   = f"✅ <b>Correct!</b>  +{pts} pts{streak_msg}"
        new_correct = data["correct"] + 1
    else:
        feedback   = (
            f"❌ <b>Wrong!</b>\n"
            f"Correct answer: <b>{current['english_word']}</b>"
        )
        new_correct = data["correct"]

    await message.answer(feedback, parse_mode="HTML")

    # Advance
    new_queue = queue[1:]
    await state.update_data(
        queue=new_queue,
        done=data["done"] + 1,
        correct=new_correct,
        wrong=data["wrong"] + (0 if correct else 1),
        score=data["score"] + pts,
        streak=new_streak,
    )

    if not new_queue:
        await _end_game(message, state)
    else:
        await _send_card(message, state)


# ─── Stop button ──────────────────────────────────────────────────────────────

@router.callback_query(GameStates.playing, F.data == "game:stop")
async def stop_btn(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("Game stopped.")
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await _end_game(callback.message, state, aborted=True)


# ─── Cancel button ────────────────────────────────────────────────────────────

@router.message(GameStates.choosing_topic, F.text == "🚫 Cancel")
@router.message(GameStates.playing,        F.text == "🚫 Cancel")
async def cancel_game(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Game cancelled.", reply_markup=main_menu_kb())


# ─── Internal helpers ─────────────────────────────────────────────────────────

async def _send_card(message, state: FSMContext) -> None:
    data  = await state.get_data()
    queue = data.get("queue", [])
    done  = data.get("done", 0)
    total = data.get("total", 0)
    score = data.get("score", 0)

    if not queue:
        return

    word     = queue[0]
    progress = f"{done + 1}/{total}"

    await message.answer(
        f"🃏 <b>Card {progress}</b>  |  🏆 {score} pts\n\n"
        f"🇷🇺  <b>{word['russian_word']}</b>\n\n"
        "Type the English translation 👇",
        parse_mode="HTML",
        reply_markup=stop_game_kb(),
    )


async def _end_game(message, state: FSMContext, aborted: bool = False) -> None:
    data    = await state.get_data()
    correct = data.get("correct", 0)
    wrong   = data.get("wrong",   0)
    score   = data.get("score",   0)
    topic   = data.get("topic",   "—")
    done    = data.get("done",    0)
    streak  = data.get("streak",  0)
    user_id = message.chat.id

    await state.clear()

    if aborted and done == 0:
        await message.answer("👋 Game cancelled. No questions answered.", reply_markup=main_menu_kb())
        return

    xp = compute_xp(correct)

    # Persist to DB
    await save_session(user_id, topic, score, correct, wrong)
    await update_user_after_game(user_id, correct, wrong, xp, streak)

    summary = build_result_message(topic, score, correct, wrong, xp)
    await message.answer(summary, parse_mode="HTML", reply_markup=main_menu_kb())
