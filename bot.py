# Telegram

import os
from dotenv import load_dotenv
from project import conversation_flow, Tracker, format_report
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

tracker = Tracker()

welcome_txt = """
Welcome to Personal Finance Tracker Bot!

Commands:

/add - Add new transaction
/report - Show financial report
"""

action_keyboard = ReplyKeyboardMarkup(
    [["Income", "Expense"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

category_keyboard = ReplyKeyboardMarkup(
    [
        ["Food", "Transport"],
        ["Housing", "Shopping"],
        ["Bills", "Health"],
        ["Education", "Entertainment"],
        ["Travel", "Personal"],
        ["Other"],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

account_keyboard = ReplyKeyboardMarkup(
    [
        ["Meli", "Saderat", "Melat"],
        ["Saman", "Mehr", "Pasargad"],
        ["Keshavarzi", "Tejarat", "Maskan"],
        ["Dey", "Parsian", "Resalat"],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


app = ApplicationBuilder().token(TOKEN).build()


async def start_command(update, context):
    await update.message.reply_text(welcome_txt)


async def add_command(update, context):
    user_id = update.message.from_user.id
    tracker.reset_user_state(user_id)
    await update.message.reply_text(
        "Choose transaction type:",
        reply_markup=action_keyboard,
    )


async def handle_message(update, context):
    user_id = update.message.from_user.id
    user_input = update.message.text

    response = conversation_flow(tracker, user_id, user_input)

    state = tracker.get_user_state(user_id)

    if state and state["state"] == "WAITING_FOR_CATEGORY":
        keyboard = category_keyboard

    elif state and state["state"] == "WAITING_FOR_ACCOUNT":
        keyboard = account_keyboard

    else:
        keyboard = ReplyKeyboardRemove()

    await update.message.reply_text(
        response,
        reply_markup=keyboard
    )

async def report_command(update, context):
    user_id = update.message.from_user.id
    report = format_report(user_id, tracker)
    await update.message.reply_text(report)


async def cancel_command(update, context):
    user_id = update.message.from_user.id
    tracker.delete_user_state(user_id)
    await update.message.reply_text("Transaction canceled.")


async def error_handler(update, context):
    print(f"Exception: {context.error}")

    if update and update.message:
        await update.message.reply_text("Something went wrong. Please try again.")


app.add_handler(CommandHandler("start", start_command))

app.add_handler(CommandHandler("add", add_command))

app.add_handler(CommandHandler("report", report_command))

app.add_handler(CommandHandler("cancel", cancel_command))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.add_error_handler(error_handler)

app.run_polling()
