"""
handlers/start.py — /start command and main menu button dispatcher.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import get_level_name
from database.db import get_or_create_user
from keyboards.keyboards import (
    main_menu_kb,
    BTN_MY_WORDS, BTN_PLAY, BTN_ADD,
    BTN_DELETE, BTN_STATS, BTN_PROFILE,
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Greet the user and show the main menu."""
    await state.clear()
    user = await get_or_create_user(
        user_id    = message.from_user.id,
        username   = message.from_user.username or "",
        first_name = message.from_user.first_name or "",
    )
    name  = message.from_user.first_name or "there"
    level = get_level_name(user["xp"])

    await message.answer(
        f"👋 Hello, <b>{name}</b>!  [ {level} ]\n\n"
        "Welcome to the <b>Word Learning Bot</b> 🇬🇧\n\n"
        "Learn vocabulary through games, track your progress,\n"
        "and build your own word collection.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Pick an option from the menu below:",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ─── Menu button dispatchers ──────────────────────────────────────────────────

@router.message(F.text == BTN_MY_WORDS)
async def btn_my_words(message: Message, state: FSMContext) -> None:
    from handlers.my_words import show_my_words
    await show_my_words(message, state)

@router.message(F.text == BTN_PLAY)
async def btn_play(message: Message, state: FSMContext) -> None:
    from handlers.game import start_game
    await start_game(message, state)

@router.message(F.text == BTN_ADD)
async def btn_add(message: Message, state: FSMContext) -> None:
    from handlers.add_word import start_add
    await start_add(message, state)

@router.message(F.text == BTN_DELETE)
async def btn_delete(message: Message, state: FSMContext) -> None:
    from handlers.delete_word import start_delete
    await start_delete(message, state)

@router.message(F.text == BTN_STATS)
async def btn_stats(message: Message, state: FSMContext) -> None:
    from handlers.stats import show_stats
    await show_stats(message, state)

@router.message(F.text == BTN_PROFILE)
async def btn_profile(message: Message, state: FSMContext) -> None:
    from handlers.profile import show_profile
    await show_profile(message, state)

@router.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext) -> None:
    from handlers.stats import show_stats
    await show_stats(message, state)

@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext) -> None:
    from handlers.profile import show_profile
    await show_profile(message, state)
