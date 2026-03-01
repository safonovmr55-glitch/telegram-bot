"""
keyboards/keyboards.py — All keyboard layouts in one place.
"""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ALL_TOPICS, TOPIC_EMOJI


# ─── Button label constants ───────────────────────────────────────────────────
BTN_MY_WORDS  = "📚 My Words"
BTN_PLAY      = "🎮 Play Game"
BTN_ADD       = "➕ Add Word"
BTN_DELETE    = "❌ Delete Word"
BTN_STATS     = "📊 Statistics"
BTN_PROFILE   = "👤 Profile"
BTN_CANCEL    = "🚫 Cancel"


# ─── Main menu ────────────────────────────────────────────────────────────────

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MY_WORDS),  KeyboardButton(text=BTN_PLAY)],
            [KeyboardButton(text=BTN_ADD),        KeyboardButton(text=BTN_DELETE)],
            [KeyboardButton(text=BTN_STATS),      KeyboardButton(text=BTN_PROFILE)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose an option…",
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ─── Topic selection (inline) ─────────────────────────────────────────────────

def topic_inline_kb(callback_prefix: str = "topic") -> InlineKeyboardMarkup:
    """Inline buttons for all topics + Mixed."""
    builder = InlineKeyboardBuilder()
    for t in ALL_TOPICS:
        emoji = TOPIC_EMOJI.get(t, "")
        builder.button(text=f"{emoji} {t}", callback_data=f"{callback_prefix}:{t}")
    builder.button(text="🎲 Mixed Random", callback_data=f"{callback_prefix}:Mixed")
    builder.adjust(2)
    return builder.as_markup()


def game_topic_kb() -> InlineKeyboardMarkup:
    """Same as topic_inline_kb but scoped to non-custom game topics."""
    builder = InlineKeyboardBuilder()
    for t in ["Animals", "Drinks", "Transport"]:
        emoji = TOPIC_EMOJI.get(t, "")
        builder.button(text=f"{emoji} {t}", callback_data=f"game_topic:{t}")
    builder.button(text="🎲 Mixed Random", callback_data="game_topic:Mixed")
    builder.adjust(2)
    return builder.as_markup()


# ─── Word list (inline) ───────────────────────────────────────────────────────

def word_list_kb(
    words: list[dict],
    callback_prefix: str = "select_word",
    page: int = 0,
    page_size: int = 8,
) -> InlineKeyboardMarkup:
    """
    Paginated inline keyboard of word buttons.
    Each button label: "russian — english"
    """
    builder = InlineKeyboardBuilder()
    total_pages = max(1, (len(words) + page_size - 1) // page_size)
    start       = page * page_size
    chunk       = words[start : start + page_size]

    for w in chunk:
        label = f"{w['russian_word']} — {w['english_word']}"
        builder.button(text=label, callback_data=f"{callback_prefix}:{w['id']}")
    builder.adjust(1)

    # Pagination row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="◀️ Prev",
            callback_data=f"word_page:{page-1}",
        ))
    nav.append(InlineKeyboardButton(
        text=f"{page+1}/{total_pages}",
        callback_data="word_page:noop",
    ))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(
            text="Next ▶️",
            callback_data=f"word_page:{page+1}",
        ))

    if len(nav) > 1 or total_pages > 1:
        builder.row(*nav)

    return builder.as_markup()


# ─── Confirmation (inline) ────────────────────────────────────────────────────

def confirm_delete_kb(word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Yes, delete", callback_data=f"confirm_delete:{word_id}"),
        InlineKeyboardButton(text="❌ No",          callback_data="cancel_delete"),
    ]])


# ─── Stop game (inline) ───────────────────────────────────────────────────────

def stop_game_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🛑 Stop Game", callback_data="game:stop"),
    ]])
