from src.config import get_admin_chat_id

ADMIN_CHAT_ID = get_admin_chat_id()

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
