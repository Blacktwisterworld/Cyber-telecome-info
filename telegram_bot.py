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

from file_groups import load_file_groups
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
        [
            InlineKeyboardButton(
                "🔟 10 Digit Number",
                callback_data="10_digit"
            )
        ],
        [
            InlineKeyboardButton(
                "🔢 13 Digit Number",
                callback_data="13_digit"
            )
        ],
        [
            InlineKeyboardButton(
                "🔀 Mix Number",
                callback_data="mix"
            )
        ],
    ]

    await update.message.reply_text(
        "🔎 850MindData Search Bot\n\n"
        "Search type select karo:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    groups = load_file_groups()

    selected = query.data

    if selected == "10_digit":
        files = groups["10_digit"] + groups["mix"]

        context.user_data["files"] = files

        text = (
            "🔟 10 Digit search selected.\n\n"
            f"📁 Files to search: {len(files)}\n\n"
            "Number bhejo."
        )

    elif selected == "13_digit":
        files = groups["13_digit"] + groups["mix"]

        context.user_data["files"] = files

        text = (
            "🔢 13 Digit search selected.\n\n"
            f"📁 Files to search: {len(files)}\n\n"
            "Number bhejo."
        )

    else:
        files = groups["mix"]

        context.user_data["files"] = files

        text = (
            "🔀 Mix search selected.\n\n"
            f"📁 Files to search: {len(files)}\n\n"
            "Number bhejo."
        )

    await query.message.reply_text(text)


async def number_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    if not number.isdigit():
        await update.message.reply_text(
            "⚠️ Sirf number bhejo."
        )
        return

    files = context.user_data.get("files")

    if not files:
        await update.message.reply_text(
            "⚠️ Pehle /start dabakar search type select karo."
        )
        return

    await update.message.reply_text(
        f"🔍 Searching...\n\nNumber: `{number}`",
        parse_mode="Markdown",
    )

    result = search_files(number, files)

    if not result:
        await update.message.reply_text(
            "❌ Match nahi mila."
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
        raise RuntimeError("BOT_TOKEN environment variable missing")

    Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TOKEN).build()

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
