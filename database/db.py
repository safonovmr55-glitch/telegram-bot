"""
database/db.py — All async SQLite operations via aiosqlite.

Tables
──────
words   — per-user vocabulary store
users   — per-user XP, streak, accuracy
sessions — completed game history
"""

import aiosqlite
from datetime import date
from typing import Optional

from config import DB_PATH


# ═══════════════════════════════════════════════════════════════════════════════
#  Schema
# ═══════════════════════════════════════════════════════════════════════════════

async def init_db() -> None:
    """Create all tables on first run. Safe to call on every startup."""
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id         INTEGER PRIMARY KEY,
                username        TEXT    DEFAULT '',
                first_name      TEXT    DEFAULT '',
                xp              INTEGER NOT NULL DEFAULT 0,
                level           INTEGER NOT NULL DEFAULT 1,
                streak          INTEGER NOT NULL DEFAULT 0,
                best_streak     INTEGER NOT NULL DEFAULT 0,
                total_correct   INTEGER NOT NULL DEFAULT 0,
                total_wrong     INTEGER NOT NULL DEFAULT 0,
                games_played    INTEGER NOT NULL DEFAULT 0,
                created_at      TEXT    NOT NULL DEFAULT (date('now'))
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                russian_word     TEXT    NOT NULL,
                english_word     TEXT    NOT NULL,
                topic            TEXT    NOT NULL DEFAULT 'Custom',
                correct_count    INTEGER NOT NULL DEFAULT 0,
                wrong_count      INTEGER NOT NULL DEFAULT 0,
                streak           INTEGER NOT NULL DEFAULT 0,
                next_review_date TEXT    NOT NULL DEFAULT (date('now')),
                created_at       TEXT    NOT NULL DEFAULT (date('now'))
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                topic       TEXT    NOT NULL,
                score       INTEGER NOT NULL DEFAULT 0,
                correct     INTEGER NOT NULL DEFAULT 0,
                wrong       INTEGER NOT NULL DEFAULT 0,
                accuracy    REAL    NOT NULL DEFAULT 0.0,
                played_at   TEXT    NOT NULL DEFAULT (date('now'))
            )
        """)
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  Users
# ═══════════════════════════════════════════════════════════════════════════════

async def get_or_create_user(user_id: int, username: str, first_name: str) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()

        if row:
            return dict(row)

        await db.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username or "", first_name or ""),
        )
        await db.commit()

        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
        return dict(row)


async def get_user(user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None


async def update_user_after_game(
    user_id: int, correct: int, wrong: int, xp_gained: int, streak: int
) -> None:
    best_streak_sql = "MAX(best_streak, ?)"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"""
            UPDATE users SET
                total_correct = total_correct + ?,
                total_wrong   = total_wrong   + ?,
                xp            = xp + ?,
                streak        = ?,
                best_streak   = {best_streak_sql},
                games_played  = games_played + 1
            WHERE user_id = ?
            """,
            (correct, wrong, xp_gained, streak, streak, user_id),
        )
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  Words — CRUD
# ═══════════════════════════════════════════════════════════════════════════════

async def add_word(
    user_id: int, russian: str, english: str, topic: str
) -> int:
    """Insert a word and return its new id."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            INSERT INTO words (user_id, russian_word, english_word, topic)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, russian.strip(), english.strip(), topic),
        )
        await db.commit()
        return cur.lastrowid


async def get_user_words(user_id: int, topic: Optional[str] = None) -> list[dict]:
    """Return all (or topic-filtered) words for the given user."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if topic and topic != "Mixed":
            async with db.execute(
                "SELECT * FROM words WHERE user_id = ? AND topic = ? ORDER BY id",
                (user_id, topic),
            ) as cur:
                rows = await cur.fetchall()
        else:
            async with db.execute(
                "SELECT * FROM words WHERE user_id = ? ORDER BY id",
                (user_id,),
            ) as cur:
                rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_word_by_id(word_id: int, user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM words WHERE id = ? AND user_id = ?",
            (word_id, user_id),
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None


async def delete_word(word_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM words WHERE id = ? AND user_id = ?",
            (word_id, user_id),
        )
        await db.commit()
    return cur.rowcount > 0


async def update_word_stats(word_id: int, correct: bool) -> None:
    """Increment correct/wrong counter and update streak for a DB word."""
    from datetime import timedelta
    if word_id is None:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        if correct:
            await db.execute(
                """
                UPDATE words SET
                    correct_count = correct_count + 1,
                    streak        = streak + 1,
                    next_review_date = date('now', '+7 days')
                WHERE id = ?
                """,
                (word_id,),
            )
        else:
            await db.execute(
                """
                UPDATE words SET
                    wrong_count = wrong_count + 1,
                    streak      = 0,
                    next_review_date = date('now', '+1 days')
                WHERE id = ?
                """,
                (word_id,),
            )
        await db.commit()


async def count_user_words(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM words WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
    return row[0] if row else 0


async def count_learned_words(user_id: int) -> int:
    """Words with streak >= 3 are considered 'learned'."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM words WHERE user_id = ? AND streak >= 3",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
    return row[0] if row else 0


# ═══════════════════════════════════════════════════════════════════════════════
#  Game sessions
# ═══════════════════════════════════════════════════════════════════════════════

async def save_session(
    user_id: int, topic: str, score: int, correct: int, wrong: int
) -> None:
    total    = correct + wrong
    accuracy = round(correct / total * 100, 1) if total else 0.0
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO sessions (user_id, topic, score, correct, wrong, accuracy)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, topic, score, correct, wrong, accuracy),
        )
        await db.commit()


async def get_user_accuracy(user_id: int) -> float:
    user = await get_user(user_id)
    if not user:
        return 0.0
    total = user["total_correct"] + user["total_wrong"]
    return round(user["total_correct"] / total * 100, 1) if total else 0.0
