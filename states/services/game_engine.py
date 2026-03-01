"""
services/game_engine.py — Core game logic (pure, no I/O).
"""
import random

from config import (
    BASE_SCORE_PER_CORRECT, STREAK_BONUS_EVERY, STREAK_BONUS_POINTS,
    XP_PER_CORRECT, XP_PER_GAME,
)
from ai.vocabulary import get_builtin_words


# ─── Answer checking ──────────────────────────────────────────────────────────

def check_answer(user_input: str, correct: str) -> bool:
    return user_input.strip().lower() == correct.strip().lower()


# ─── Scoring ──────────────────────────────────────────────────────────────────

def compute_turn_score(streak: int) -> int:
    """Points earned for a single correct answer."""
    bonus = (streak // STREAK_BONUS_EVERY) * STREAK_BONUS_POINTS
    return BASE_SCORE_PER_CORRECT + bonus


def compute_xp(correct: int) -> int:
    return XP_PER_GAME + correct * XP_PER_CORRECT


# ─── Word loading ─────────────────────────────────────────────────────────────

async def load_words_for_game(
    user_id: int, topic: str
) -> list[dict]:
    """
    Load words for a game session.
    Priority: user's DB words → built-in fallback.
    Always returns shuffled list.
    """
    from database.db import get_user_words
    db_words = await get_user_words(user_id, topic)

    if len(db_words) >= 3:
        words = db_words
    else:
        # Merge DB words with built-in (de-duplicate by russian_word)
        builtin = get_builtin_words(topic)
        db_russian = {w["russian_word"].lower() for w in db_words}
        extra = [w for w in builtin if w["russian_word"].lower() not in db_russian]
        words = db_words + extra

    random.shuffle(words)
    return words


# ─── Result message ───────────────────────────────────────────────────────────

def build_result_message(
    topic: str, score: int, correct: int, wrong: int, xp_gained: int
) -> str:
    total    = correct + wrong
    accuracy = round(correct / total * 100) if total else 0
    stars    = "⭐" * min(5, round(accuracy / 20))

    mood = (
        "🌟 Perfect score! You're a genius!" if accuracy == 100
        else "💪 Great job! Keep it up!" if accuracy >= 80
        else "📖 Good effort! Keep practising!" if accuracy >= 50
        else "🔁 Don't worry — review these words!"
    )

    return (
        f"🏁 <b>Game Finished!</b>\n\n"
        f"📂 Topic: <b>{topic}</b>\n"
        f"🏆 Score: <b>{score}</b>\n"
        f"✅ Correct: <b>{correct}</b>  /  {total}\n"
        f"❌ Wrong:   <b>{wrong}</b>\n"
        f"🎯 Accuracy: <b>{accuracy}%</b>  {stars}\n"
        f"✨ XP earned: <b>+{xp_gained}</b>\n\n"
        f"{mood}"
    )
