QUESTIONS = [
    {
        "key": "frequency",
        "text": "Как часто планируете заниматься?",
        "options": ["1-2 раза в неделю", "3-4 раза в неделю", "Каждый день"],
    },
    {
        "key": "goal",
        "text": "Что вам важнее?",
        "options": ["Похудение", "Набор массы", "Общий тонус и здоровье"],
    },
    {
        "key": "preference",
        "text": "Предпочитаете тренироваться...",
        "options": ["Самостоятельно", "С тренером", "В группе"],
    },
    {
        "key": "experience",
        "text": "Какой у вас опыт?",
        "options": ["Новичок", "Средний уровень", "Продвинутый"],
    },
]

TARIFFS = {
    "Старт": {
        "price": "1 900",
        "description": "Базовый абонемент + вводная консультация с тренером",
    },
    "Персональный": {
        "price": "5 900",
        "description": "Индивидуальные тренировки с персональным тренером",
    },
    "Стандарт": {
        "price": "3 900",
        "description": "Групповые занятия + доступ к залу и бассейну",
    },
    "Профи": {
        "price": "8 900",
        "description": "Безлимит + сауна, массаж и приоритетная запись",
    },
}

SCORES = {
    "start_q1_1-2": 5,
    "start_q3_alone": 3,
    "start_q4_beginner": 3,
    "start_q2_lose": 1,
    "start_q2_tone": 1,
    "personal_q1_3-4": 5,
    "personal_q2_gain": 3,
    "personal_q3_trainer": 3,
    "personal_q2_tone_secondary": 1,
    "pro_q1_every": 5,
    "pro_q2_gain_sec": 1,
    "pro_q2_tone": 1,
    "pro_q3_group_sec": 1,
    "pro_q3_trainer_sec": 1,
    "pro_q4_advanced": 3,
    "standard_q1_1-2": 1,
    "standard_q1_3-4": 1,
    "standard_q1_every": 1,
    "standard_q2_lose": 3,
    "standard_q2_gain_sec": 1,
    "standard_q2_tone": 3,
    "standard_q3_group": 3,
    "standard_q3_trainer_sec": 1,
    "standard_q4_medium": 3,
}

TARIFF_KEYS = ["Старт", "Персональный", "Стандарт", "Профи"]


def calculate_tariff(answers: dict) -> tuple:
    scores = {tariff: 0 for tariff in TARIFF_KEYS}

    freq = answers.get("frequency", "")
    goal = answers.get("goal", "")
    pref = answers.get("preference", "")
    exp = answers.get("experience", "")

    if freq == "1-2 раза в неделю":
        scores["Старт"] += SCORES.get("start_q1_1-2", 0)
        scores["Стандарт"] += SCORES.get("standard_q1_1-2", 0)
    elif freq == "3-4 раза в неделю":
        scores["Персональный"] += SCORES.get("personal_q1_3-4", 0)
        scores["Стандарт"] += SCORES.get("standard_q1_3-4", 0)
    elif freq == "Каждый день":
        scores["Профи"] += SCORES.get("pro_q1_every", 0)
        scores["Стандарт"] += SCORES.get("standard_q1_every", 0)

    if goal == "Похудение":
        scores["Старт"] += SCORES.get("start_q2_lose", 0)
        scores["Стандарт"] += SCORES.get("standard_q2_lose", 0)
    elif goal == "Набор массы":
        scores["Персональный"] += SCORES.get("personal_q2_gain", 0)
        scores["Профи"] += SCORES.get("pro_q2_gain_sec", 0)
        scores["Стандарт"] += SCORES.get("standard_q2_gain_sec", 0)
    elif goal == "Общий тонус и здоровье":
        scores["Персональный"] += SCORES.get("personal_q2_tone_secondary", 0)
        scores["Профи"] += SCORES.get("pro_q2_tone", 0)
        scores["Старт"] += SCORES.get("start_q2_tone", 0)
        scores["Стандарт"] += SCORES.get("standard_q2_tone", 0)

    if pref == "Самостоятельно":
        scores["Старт"] += SCORES.get("start_q3_alone", 0)
    elif pref == "С тренером":
        scores["Персональный"] += SCORES.get("personal_q3_trainer", 0)
        scores["Профи"] += SCORES.get("pro_q3_trainer_sec", 0)
        scores["Стандарт"] += SCORES.get("standard_q3_trainer_sec", 0)
    elif pref == "В группе":
        scores["Стандарт"] += SCORES.get("standard_q3_group", 0)
        scores["Профи"] += SCORES.get("pro_q3_group_sec", 0)

    if exp == "Новичок":
        scores["Старт"] += SCORES.get("start_q4_beginner", 0)
    elif exp == "Средний уровень":
        scores["Стандарт"] += SCORES.get("standard_q4_medium", 0)
    elif exp == "Продвинутый":
        scores["Профи"] += SCORES.get("pro_q4_advanced", 0)

    best_tariff = max(scores, key=scores.get)
    return best_tariff, TARIFFS[best_tariff]
