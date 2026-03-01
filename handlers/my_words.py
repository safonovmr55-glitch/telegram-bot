"""
handlers/my_words.py — 📚 My Words — view and browse personal vocabulary.
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from ai.vocabulary import get_all_builtin_flat
from database.db import get_user_words, count_user_words
from keyboards.keyboards import main_menu_kb, topic_inline_kb, word_list_kb

router = Router()
PAGE_SIZE = 8


async def show_my_words(message: Message, state: FSMContext) -> None:
    """Entry — ask user which topic they want to browse."""
    await state.clear()
    count = await count_user_words(message.from_user.id)

    if count == 0:
        # Show built-in preview
        builtin = get_all_builtin_flat()
        lines   = ["📚 <b>Built-in Word Library</b> (your list is empty)\n"]
        for w in builtin[:15]:
            lines.append(f"  🇷🇺 <b>{w['russian_word']}</b>  →  🇬🇧 {w['english_word']}  [{w['topic']}]")
        if len(builtin) > 15:
            lines.append(f"\n  … and {len(builtin)-15} more words")
        lines.append("\nAdd your own words with <b>➕ Add Word</b>!")
        await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=main_menu_kb())
        return

    await message.answer(
        f"📚 <b>My Words</b>  ({count} total)\n\nFilter by topic:",
        parse_mode="HTML",
        reply_markup=topic_inline_kb("browse_topic"),
    )


# ─── Topic filter chosen ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("browse_topic:"))
async def browse_topic(callback: CallbackQuery, state: FSMContext) -> None:
    topic   = callback.data.split(":")[1]
    user_id = callback.from_user.id
    await callback.answer()

    words = await get_user_words(user_id, None if topic == "Mixed" else topic)

    if not words:
        await callback.message.edit_text(
            f"📭 No words found for <b>{topic}</b>.\nAdd some with <b>➕ Add Word</b>!",
            parse_mode="HTML",
        )
        return

    await state.update_data(browse_words=words, browse_page=0)
    await callback.message.edit_text(
        f"📚 <b>{topic}</b> — {len(words)} word(s)",
        parse_mode="HTML",
        reply_markup=word_list_kb(words, callback_prefix="view_word", page=0),
    )


# ─── Pagination ───────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("word_page:"))
async def word_page(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[1]
    if val == "noop":
        await callback.answer()
        return

    page  = int(val)
    data  = await state.get_data()
    words = data.get("browse_words", [])
    await callback.answer()

    await callback.message.edit_reply_markup(
        reply_markup=word_list_kb(words, callback_prefix="view_word", page=page)
    )
    await state.update_data(browse_page=page)


# ─── Word detail view ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("view_word:"))
async def view_word(callback: CallbackQuery) -> None:
    word_id = int(callback.data.split(":")[1])
    from database.db import get_word_by_id
    word = await get_word_by_id(word_id, callback.from_user.id)
    await callback.answer()

    if not word:
        await callback.answer("⚠️ Word not found.", show_alert=True)
        return

    total = word["correct_count"] + word["wrong_count"]
    acc   = round(word["correct_count"] / total * 100) if total else 0

    await callback.message.answer(
        f"📖 <b>Word Detail</b>\n\n"
        f"🇷🇺  <b>{word['russian_word']}</b>\n"
        f"🇬🇧  <b>{word['english_word']}</b>\n"
        f"📂  Topic: {word['topic']}\n\n"
        f"✅ Correct: {word['correct_count']}   ❌ Wrong: {word['wrong_count']}\n"
        f"🎯 Accuracy: {acc}%   🔥 Streak: {word['streak']}",
        parse_mode="HTML",
    )
