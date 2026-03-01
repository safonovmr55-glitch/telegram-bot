"""
ai/vocabulary.py — Built-in vocabulary dataset.

Used as fallback when the user's personal database is empty
or doesn't have enough words for a chosen topic.

Structure: BUILTIN_WORDS[topic] = list of (russian, english) tuples
"""

BUILTIN_WORDS: dict[str, list[tuple[str, str]]] = {

    "Animals": [
        ("собака",   "dog"),
        ("кот",      "cat"),
        ("птица",    "bird"),
        ("рыба",     "fish"),
        ("корова",   "cow"),
        ("лошадь",   "horse"),
        ("мышь",     "mouse"),
        ("лев",      "lion"),
        ("волк",     "wolf"),
        ("медведь",  "bear"),
    ],

    "Drinks": [
        ("вода",        "water"),
        ("чай",         "tea"),
        ("кофе",        "coffee"),
        ("сок",         "juice"),
        ("молоко",      "milk"),
        ("газировка",   "soda"),
        ("пиво",        "beer"),
        ("вино",        "wine"),
        ("лимонад",     "lemonade"),
        ("смузи",       "smoothie"),
    ],

    "Transport": [
        ("машина",     "car"),
        ("автобус",    "bus"),
        ("поезд",      "train"),
        ("самолет",    "plane"),
        ("велосипед",  "bike"),
        ("такси",      "taxi"),
        ("грузовик",   "truck"),
        ("корабль",    "ship"),
        ("метро",      "subway"),
        ("самокат",    "scooter"),
    ],
}


def get_builtin_words(topic: str) -> list[dict]:
    """
    Return built-in words for a topic as a list of dicts
    compatible with database row format.
    topic == "Mixed" → return all topics shuffled.
    """
    import random

    if topic == "Mixed":
        all_pairs: list[tuple[str, str]] = []
        for t, pairs in BUILTIN_WORDS.items():
            for ru, en in pairs:
                all_pairs.append((ru, en, t))
        random.shuffle(all_pairs)
        return [
            {"russian_word": ru, "english_word": en, "topic": t, "id": None}
            for ru, en, t in all_pairs
        ]

    pairs = BUILTIN_WORDS.get(topic, [])
    result = [
        {"russian_word": ru, "english_word": en, "topic": topic, "id": None}
        for ru, en in pairs
    ]
    random.shuffle(result)
    return result


def get_all_builtin_flat() -> list[dict]:
    """Return every built-in word as a flat list."""
    result = []
    for topic, pairs in BUILTIN_WORDS.items():
        for ru, en in pairs:
            result.append({"russian_word": ru, "english_word": en, "topic": topic})
    return result
