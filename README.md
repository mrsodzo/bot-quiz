# Telegram-бот: квиз/подбор тарифа для бизнеса

Бот проводит интерактивную викторину через inline-кнопки, подбирает оптимальный тариф по матрице баллов и сохраняет результат с контактом клиента для последующей выгрузки.

## Онлайн-доступ

Бот развёрнут на Render: **@fitnes_quiz_bot**

## Сценарий

- 4 вопроса с вариантами ответов
- Подбор тарифа: «Старт», «Персональный», «Стандарт», «Профи»
- Сбор контакта: имя → телефон → подтверждение
- Уведомление админу о новом лиде

## Технологии

- Python 3.13+
- `aiogram` 3.x
- `aiohttp` (веб-сервер/webhook)
- `sqlalchemy[asyncio]` + `aiosqlite`
- `python-dotenv`

## Деплой на Render

### Через `render.yaml`

Файл `render.yaml` уже настроен:
- **Build**: `pip install -r requirements.txt`
- **Start**: `python -m src.main`
- Режим: webhook + `/health` endpoint

### Переменные окружения

- `TELEGRAM_BOT_TOKEN` — от @BotFather
- `ADMIN_CHAT_ID` — ваш чат с @userinfobot
- `WEBHOOK_PATH` — обычно `/webhook`
- `RENDER_EXTERNAL_URL` или `WEBHOOK_URL` — Render задаёт первый автоматически
- `PORT` — Render задаёт автоматически, не меняйте
- `DB_PATH` — по умолчанию `data/quiz.db`

### Примечание

При использовании бесплатного инстанса Render бот засыпает после 15 минут неактивности. При первом запросе после пробуждения ответ может задержаться до 50 секунд.

## Локальный запуск

```bash
git clone <repo>
cd bot-quiz
pip install -r requirements.txt
cp .env.example .env
python -m src.main
```

Для теста вебхука локально (например через ngrok):
```
WEBHOOK_URL=https://<ngrok-url>/webhook python -m src.main
```

## Структура

```
src/
├── __init__.py
├── main.py         # aiohttp webhook server + /health
├── bot.py          # aiogram handlers + FSM
├── config.py       # переменные окружения
├── models.py       # SQLAlchemy ORM модели
├── db.py           # async SQLite CRUD + миграции
└── scoring.py      # вопросы, тарифы, матрица баллов
```

## Инициализация БД

При старте и `python -m src.main()` автоматически:
- создаются таблицы `quiz_results` и `contacts`;
- добавляется демо-запись, чтобы база не была пустой.
