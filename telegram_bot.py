import os
from flask import Flask
from threading import Thread

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from search import search_files


TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)


@app.route("/")
def home():
    return "850MindData Bot is running"


@app.route("/health")
def health():
    return "OK"


def run_flask():
    app.run(host="0.0.0.0", port=10000)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🔎 Number Search", callback_data="search")]
    ]

    await update.message.reply_text(
        "🔎 850MindData Search Bot\n\n"
        "Number search ke liye button dabao.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "search":

        context.user_data["search_mode"] = True

        await query.message.reply_text(
            "📱 Number Search Selected\n\n"
            "Ab number bhejo."
        )


async def number_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    number = update.message.text.strip()

    if not number.isdigit():
        await update.message.reply_text(
            "⚠️ Sirf number bhejo."
        )
        return

    if not context.user_data.get("search_mode"):
        await update.message.reply_text(
            "⚠️ Pehle /start dabao aur Number Search select karo."
        )
        return

    await update.message.reply_text(
        f"🔍 Searching...\n\n"
        f"Number: `{number}`",
        parse_mode="Markdown",
    )

    try:
        search_result = search_files(number)

    except Exception as e:
        await update.message.reply_text(
            "❌ Search error hua.\n\n"
            f"{str(e)}"
        )
        return

    result = search_result["result"]
    candidates = search_result["candidates"]

    if not candidates:
        await update.message.reply_text(
            "❌ JSON range ke according is number ke liye "
            "koi candidate file nahi mili."
        )
        return

    if not result:
        await update.message.reply_text(
            "❌ Candidate files me number nahi mila.\n\n"
            f"📁 Candidate files: {len(candidates)}"
        )
        return

    data = result["data"]

    response = "✅ MATCH FOUND\n\n"
    response += f"📁 File: {result['file']}\n\n"

    for key, value in data.items():

        if value is None or value == "":
            value = "N/A"

        response += f"• {key}: {value}\n"

    await update.message.reply_text(response)


def main():

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable missing"
        )

    Thread(
        target=run_flask,
        daemon=True
    ).start()

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(button_click)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            number_search
        )
    )

    application.run_polling()


if __name__ == "__main__":
    main()
