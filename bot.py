import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    filters
)

# Загрузка таблицы
with open("prufz_table.json", "r", encoding="utf-8") as f:
    prufz_table = json.load(f)

user_languages = {}

translations = {
    "ru": {
        "start": "Привет! Выбери язык.",
        "ask": "Введи номер ячейки (Reihe), и я скажу тебе код подтверждения (Prüfz.).",
        "not_found": "Такой ячейки нет в базе. Попробуй другой номер.",
        "result": "Prüfz. для ячейки {cell}: {code}"
    },
    "pl": {
        "start": "Cześć! Wybierz język.",
        "ask": "Wpisz numer komórki (Reihe), a podam Ci kod potwierdzający (Prüfz.).",
        "not_found": "Nie znaleziono takiej komórki. Spróbuj inny numer.",
        "result": "Prüfz. dla komórki {cell}: {code}"
    },
    "de": {
        "start": "Hallo! Wähle eine Sprache.",
        "ask": "Gib die Zellnummer (Reihe) ein, ich gebe dir den Prüfz.-Code.",
        "not_found": "Diese Zelle wurde nicht gefunden. Versuche eine andere Nummer.",
        "result": "Prüfz. für Zelle {cell}: {code}"
    },
    "en": {
        "start": "Hi! Choose a language.",
        "ask": "Enter the cell number (Reihe), and I'll give you the Prüfz. code.",
        "not_found": "That cell is not in the database. Try another number.",
        "result": "Prüfz. for cell {cell}: {code}"
    }
}

language_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Русский", "Polski", "Deutsch", "English"]],
    resize_keyboard=True,
    one_time_keyboard=True
)

language_map = {
    "Русский": "ru",
    "Polski": "pl",
    "Deutsch": "de",
    "English": "en"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(translations["ru"]["start"], reply_markup=language_keyboard)

async def handle_language_or_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_input = update.message.text.strip()

    if user_input in language_map:
        user_languages[chat_id] = language_map[user_input]
        lang = user_languages[chat_id]
        await update.message.reply_text(translations[lang]["ask"])
        return

    lang = user_languages.get(chat_id, "en")
    if user_input in prufz_table:
        code = prufz_table[user_input]
        await update.message.reply_text(translations[lang]["result"].format(cell=user_input, code=code))
    else:
        await update.message.reply_text(translations[lang]["not_found"])

if name == "__main__":
    import asyncio
    from aiohttp import web

    async def webhook_handler(request):
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response()

    async def main():
        global application
        application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_or_input))
        
        await application.initialize()

        app = web.Application()
        app.router.add_post("/", webhook_handler)

        port = int(os.getenv("PORT", 10000))
        await application.start()
        await application.bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        print("Bot is up and running via webhook...")

        # Бесконечный цикл
        await asyncio.Event().wait()

    asyncio.run(main())