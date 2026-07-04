import json
import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.config import get_admin_chat_id
from src.db import save_quiz_result, save_contact, get_quiz_result_with_contact
from src.scoring import QUESTIONS, TARIFFS, calculate_tariff

router = Router()
logger = logging.getLogger(__name__)


class QuizStates(StatesGroup):
    menu = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    result = State()
    contact_name = State()
    contact_phone = State()
    contact_confirm = State()


def kb(options):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=o, callback_data=o)] for o in options])


def kb_result():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Узнать подробнее", callback_data="details")],
            [InlineKeyboardButton("Оставить заявку на консультацию", callback_data="contact")],
        ]
    )


def kb_confirm():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Все верно", callback_data="confirm")],
            [InlineKeyboardButton("Исправить", callback_data="retry_contact")],
        ]
    )


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Отвечу за 1 минуту, какой формат тренировок подойдёт именно вам. Начнём?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Начать подбор", callback_data="start_quiz")]
            ]
        ),
    )
    await state.set_state(QuizStates.menu)


@router.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.update_data(answers={}, current_question=0)
    await send_question(callback.message, state, 0)
    await state.set_state(QuizStates.q1)


@router.callback_query(F.data)
async def handle_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    current_state = await state.get_state()

    if current_state == QuizStates.result.state:
        await handle_result_action(callback, state)
        return

    if current_state == QuizStates.contact_confirm.state:
        if callback.data == "confirm":
            await confirm_contact(callback, state, bot)
        elif callback.data == "retry_contact":
            await retry_contact(callback, state)
        return

    if current_state == QuizStates.menu.state and callback.data != "start_quiz":
        await callback.answer("Сначала нажмите «Начать подбор»")
        return

    state_to_idx = {
        QuizStates.q1.state: 0,
        QuizStates.q2.state: 1,
        QuizStates.q3.state: 2,
        QuizStates.q4.state: 3,
    }
    if current_state not in state_to_idx:
        await callback.answer("Сначала нажмите /start")
        return

    await callback.answer()
    idx = state_to_idx[current_state]
    answers = data.get("answers", {})
    answers[QUESTIONS[idx]["key"]] = callback.data
    await state.update_data(answers=answers, current_question=idx + 1)

    next_idx = idx + 1
    if next_idx >= len(QUESTIONS):
        await state.set_state(QuizStates.result)
        await show_result(callback.message, state)
    else:
        await send_question(callback.message, state, next_idx)
        next_state = [QuizStates.q1, QuizStates.q2, QuizStates.q3, QuizStates.q4][next_idx]
        await state.set_state(next_state)


async def send_question(message: Message, state: FSMContext, index: int):
    if index >= len(QUESTIONS):
        return
    q = QUESTIONS[index]
    await message.answer(q["text"], reply_markup=kb(q["options"]))


async def show_result(message: Message, state: FSMContext):
    answers = (await state.get_data()).get("answers", {})
    tariff_name, tariff_info = calculate_tariff(answers)
    price = tariff_info["price"]
    desc = tariff_info["description"]

    result_id = await save_quiz_result(
        user_id=message.chat.id,
        username=message.chat.username,
        answers=answers,
        tariff=tariff_name,
        price=f"{price} ₽/мес",
        description=desc,
    )
    await state.update_data(result_id=result_id, tariff_name=tariff_name, tariff_price=price)

    text = (
        f"Судя по ответам, вам подойдёт тариф <b>{tariff_name}</b>.\n"
        f"Он включает: {desc}.\n"
        f"Стоимость: от {price} ₽/мес"
    )
    await message.answer(text=text, reply_markup=kb_result(), parse_mode=ParseMode.HTML)
    await state.set_state(QuizStates.result)


async def handle_result_action(callback: CallbackQuery, state: FSMContext):
    if callback.data == "details":
        tariff_name = (await state.get_data()).get("tariff_name")
        tariff_info = TARIFFS[tariff_name]
        text = (
            f"Тариф <b>{tariff_name}</b>\n"
            f"Цена: {tariff_info['price']} ₽/мес\n"
            f"Описание: {tariff_info['description']}\n\n"
            f"Хотите оставить заявку на консультацию?"
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("Оставить заявку", callback_data="contact")],
                    [InlineKeyboardButton("Назад", callback_data="back_to_result")],
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
    elif callback.data == "contact":
        await callback.message.edit_text("Как вас зовут?")
        await state.set_state(QuizStates.contact_name)
    elif callback.data == "back_to_result":
        await show_result(callback.message, state)


@router.message(StateFilter(QuizStates.contact_name))
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Отлично. Теперь оставьте ваш номер телефона:")
    await state.set_state(QuizStates.contact_phone)


@router.message(StateFilter(QuizStates.contact_phone))
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    data = await state.get_data()
    await message.answer(
        f"Проверьте данные:\nИмя: {data.get('name', '')}\nТелефон: {data.get('phone', '')}",
        reply_markup=kb_confirm(),
    )
    await state.set_state(QuizStates.contact_confirm)


async def confirm_contact(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    result_id = data.get("result_id")
    name = data.get("name", "")
    phone = data.get("phone", "")
    await save_contact(result_id, name, phone)
    await callback.message.edit_text("Спасибо! Мы свяжемся с вами в течение часа.")
    await notify_admin(bot, result_id)
    await state.clear()


async def retry_contact(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Как вас зовут?")
    await state.set_state(QuizStates.contact_name)


async def notify_admin(bot: Bot, result_id: int):
    data = await get_quiz_result_with_contact(result_id)
    if not data:
        return
    answers = json.loads(data["answers"]) if isinstance(data["answers"], str) else data["answers"]
    answer_lines = [f"{q['text']} — {answers.get(q['key'], '-')}" for q in QUESTIONS]
    contact = data.get("contact") or {}
    text = (
        "Новый лид из бота-квиза:\n\n"
        f"Пользователь: @{data.get('username', 'без username')} (id: {data.get('user_id')})\n"
        f"Тариф: {data.get('tariff')} ({data.get('price')})\n\n"
        f"Ответы:\n" + "\n".join(answer_lines) + "\n\n"
        f"Контакт: {contact.get('name', '-')}, {contact.get('phone', '-')}"
    )
    try:
        await bot.send_message(chat_id=get_admin_chat_id(), text=text)
    except Exception as exc:
        logger.error("Failed to notify admin: %s", exc)
