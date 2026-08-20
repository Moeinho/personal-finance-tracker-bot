"""
bot.py - Telegram bot interface for the Personal Finance Tracker.
Handles user interactions, commands, keyboards, and message processing.
"""

import os
from dotenv import load_dotenv
from tracker import Tracker
from project import VALID_ACCOUNTS, VALID_CATEGORIES
from project import conversation_flow, format_report, recent_transactions
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import BotCommand

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

tracker = Tracker()


help_txt = """
❓ HELP

➕ Add Transaction
Add a new income or expense.

📊 Report
View your financial summary.

🕐 Recent
View your latest transactions.

🔄 Reset
Delete all your transactions.

Commands:
/start - Main menu
/add - Add transaction
/report - Financial report
/recent - Recent transactions
/cancel - Cancel current transaction
/reset - Delete all transactions
/help - Show help
"""


start_keyboard = ReplyKeyboardMarkup(
    [
        ["➕ Add Transaction"],
        ["📊 Report", "🕐 Recent"],
        ["❓ Help", "🔄 Reset"],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

action_keyboard = ReplyKeyboardMarkup(
    [["💰 Income", "💸 Expense"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


reset_keyboard = ReplyKeyboardMarkup(
    [["✅ Yes, Reset"], ["❌ Cancel"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def build_keyboard(items, columns=3):
    rows = [items[i : i + columns] for i in range(0, len(items), columns)]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)


account_keyboard = build_keyboard(VALID_ACCOUNTS)
category_keyboard = build_keyboard(VALID_CATEGORIES, columns=2)


async def post_init(application):
    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("add", "Add transaction"),
        BotCommand("report", "Show financial report"),
        BotCommand("recent", "Recent transactions"),
        BotCommand("cancel", "Cancel transaction"),
        BotCommand("reset", "Delete all transactions"),
        BotCommand("help", "Show help"),
    ]
    await application.bot.set_my_commands(commands)


app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()


async def start_command(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.first_name
    tracker.reset_user_state(user_id)

    welcome_txt = f"""
👋 Welcome, {username}!

💰 Personal Finance Tracker

Track your income and expenses, keep an eye on your balance, and stay in control of your finances.

What would you like to do?
"""
    await update.message.reply_text(welcome_txt, reply_markup=start_keyboard)


async def add_command(update, context):
    user_id = update.message.from_user.id
    state = tracker.get_user_state(user_id)

    if state and state["state"] != "WAITING_FOR_ACTION":
        message = "You already have an active transaction. Use /cancel first."
        await update.message.reply_text(message)
        return

    tracker.reset_user_state(user_id)
    await update.message.reply_text(
        "Choose transaction type:",
        reply_markup=action_keyboard,
    )


async def report_command(update, context):
    user_id = update.message.from_user.id
    report = format_report(user_id, tracker)
    await update.message.reply_text(report, reply_markup=start_keyboard)


async def cancel_command(update, context):
    user_id = update.message.from_user.id
    state = tracker.get_user_state(user_id)

    if state is None or state["state"] == "WAITING_FOR_ACTION":
        await update.message.reply_text("There is no active transaction to cancel.")
        return

    tracker.delete_user_state(user_id)
    await update.message.reply_text(
        "Transaction canceled.", reply_markup=start_keyboard
    )


async def help_command(update, context):
    await update.message.reply_text(help_txt)


async def recent_command(update, context):
    user_id = update.message.from_user.id
    recent = recent_transactions(user_id, tracker, 10)
    await update.message.reply_text(recent, reply_markup=start_keyboard)


async def reset_command(update, context):
    warning = "⚠️ This will permanently delete all your transactions."
    await update.message.reply_text(warning, reply_markup=reset_keyboard)


async def error_handler(update, context):
    print(f"Exception: {context.error}")

    if update and update.message:
        await update.message.reply_text("Something went wrong. Please try again.")


# Start menu buttons
async def button_handler(update, context):
    user_id = update.message.from_user.id
    user_input = update.message.text

    if user_input == "📊 Report":
        await report_command(update, context)

    elif user_input == "❓ Help":
        await help_command(update, context)

    elif user_input == "➕ Add Transaction":
        await add_command(update, context)

    elif user_input == "💰 Income":
        response = conversation_flow(tracker, user_id, "income")
        await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())

    elif user_input == "💸 Expense":
        response = conversation_flow(tracker, user_id, "expense")
        await update.message.reply_text(response, reply_markup=category_keyboard)

    elif user_input == "🕐 Recent":
        await recent_command(update, context)

    elif user_input == "🔄 Reset":
        await reset_command(update, context)

    elif user_input == "❌ Cancel":
        await update.message.reply_text("Reset canceled.", reply_markup=start_keyboard)

    elif user_input == "✅ Yes, Reset":
        tracker.delete_user_transactions(user_id)
        tracker.delete_user_state(user_id)
        await update.message.reply_text(
            "All transactions deleted", reply_markup=start_keyboard
        )


async def handle_message(update, context):
    user_id = update.message.from_user.id
    user_input = update.message.text

    state_before = tracker.get_user_state(user_id)
    response = conversation_flow(tracker, user_id, user_input)
    state_after = tracker.get_user_state(user_id)

    if state_after and state_after["state"] == "WAITING_FOR_CATEGORY":
        keyboard = category_keyboard
    elif state_after and state_after["state"] == "WAITING_FOR_ACCOUNT":
        keyboard = account_keyboard
    elif (
        state_before
        and state_before["state"] == "WAITING_FOR_DESCRIPTION"
        and state_after is None
    ):
        keyboard = start_keyboard
    else:
        keyboard = ReplyKeyboardRemove()
    await update.message.reply_text(response, reply_markup=keyboard)


app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("add", add_command))
app.add_handler(CommandHandler("report", report_command))
app.add_handler(CommandHandler("cancel", cancel_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("recent", recent_command))
app.add_handler(CommandHandler("reset", reset_command))

button_filter = filters.Regex(
    r"^(📊 Report|❓ Help|➕ Add Transaction|💰 Income|💸 Expense|🕐 Recent|🔄 Reset|❌ Cancel|✅ Yes, Reset)$"
)

app.add_handler(MessageHandler(button_filter, button_handler))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.add_error_handler(error_handler)


def main():
    app.run_polling()


if __name__ == "__main__":
    main()
