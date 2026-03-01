"""
handlers/delete_word.py — ❌ Delete Word

Flow:
  1. Show paginated list of user's words (inline buttons)
  2. User taps a word → confirmation dialog [Yes] [No]
  3. Confirm → DELETE FROM words WHERE id = ? AND user_id = ?
  4. Show success / cancellation message
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.db import get_user_words, get_word_by_id, delete_word
from keyboards.keyboards import (
    main_menu_kb, cancel_kb, word_list_kb, confirm_delete_kb, BTN_CANCEL
)
from states.states import DeleteWordStates

router = Router()
PAGE_SIZE = 8


async def start_delete(message: Message, state: FSMContext) -> None:
    """Entry — show the user's word list."""
    await state.clear()
    user_id = message.from_user.id
    words   = await get_user_words(user_id)

    if not words:
        await message.answer(
            "📭 <b>You have no words to delete.</b>\n\n"
            "Add words first with <b>➕ Add Word</b>.",
            parse_mode="HTML",
            reply_markup=main_menu_kb(),
        )
        return

    await state.set_state(DeleteWordStates.choosing_word)
    await state.update_data(words=words, page=0)

    await message.answer(
        f"❌ <b>Delete a Word</b>\n\n"
        f"You have <b>{len(words)}</b> word(s).\n"
        "Tap a word to select it for deletion:",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )
    await message.answer(
        "👇 Select word:",
        reply_markup=word_list_kb(words, callback_prefix="del_pick", page=0),
    )


# ─── Pagination within delete flow ───────────────────────────────────────────

@router.callback_query(DeleteWordStates.choosing_word, F.data.startswith("word_page:"))
async def delete_page(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[1]
    if val == "noop":
        await callback.answer()
        return

    page  = int(val)
    data  = await state.get_data()
    words = data.get("words", [])
    await callback.answer()
    await state.update_data(page=page)

    await callback.message.edit_reply_markup(
        reply_markup=word_list_kb(words, callback_prefix="del_pick", page=page)
    )


# ─── Word selected → confirm ──────────────────────────────────────────────────

@router.callback_query(DeleteWordStates.choosing_word, F.data.startswith("del_pick:"))
async def word_picked(callback: CallbackQuery, state: FSMContext) -> None:
    word_id = int(callback.data.split(":")[1])
    word    = await get_word_by_id(word_id, callback.from_user.id)
    await callback.answer()

    if not word:
        await callback.answer("⚠️ Word not found.", show_alert=True)
        return

    await state.set_state(DeleteWordStates.confirming)
    await state.update_data(delete_word_id=word_id)

    await callback.message.answer(
        f"⚠️ Are you sure you want to delete:\n\n"
        f"🇷🇺  <b>{word['russian_word']}</b>  →  🇬🇧  <b>{word['english_word']}</b>\n"
        f"📂  Topic: {word['topic']}",
        parse_mode="HTML",
        reply_markup=confirm_delete_kb(word_id),
    )


# ─── Confirmed → execute delete ──────────────────────────────────────────────

@router.callback_query(DeleteWordStates.confirming, F.data.startswith("confirm_delete:"))
async def confirmed_delete(callback: CallbackQuery, state: FSMContext) -> None:
    word_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    deleted = await delete_word(word_id, user_id)
    await state.clear()
    await callback.answer("🗑 Deleted!" if deleted else "⚠️ Already gone.")

    if deleted:
        await callback.message.edit_text(
            "✅ <b>Word deleted successfully.</b>",
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text("⚠️ Word was not found in your list.")

    await callback.message.answer("Back to the main menu:", reply_markup=main_menu_kb())


# ─── Cancelled ────────────────────────────────────────────────────────────────

@router.callback_query(DeleteWordStates.confirming, F.data == "cancel_delete")
async def cancel_delete_cb(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Cancelled.")
    await callback.message.edit_text("❌ Deletion cancelled.")
    await callback.message.answer("Back to the main menu:", reply_markup=main_menu_kb())


@router.message(DeleteWordStates.choosing_word, F.text == BTN_CANCEL)
async def cancel_delete_btn(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Cancelled.", reply_markup=main_menu_kb())
