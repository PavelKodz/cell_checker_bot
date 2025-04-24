import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Загружаем таблицу с кодами
with open("prufz_table.json", "r", encoding="utf-8") as f:
    prufz_table = json.load(f)

# Словарь для хранения выбранного языка для каждого пользователя
user_languages = {}

# Переводы
translations = {
    "ru": {
        "start": "Привет! Выбери язык:",
        "ask": "Введи номер ячейки (Reihe), и я скажу тебе код подтверждения (Prüfz.).",
        "not_found": "Такой ячейки нет в базе. Попробуй другой номер.",
        "result": "Prüfz. для ячейки {cell}: {code}"
    },
    "pl": {
        "start": "Cześć! Wybierz język:",
        "ask": "Wpisz numer komórki (Reihe), a podam Ci kod potwierdzający (Prüfz.).",
        "not_found": "Nie znaleziono takiej komórki. Spróbuj inny numer.",
        "result": "Prüfz. dla komórki {cell}: {code}"
    },
    "de": {
        "start": "Hallo! Wähle eine Sprache:",
        "ask": "Gib die Zellennummer (Reihe) ein, ich gebe dir den Prüfz.-Code.",
        "not_found": "Diese Zelle wurde nicht gefunden. Versuche eine andere Nummer.",
        "result": "Prüfz. für Zelle {cell}: {code}"
    },
    "en": {
        "start": "Hi! Choose a language:",
        "ask": "Enter the cell number (Reihe), and I’ll give you the Prüfz. code.",
        "not_found": "That cell is not in the database. Try another number.",
        "result": "Prüfz. for cell {cell}: {code}"
    }
}

# Кнопки с языками
language_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Русский", "Polski", "Deutsch", "English"]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Соответствие кнопок и кодов языков
language_map = {
    "Русский": "ru",
    "Polski": "pl",
    "Deutsch": "de",
    "English": "en"
}

# Обработка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(translations["ru"]["start"], reply_markup=language_keyboard)

# Обработка /language — смена языка
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(translations["ru"]["start"], reply_markup=language_keyboard)

# Обработка выбора языка или ввода
async def handle_language_or_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_input = update.message.text.strip()

    # Если выбрали язык
    if user_input in language_map:
        user_languages[chat_id] = language_map[user_input]
        lang = user_languages[chat_id]
        await update.message.reply_text(translations[lang]["ask"])
        return

    # Если ввели ячейку
    lang = user_languages.get(chat_id, "en")
    if user_input in prufz_table:
        code = prufz_table[user_input]
        await update.message.reply_text(translations[lang]["result"].format(cell=user_input, code=code))
    else:
        await update.message.reply_text(translations[lang]["not_found"])

# Запуск бота
import os

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("language", change_language))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_or_input))

async def start_bot():
    await app.bot.set_webhook(WEBHOOK_URL)
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL
    )

import asyncio
asyncio.run(start_bot())