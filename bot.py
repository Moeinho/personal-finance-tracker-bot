import os
from dotenv import load_dotenv
from tracker import Tracker
from project import conversation_flow, format_report
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import BotCommand

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

help_txt = """
📌 Personal Finance Tracker Bot

Commands:

/add
➕ Add a new income or expense transaction

/report
📊 Show your financial report

/cancel
❌ Cancel current transaction

/help
ℹ️ Show available commands


How to use:

1. Press /add
2. Choose Income or Expense
3. Follow the steps
4. Your transaction will be saved automatically
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


async def post_init(application):
    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("add", "Add transaction"),
        BotCommand("report", "Show financial report"),
        BotCommand("cancel", "Cancel transaction"),
        BotCommand("help", "Show help"),
    ]
    await application.bot.set_my_commands(commands)


app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()


async def start_command(update, context):
    await update.message.reply_text(
        welcome_txt,
        reply_markup=ReplyKeyboardRemove()
    )


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
    await update.message.reply_text(report, reply_markup=ReplyKeyboardRemove())


async def cancel_command(update, context):
    user_id = update.message.from_user.id
    state = tracker.get_user_state(user_id)

    if state is None or state["state"] == "WAITING_FOR_ACTION":
        await update.message.reply_text(
            "There is no active transaction to cancel."
        )
        return

    tracker.delete_user_state(user_id)
    await update.message.reply_text(
        "Transaction canceled.",
        reply_markup=ReplyKeyboardRemove()
    )


async def help_command(update, context):
    await update.message.reply_text(help_txt)


async def error_handler(update, context):
    print(f"Exception: {context.error}")

    if update and update.message:
        await update.message.reply_text("Something went wrong. Please try again.")


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

    await update.message.reply_text(response, reply_markup=keyboard)



app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("add", add_command))
app.add_handler(CommandHandler("report", report_command))
app.add_handler(CommandHandler("cancel", cancel_command))
app.add_handler(CommandHandler("help", help_command))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.add_error_handler(error_handler)


def main():
    app.run_polling()


if __name__ == "__main__":
    main()
