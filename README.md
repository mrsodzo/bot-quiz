# Telegram-бот: квиз/подбор тарифа для бизнеса

Бот проводит интерактивную викторину через inline-кнопки, подбирает оптимальный тариф по матрице баллов и сохраняет результат с контактом клиента для последующей выгрузки.

## Сценарий

- 4 вопроса с вариантами ответов
- Подбор тарифа: «Старт», «Персональный», «Стандарт», «Профи»
- Сбор контакта: имя → телефон → подтверждение
- Уведомление админу о новом лиде

## Технологии

- Python 3.13
- `python-telegram-bot` v21.6
- SQLite через `sqlite3`
- `python-dotenv` для конфигурации

## Установка

```bash
git clone <repo-url>
cd bot-quiz
pip install -r requirements.txt
```

## Конфигурация

Создайте `.env` на основе `.env.example`:

```
TELEGRAM_BOT_TOKEN=токен_от_BotFather
ADMIN_CHAT_ID=ID_чата_админа
```

`ADMIN_CHAT_ID` можно получить у @userinfobot.

## Запуск

```bash
python -m src.main
```

## Структура

```
src/
├── main.py        # Точка входа
├── bot.py         # ConversationHandler + хендлеры
├── config.py      # Переменные окружения
├── db.py          # SQLite CRUD
└── scoring.py     # Вопросы, тарифы, баллы
```
