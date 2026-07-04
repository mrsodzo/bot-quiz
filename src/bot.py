import json
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from src.config import get_bot_token, get_admin_chat_id
from src.scoring import QUESTIONS, TARIFFS, TARIFF_KEYS, SCORES
from src.db import init_db, save_quiz_result, save_contact, get_quiz_result_with_contact

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

MENU, Q1, Q2, Q3, Q4, RESULT, CONTACT_NAME, CONTACT_PHONE, CONTACT_CONFIRM = range(9)


def build_keyboard(options):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text=opt, callback_data=opt)] for opt in options])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отвечу за 1 минуту, какой формат тренировок подойдёт именно вам. Начнём?",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Начать подбор", callback_data="start_quiz")]]),
    )
    return MENU


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    return await send_question(update, context, 0)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    if index >= len(QUESTIONS):
        return await show_result(update, context)

    question = QUESTIONS[index]
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=question["text"],
            reply_markup=build_keyboard(question["options"]),
        )
    else:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question["text"],
            reply_markup=build_keyboard(question["options"]),
        )

    state = [Q1, Q2, Q3, Q4][index]
    return state


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    answer = query.data
    current_index = context.user_data.get("current_question", 0)
    key = QUESTIONS[current_index]["key"]
    context.user_data.setdefault("answers", {})[key] = answer
    context.user_data["current_question"] = current_index + 1
    return await send_question(update, context, current_index + 1)


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


async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answers = context.user_data.get("answers", {})
    tariff_name, tariff_info = calculate_tariff(answers)
    price = tariff_info["price"]
    desc = tariff_info["description"]

    result_id = save_quiz_result(
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        answers=answers,
        tariff=tariff_name,
        price=f"{price} ₽/мес",
        description=desc,
    )
    context.user_data["result_id"] = result_id
    context.user_data["tariff_name"] = tariff_name
    context.user_data["tariff_price"] = price

    text = (
        f"Судя по ответам, вам подойдёт тариф <b>{tariff_name}</b>.\n"
        f"Он включает: {desc}.\n"
        f"Стоимость: от {price} ₽/мес"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Узнать подробнее", callback_data="details")],
        [InlineKeyboardButton("Оставить заявку на консультацию", callback_data="contact")],
    ])

    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard, parse_mode="HTML")

    return RESULT


async def result_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "details":
        tariff_name = context.user_data.get("tariff_name")
        tariff_info = TARIFFS[tariff_name]
        text = (
            f"Тариф <b>{tariff_name}</b>\n"
            f"Цена: {tariff_info['price']} ₽/мес\n"
            f"Описание: {tariff_info['description']}\n\n"
            f"Хотите оставить заявку на консультацию?"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Оставить заявку", callback_data="contact")],
            [InlineKeyboardButton("Назад", callback_data="back_to_result")],
        ])
        await query.edit_message_text(text=text, reply_markup=keyboard, parse_mode="HTML")
    elif query.data == "contact":
        await query.edit_message_text("Как вас зовут?")
        return CONTACT_NAME
    elif query.data == "back_to_result":
        return await show_result(update, context)

    return RESULT


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Отлично. Теперь оставьте ваш номер телефона:")
    return CONTACT_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()
    name = context.user_data.get("name", "")
    phone = context.user_data.get("phone", "")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Все верно", callback_data="confirm")],
        [InlineKeyboardButton("Исправить", callback_data="retry_contact")],
    ])
    await update.message.reply_text(
        f"Проверьте данные:\nИмя: {name}\nТелефон: {phone}",
        reply_markup=keyboard,
    )
    return CONTACT_CONFIRM


async def confirm_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        result_id = context.user_data.get("result_id")
        name = context.user_data.get("name", "")
        phone = context.user_data.get("phone", "")
        save_contact(result_id, name, phone)
        await query.edit_message_text("Спасибо! Мы свяжемся с вами в течение часа.")

        context.application.bot_data.setdefault("_pending_leads", [])
        context.application.bot_data["_pending_leads"].append(result_id)
        await notify_admin(context, result_id)
    elif query.data == "retry_contact":
        await query.edit_message_text("Как вас зовут?")
        return CONTACT_NAME

    return ConversationHandler.END


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, result_id: int):
    data = get_quiz_result_with_contact(result_id)
    tariff = data.get("tariff", "")
    price = data.get("price", "")
    answer_lines = []
    answers = data.get("answers", {})
    if isinstance(answers, str):
        answers = json.loads(answers)
    for q in QUESTIONS:
        answer_lines.append(f"{q['text']} — {answers.get(q['key'], '-')}")

    contact = data.get("contact") or {}
    text = (
        "Новый лид из бота-квиза:\n\n"
        f"Пользователь: @{data.get('username', 'без username')} (id: {data.get('user_id')})\n"
        f"Тариф: {tariff} ({price})\n\n"
        f"Ответы:\n" + "\n".join(answer_lines) + "\n\n"
        f"Контакт: {contact.get('name', '-')}, {contact.get('phone', '-')}"
    )
    try:
        await context.bot.send_message(chat_id=get_admin_chat_id(), text=text)
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Диалог отменён. Чтобы начать заново, нажмите /start.")
    return ConversationHandler.END


def build_application() -> Application:
    init_db()
    application = Application.builder().token(get_bot_token()).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [CallbackQueryHandler(start_quiz, pattern="^start_quiz$")],
            Q1: [CallbackQueryHandler(handle_answer)],
            Q2: [CallbackQueryHandler(handle_answer)],
            Q3: [CallbackQueryHandler(handle_answer)],
            Q4: [CallbackQueryHandler(handle_answer)],
            RESULT: [CallbackQueryHandler(result_buttons)],
            CONTACT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CONTACT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CONTACT_CONFIRM: [CallbackQueryHandler(confirm_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv)
    return application
