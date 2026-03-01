"""
main.py — Entry point for the Word Learning Bot.

Project structure
─────────────────
  config.py              — settings, scoring, level system
  ai/vocabulary.py       — built-in word dataset (30 words × 3 topics)
  database/db.py         — async SQLite (users, words, sessions)
  states/states.py       — FSM state groups
  keyboards/keyboards.py — all keyboard layouts
  services/game_engine.py — scoring, word loading, result builder
  handlers/
    start.py      — /start + main-menu routing
    my_words.py   — 📚 My Words (browse + pagination)
    add_word.py   — ➕ Add Word (3-step FSM)
    delete_word.py— ❌ Delete Word (list + confirm dialog)
    game.py       — 🎮 Play Game (full quiz loop)
    stats.py      — 📊 Statistics
    profile.py    — 👤 Profile (XP + level bar)

Run
───
  export BOT_TOKEN="123456:ABC-..."
  python main.py
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db

from handlers.start       import router as start_router
from handlers.my_words    import router as my_words_router
from handlers.add_word    import router as add_router
from handlers.delete_word import router as delete_router
from handlers.game        import router as game_router
from handlers.stats       import router as stats_router
from handlers.profile     import router as profile_router

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)-8s]  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    # ─── Guard ────────────────────────────────────────────────────────────────
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  BOT_TOKEN not configured!\n"
            "  export BOT_TOKEN='your_token'\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        sys.exit(1)

    # ─── DB ───────────────────────────────────────────────────────────────────
    logger.info("Initialising database…")
    await init_db()
    logger.info("Database ready ✓")

    # ─── Bot & Dispatcher ─────────────────────────────────────────────────────
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers — FSM-specific routers must come before generic ones
    dp.include_router(start_router)
    dp.include_router(add_router)
    dp.include_router(delete_router)
    dp.include_router(game_router)
    dp.include_router(my_words_router)
    dp.include_router(stats_router)
    dp.include_router(profile_router)

    logger.info("Bot polling…  (Ctrl-C to stop)\n")
    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
