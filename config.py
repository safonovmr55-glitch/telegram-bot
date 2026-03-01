"""
config.py — Central configuration for the Word Learning Bot.

Set BOT_TOKEN via environment variable or replace the placeholder:
    export BOT_TOKEN="123456:ABC-..."
"""
import os

# ─── Bot ──────────────────────────────────────────────────────────────────────
BOT_TOKEN = "8716343676:AAEs3Zxj5RTAGuvLl3jmfr860ZCztTb6W0E"

# ─── Database ─────────────────────────────────────────────────────────────────
DB_PATH: str = os.path.join(os.path.dirname(__file__), "wordbot.db")

# ─── Topics ───────────────────────────────────────────────────────────────────
TOPIC_ANIMALS   = "Animals"
TOPIC_DRINKS    = "Drinks"
TOPIC_TRANSPORT = "Transport"
TOPIC_CUSTOM    = "Custom"

ALL_TOPICS = [TOPIC_ANIMALS, TOPIC_DRINKS, TOPIC_TRANSPORT, TOPIC_CUSTOM]

TOPIC_EMOJI = {
    TOPIC_ANIMALS:   "🐶",
    TOPIC_DRINKS:    "🍹",
    TOPIC_TRANSPORT: "🚗",
    TOPIC_CUSTOM:    "✏️",
}

# ─── Scoring ──────────────────────────────────────────────────────────────────
BASE_SCORE_PER_CORRECT = 10
STREAK_BONUS_EVERY     = 3      # every N correct in a row → bonus
STREAK_BONUS_POINTS    = 5
XP_PER_CORRECT         = 5
XP_PER_GAME            = 20

# ─── Level thresholds ─────────────────────────────────────────────────────────
LEVEL_THRESHOLDS = [0, 100, 300, 600, 1000, 2000]
LEVEL_NAMES      = ["Novice 🌱", "Learner 📖", "Student 🎓",
                    "Scholar 🏅", "Expert 💎", "Master 🏆"]

def get_level_name(xp: int) -> str:
    lvl = 0
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            lvl = i
    return LEVEL_NAMES[lvl]
