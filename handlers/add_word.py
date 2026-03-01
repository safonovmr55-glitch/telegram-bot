"""
handlers/add_word.py — ➕ Add Word — 3-step FSM flow.
Steps: Russian → English → Topic
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.db import add_word
from keyboards.keyboards import (
    main_menu_kb, cancel_kb, topic_inline_kb, BTN_CANCEL
)
from states.states import AddWordStates

router = Router()


async def start_add(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddWordStates.waiting_for_russian)
    await message.answer(
        "➕ <b>Add a New Word</b>\n\n"
        "<b>Step 1/3</b> — Send the <b>Russian word</b>:",
        parse_mode="HTML",
        reply_markup=cancel_kb(),
    )

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    await start_add(message, state)

# ─── Step 1 ───────────────────────────────────────────────────────────────────

@router.message(AddWordStates.waiting_for_russian)
async def got_russian(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if text == BTN_CANCEL or text.startswith("/"):
        await _cancel(message, state); return
    if not text:
        await message.answer("⚠️ Please enter a valid Russian word."); return

    await state.update_data(russian=text)
    await state.set_state(AddWordStates.waiting_for_english)
    await message.answer(
        f"✅ Russian: <b>{text}</b>\n\n"
        "<b>Step 2/3</b> — Now send the <b>English translation</b>:",
        parse_mode="HTML",
    )

# ─── Step 2 ───────────────────────────────────────────────────────────────────

@router.message(AddWordStates.waiting_for_english)
async def got_english(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if text == BTN_CANCEL or text.startswith("/"):
        await _cancel(message, state); return
    if not text:
        await message.answer("⚠️ Please enter a valid English translation."); return

    await state.update_data(english=text)
    await state.set_state(AddWordStates.waiting_for_topic)
    await message.answer(
        f"✅ English: <b>{text}</b>\n\n"
        "<b>Step 3/3</b> — Select a <b>topic</b>:",
        parse_mode="HTML",
    )
    await message.answer("👇 Choose topic:", reply_markup=topic_inline_kb("addword_topic"))

# ─── Step 3 ───────────────────────────────────────────────────────────────────

@router.callback_query(AddWordStates.waiting_for_topic, F.data.startswith("addword_topic:"))
async def got_topic(callback: CallbackQuery, state: FSMContext) -> None:
    topic = callback.data.split(":")[1]
    if topic == "Mixed":
        await callback.answer("Please choose a specific topic.", show_alert=True)
        return

    data    = await state.get_data()
    user_id = callback.from_user.id

    await add_word(user_id, data["russian"], data["english"], topic)
    await state.clear()
    await callback.answer("✅ Word saved!")

    await callback.message.edit_text(
        f"✅ <b>Word added!</b>\n\n"
        f"🇷🇺  <b>{data['russian']}</b>  →  🇬🇧  <b>{data['english']}</b>\n"
        f"📂  Topic: <b>{topic}</b>",
        parse_mode="HTML",
    )
    await callback.message.answer("What's next?", reply_markup=main_menu_kb())

# ─── Cancel ───────────────────────────────────────────────────────────────────

@router.message(F.text == BTN_CANCEL)
async def cancel_any(message: Message, state: FSMContext) -> None:
    await _cancel(message, state)

async def _cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Cancelled.", reply_markup=main_menu_kb())
