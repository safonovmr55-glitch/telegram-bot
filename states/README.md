# 🤖 Word Learning Bot

A fully functional Telegram vocabulary learning bot built with Python + aiogram 3.x.

---

## 📁 Project structure

```
wordbot/
├── main.py                      ← Entry point
├── config.py                    ← Token, topics, scoring, level system
├── requirements.txt
│
├── ai/
│   └── vocabulary.py            ← 30 built-in words (3 topics × 10)
│
├── database/
│   └── db.py                    ← All async SQLite queries
│
├── handlers/
│   ├── start.py                 ← /start + main menu routing
│   ├── my_words.py              ← 📚 My Words (browser + word detail)
│   ├── add_word.py              ← ➕ Add Word (3-step FSM)
│   ├── delete_word.py           ← ❌ Delete Word (list + confirmation)
│   ├── game.py                  ← 🎮 Play Game (quiz loop + scoring)
│   ├── stats.py                 ← 📊 Statistics
│   └── profile.py               ← 👤 Profile (XP + level progress bar)
│
├── keyboards/
│   └── keyboards.py             ← All ReplyKeyboard + InlineKeyboard layouts
│
├── services/
│   └── game_engine.py           ← Score logic, word loading, result builder
│
└── states/
    └── states.py                ← FSM StatesGroups
```

---

## 🚀 Quick start

```bash
pip install -r requirements.txt
export BOT_TOKEN="123456:ABC-your-token"
python main.py
```

---

## 🎮 Features

| Button | Behaviour |
|---|---|
| 📚 My Words | Browse personal words by topic with pagination; if empty → shows built-in library |
| 🎮 Play Game | Choose topic → quiz loop (Russian → English); built-in fallback if no DB words |
| ➕ Add Word | 3-step FSM: Russian → English → Topic |
| ❌ Delete Word | Paginated word list → tap word → [Yes]/[No] confirmation dialog |
| 📊 Statistics | Totals, accuracy bar, streak, games played |
| 👤 Profile | XP, level name, progress bar to next level |

---

## 🗄️ Database schema

```sql
-- User profiles
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    total_wrong INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0,
    ...
);

-- Vocabulary store
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    russian_word TEXT NOT NULL,
    english_word TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT 'Custom',
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    next_review_date TEXT NOT NULL,
    ...
);

-- Completed game history
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    wrong INTEGER DEFAULT 0,
    accuracy REAL DEFAULT 0.0,
    played_at TEXT NOT NULL
);
```

---

## 🏆 Scoring formula

```
turn_score = 10 + (streak // 3) × 5
xp_earned  = 20 + correct_answers × 5
```

## 📈 Level system

| XP | Level |
|---|---|
| 0 | 🌱 Novice |
| 100 | 📖 Learner |
| 300 | 🎓 Student |
| 600 | 🏅 Scholar |
| 1000 | 💎 Expert |
| 2000 | 🏆 Master |
