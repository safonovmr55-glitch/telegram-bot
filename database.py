"""
database.py — All SQLite operations for the bot.

Uses aiosqlite for non-blocking async database access,
which is required when working inside an asyncio event loop (aiogram).

Install:  pip install aiosqlite
"""

import aiosqlite
from datetime import date, datetime
from typing import Optional

from config import DB_PATH


# ═══════════════════════════════════════════════════════════════════════════════
#  Schema initialisation
# ═══════════════════════════════════════════════════════════════════════════════

async def init_db() -> None:
    """
    Create the 'words' table if it doesn't already exist.
    Called once on bot startup.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                russian_word     TEXT    NOT NULL,
                english_word     TEXT    NOT NULL,
                interval         INTEGER NOT NULL DEFAULT 1,
                next_review_date TEXT    NOT NULL,
                correct_count    INTEGER NOT NULL DEFAULT 0,
                wrong_count      INTEGER NOT NULL DEFAULT 0,
                streak           INTEGER NOT NULL DEFAULT 0
            )
        """)
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  Word CRUD
# ═══════════════════════════════════════════════════════════════════════════════

async def add_word(
    user_id: int,
    russian_word: str,
    english_word: str,
) -> None:
    """
    Insert a new word pair for the given user.
    The first review is scheduled for today so it appears immediately.
    """
    today = date.today().isoformat()  # e.g. "2024-05-20"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO words
                (user_id, russian_word, english_word, interval, next_review_date)
            VALUES (?, ?, ?, 1, ?)
            """,
            (user_id, russian_word.strip(), english_word.strip(), today),
        )
        await db.commit()


async def get_due_words(user_id: int) -> list[dict]:
    """
    Return all word rows that are due for review today or earlier.
    Result is a list of dicts for easy access by key.
    """
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row   # lets us use row["column_name"]
        async with db.execute(
            """
            SELECT * FROM words
            WHERE user_id = ?
              AND next_review_date <= ?
            ORDER BY next_review_date ASC
            """,
            (user_id, today),
        ) as cursor:
            rows = await cursor.fetchall()
    # Convert Row objects to plain dicts
    return [dict(row) for row in rows]


async def update_word_after_review(
    word_id: int,
    correct: bool,
    new_interval: int,
    new_streak: int,
) -> None:
    """
    Update a word's SRS fields after the user answers.
    next_review_date is calculated from today + new_interval days.
    """
    from datetime import timedelta

    next_date = (date.today() + timedelta(days=new_interval)).isoformat()

    # Build the correct/wrong counter increment dynamically
    counter_col = "correct_count" if correct else "wrong_count"

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"""
            UPDATE words
            SET interval         = ?,
                next_review_date = ?,
                streak           = ?,
                {counter_col}    = {counter_col} + 1
            WHERE id = ?
            """,
            (new_interval, next_date, new_streak, word_id),
        )
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  Statistics
# ═══════════════════════════════════════════════════════════════════════════════

async def get_stats(user_id: int) -> dict:
    """
    Aggregate statistics for a user:
      - total_words
      - learned       (interval >= 7 days — well-known words)
      - in_progress
      - total_correct
      - total_wrong
      - accuracy      (percentage, rounded to 1 decimal)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT
                COUNT(*)                              AS total_words,
                SUM(CASE WHEN interval >= 7 THEN 1 ELSE 0 END) AS learned,
                SUM(correct_count)                    AS total_correct,
                SUM(wrong_count)                      AS total_wrong
            FROM words
            WHERE user_id = ?
            """,
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()

    total_words   = row[0] or 0
    learned       = row[1] or 0
    total_correct = row[2] or 0
    total_wrong   = row[3] or 0
    in_progress   = total_words - learned

    total_answers = total_correct + total_wrong
    accuracy      = (total_correct / total_answers * 100) if total_answers else 0.0

    return {
        "total_words":   total_words,
        "learned":       learned,
        "in_progress":   in_progress,
        "total_correct": total_correct,
        "total_wrong":   total_wrong,
        "accuracy":      round(accuracy, 1),
    }
