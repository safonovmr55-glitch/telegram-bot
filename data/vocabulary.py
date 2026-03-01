"""
data/vocabulary.py — Full AI-generated vocabulary dataset.

Structure:  VOCAB[topic][level] = list of (english, russian) tuples
Each topic has:
  Level 1 → 10 beginner words
  Level 2 → 20 intermediate words
"""

VOCAB: dict[str, dict[int, list[tuple[str, str]]]] = {

    # ═══════════════════════════════════════════════════════════════════════════
    "Animals": {
        1: [
            ("dog",      "собака"),
            ("cat",      "кот"),
            ("bird",     "птица"),
            ("fish",     "рыба"),
            ("cow",      "корова"),
            ("horse",    "лошадь"),
            ("pig",      "свинья"),
            ("duck",     "утка"),
            ("rabbit",   "кролик"),
            ("mouse",    "мышь"),
        ],
        2: [
            ("elephant",    "слон"),
            ("giraffe",     "жираф"),
            ("tiger",       "тигр"),
            ("lion",        "лев"),
            ("dolphin",     "дельфин"),
            ("penguin",     "пингвин"),
            ("crocodile",   "крокодил"),
            ("kangaroo",    "кенгуру"),
            ("rhinoceros",  "носорог"),
            ("chimpanzee",  "шимпанзе"),
            ("wolf",        "волк"),
            ("bear",        "медведь"),
            ("fox",         "лиса"),
            ("deer",        "олень"),
            ("eagle",       "орёл"),
            ("parrot",      "попугай"),
            ("camel",       "верблюд"),
            ("zebra",       "зебра"),
            ("gorilla",     "горилла"),
            ("shark",       "акула"),
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    "Food": {
        1: [
            ("bread",  "хлеб"),
            ("water",  "вода"),
            ("milk",   "молоко"),
            ("apple",  "яблоко"),
            ("egg",    "яйцо"),
            ("rice",   "рис"),
            ("soup",   "суп"),
            ("cheese", "сыр"),
            ("meat",   "мясо"),
            ("cake",   "торт"),
        ],
        2: [
            ("avocado",      "авокадо"),
            ("broccoli",     "брокколи"),
            ("mushroom",     "гриб"),
            ("eggplant",     "баклажан"),
            ("pineapple",    "ананас"),
            ("strawberry",   "клубника"),
            ("cucumber",     "огурец"),
            ("pumpkin",      "тыква"),
            ("watermelon",   "арбуз"),
            ("coconut",      "кокос"),
            ("sausage",      "колбаса"),
            ("salmon",       "лосось"),
            ("shrimp",       "креветка"),
            ("omelette",     "омлет"),
            ("pancake",      "блин"),
            ("yogurt",       "йогурт"),
            ("chocolate",    "шоколад"),
            ("popcorn",      "попкорн"),
            ("vinegar",      "уксус"),
            ("cinnamon",     "корица"),
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    "Transport": {
        1: [
            ("car",        "машина"),
            ("bus",        "автобус"),
            ("train",      "поезд"),
            ("plane",      "самолёт"),
            ("bike",       "велосипед"),
            ("boat",       "лодка"),
            ("taxi",       "такси"),
            ("truck",      "грузовик"),
            ("ship",       "корабль"),
            ("helicopter", "вертолёт"),
        ],
        2: [
            ("subway",       "метро"),
            ("tram",         "трамвай"),
            ("scooter",      "самокат"),
            ("motorcycle",   "мотоцикл"),
            ("ambulance",    "скорая помощь"),
            ("fire engine",  "пожарная машина"),
            ("cable car",    "канатная дорога"),
            ("ferry",        "паром"),
            ("yacht",        "яхта"),
            ("submarine",    "подводная лодка"),
            ("spacecraft",   "космический корабль"),
            ("hovercraft",   "судно на воздушной подушке"),
            ("monorail",     "монорельс"),
            ("snowmobile",   "снегоход"),
            ("glider",       "планёр"),
            ("tanker",       "танкер"),
            ("carriage",     "карета"),
            ("rickshaw",     "рикша"),
            ("bulldozer",    "бульдозер"),
            ("excavator",    "экскаватор"),
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    "Travel": {
        1: [
            ("hotel",     "отель"),
            ("airport",   "аэропорт"),
            ("passport",  "паспорт"),
            ("ticket",    "билет"),
            ("map",       "карта"),
            ("luggage",   "багаж"),
            ("tourist",   "турист"),
            ("visa",      "виза"),
            ("beach",     "пляж"),
            ("museum",    "музей"),
        ],
        2: [
            ("itinerary",    "маршрут"),
            ("reservation",  "бронирование"),
            ("currency",     "валюта"),
            ("customs",      "таможня"),
            ("departure",    "отправление"),
            ("arrival",      "прибытие"),
            ("hostel",       "хостел"),
            ("excursion",    "экскурсия"),
            ("souvenir",     "сувенир"),
            ("check-in",     "регистрация"),
            ("layover",      "пересадка"),
            ("boarding",     "посадка"),
            ("backpacker",   "турист с рюкзаком"),
            ("guidebook",    "путеводитель"),
            ("embassy",      "посольство"),
            ("insurance",    "страховка"),
            ("exchange",     "обмен"),
            ("destination",  "пункт назначения"),
            ("timetable",    "расписание"),
            ("platform",     "платформа"),
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    "Body": {
        1: [
            ("head",  "голова"),
            ("eye",   "глаз"),
            ("nose",  "нос"),
            ("mouth", "рот"),
            ("ear",   "ухо"),
            ("hand",  "рука"),
            ("leg",   "нога"),
            ("back",  "спина"),
            ("heart", "сердце"),
            ("tooth", "зуб"),
        ],
        2: [
            ("shoulder",   "плечо"),
            ("elbow",      "локоть"),
            ("wrist",      "запястье"),
            ("thumb",      "большой палец"),
            ("ankle",      "лодыжка"),
            ("knee",       "колено"),
            ("forehead",   "лоб"),
            ("chin",       "подбородок"),
            ("cheek",      "щека"),
            ("eyebrow",    "бровь"),
            ("eyelid",     "веко"),
            ("lung",       "лёгкое"),
            ("kidney",     "почка"),
            ("liver",      "печень"),
            ("stomach",    "желудок"),
            ("spine",      "позвоночник"),
            ("muscle",     "мышца"),
            ("nerve",      "нерв"),
            ("vein",       "вена"),
            ("skeleton",   "скелет"),
        ],
    },

    # ═══════════════════════════════════════════════════════════════════════════
    "Colors": {
        1: [
            ("red",    "красный"),
            ("blue",   "синий"),
            ("green",  "зелёный"),
            ("yellow", "жёлтый"),
            ("black",  "чёрный"),
            ("white",  "белый"),
            ("pink",   "розовый"),
            ("orange", "оранжевый"),
            ("brown",  "коричневый"),
            ("grey",   "серый"),
        ],
        2: [
            ("purple",      "фиолетовый"),
            ("turquoise",   "бирюзовый"),
            ("crimson",     "малиновый"),
            ("scarlet",     "алый"),
            ("indigo",      "индиго"),
            ("magenta",     "пурпурный"),
            ("beige",       "бежевый"),
            ("ivory",       "слоновая кость"),
            ("coral",       "коралловый"),
            ("navy",        "тёмно-синий"),
            ("olive",       "оливковый"),
            ("lilac",       "сиреневый"),
            ("maroon",      "тёмно-красный"),
            ("teal",        "сине-зелёный"),
            ("gold",        "золотой"),
            ("silver",      "серебристый"),
            ("mint",        "мятный"),
            ("peach",       "персиковый"),
            ("lavender",    "лавандовый"),
            ("chartreuse",  "жёлто-зелёный"),
        ],
    },
}


def get_words(topic: str, level: int) -> list[dict]:
    """
    Return words for a given topic and level as a list of dicts:
      {"english": str, "russian": str, "topic": str, "level": int}
    Returns empty list if topic/level not found.
    """
    pairs = VOCAB.get(topic, {}).get(level, [])
    return [
        {"english": eng, "russian": rus, "topic": topic, "level": level}
        for eng, rus in pairs
    ]


def word_count(topic: str, level: int) -> int:
    return len(VOCAB.get(topic, {}).get(level, []))
