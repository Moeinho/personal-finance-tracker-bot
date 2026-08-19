from tracker import Tracker
from datetime import datetime

VALID_ACCOUNTS = [
    "Meli",
    "Saderat",
    "Pasargad",
    "Melat",
    "Saman",
    "Mehr",
    "Keshavarzi",
    "Tejarat",
    "Resalat",
    "Shahr",
    "Dey",
    "Parsian",
]

VALID_CATEGORIES = [
    "Food",
    "Transport",
    "Housing",
    "Shopping",
    "Bills",
    "Health",
    "Education",
    "Entertainment",
    "Travel",
    "Personal",
    "Other",
]


# validation logic control:


def validate_amount(amount):
    amount = int(amount)
    if amount <= 0:
        raise ValueError
    return amount


def validate_account(account):

    normalized_account_words = account.strip().lower().split()

    for valid_account in VALID_ACCOUNTS:
        if valid_account.lower() in normalized_account_words:
            return valid_account

    raise ValueError


def validate_category(category):
    normalized_category = category.strip().lower()

    for valid_category in VALID_CATEGORIES:
        if normalized_category == valid_category.lower():
            return valid_category

    raise ValueError


def validate_title(title):
    title = title.strip().lower()

    if not title or len(title) > 100 or not any(char.isalpha() for char in title):
        raise ValueError

    return title


def save_income(dict_object, tracker):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    tracker.insert_income(
        dict_object["amount"],
        dict_object["title"],
        dict_object["account"],
        dict_object["description"],
        timestamp,
        dict_object["user_id"],
    )


def save_expense(dict_object, tracker):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    tracker.insert_expense(
        dict_object["amount"],
        dict_object["category"],
        dict_object["account"],
        dict_object["description"],
        timestamp,
        dict_object["user_id"],
    )


# Convert income rows from tuples to dictionaries
def income_to_dict(latest_incomes):
    return [
        {
            "type": "income",
            "amount": row[0],
            "name": row[1],
            "account": row[2],
            "description": row[3],
            "timestamp": row[4],
        }
        for row in latest_incomes
    ]


# Convert expense rows from tuples to dictionaries
def expense_to_dict(latest_expenses):
    return [
        {
            "type": "expense",
            "amount": row[0],
            "name": row[1],
            "account": row[2],
            "description": row[3],
            "timestamp": row[4],
        }
        for row in latest_expenses
    ]


def recent_transactions(user_id, tracker, limit):
    latest_incomes = tracker.get_latest_incomes(user_id, limit)
    latest_incomes_dicts = income_to_dict(latest_incomes)

    latest_expenses = tracker.get_latest_expenses(user_id, limit)
    latest_expenses_dicts = expense_to_dict(latest_expenses)

    # merging and sorting latest_transactions list
    latest_transactions = latest_incomes_dicts + latest_expenses_dicts
    # newest first
    latest_transactions = sorted(
        latest_transactions,
        key=lambda transaction: transaction["timestamp"],
        reverse=True,
    )
    last_limited_transactions = latest_transactions[0:limit]

    # Latest transactions
    recent = "🕐 LATEST TRANSACTIONS\n"
    recent += "━━━━━━━━━━━━━━━━\n\n"

    if len(last_limited_transactions) == 0:
        recent += "No transactions yet.\n"
        return recent

    for transaction in last_limited_transactions:
        if transaction["type"] == "expense":
            recent += f"💸 {transaction["name"]}\n"
        elif transaction["type"] == "income":
            recent += f"💰 {transaction["name"]}\n"
        recent += f"{transaction["amount"]:,} T\n"
        recent += f"🏦 {transaction["account"]}\n"
        recent += f"📝 {transaction["description"]}\n"
        recent += f"📅 {transaction["timestamp"]}\n\n"
    return recent


def format_report(user_id, tracker) -> str:
    total_expenses = tracker.get_total_expenses(user_id) or 0
    total_incomes = tracker.get_total_incomes(user_id) or 0
    balance = total_incomes - total_expenses
    expense_breakdown = tracker.get_expense_breakdown(user_id)
    income_breakdown = tracker.get_income_breakdown(user_id)

    # report format
    report = "📊 FINANCIAL REPORT\n"
    report += "━━━━━━━━━━━━━━━━\n\n"

    # Incomes
    report += "💰 INCOMES\n"

    if total_incomes != 0:
        for title, total in income_breakdown:
            report += f"{title.title()}: {total:,} T\n"
    report += f"\nTotal Incomes: {total_incomes:,} T\n\n"

    # Expenses
    report += "💸 EXPENSES\n"
    if total_expenses != 0:
        for category, total in expense_breakdown:
            report += f"{category}: {total:,} T\n"
    report += f"\nTotal Expenses: {total_expenses:,} T\n\n"

    # Balance
    report += "💵 BALANCE\n"
    report += f"{balance:,} T\n\n"

    if total_expenses == 0 and total_incomes == 0:
        report += f"\nNo transactions yet.\n"

    return report


# refactor method for save
def save_transaction(state, user_id, tracker):

    if state["action"] == "income":
        final_dict = {
            "amount": state["amount"],
            "title": state["title"],
            "account": state["account"],
            "description": state["description"],
            "user_id": user_id,
        }
        save_income(final_dict, tracker)

    elif state["action"] == "expense":
        final_dict = {
            "amount": state["amount"],
            "category": state["category"],
            "account": state["account"],
            "description": state["description"],
            "user_id": user_id,
        }
        save_expense(final_dict, tracker)


def conversation_flow(tracker, user_id, user_input):

    # format user input
    user_input = user_input.strip().lower()
    state = tracker.get_user_state(user_id)

    if state is None:
        tracker.create_user_state(user_id)
        state = tracker.get_user_state(user_id)

    # 1. action
    if state["state"] == "WAITING_FOR_ACTION":
        action = user_input
        if action in ["income", "expense"]:
            state["action"] = action
            if action == "income":
                state["state"] = "WAITING_FOR_TITLE"
                tracker.update_user_state(user_id, state)
                return "Please enter the income title: "
            elif action == "expense":
                state["state"] = "WAITING_FOR_CATEGORY"
                tracker.update_user_state(user_id, state)
                return "Please enter the expense category: "
        else:
            return "Invalid action. Please try again."

    # 2. title/category
    elif state["state"] == "WAITING_FOR_TITLE":
        try:
            title = validate_title(user_input)
            state["title"] = title
            state["state"] = "WAITING_FOR_AMOUNT"
            tracker.update_user_state(user_id, state)
            return "Please enter the amount in Tomans: "

        except ValueError:
            return "Invalid title. Please try again."

    elif state["state"] == "WAITING_FOR_CATEGORY":
        try:
            category = validate_category(user_input)
            state["category"] = category
            state["state"] = "WAITING_FOR_AMOUNT"
            tracker.update_user_state(user_id, state)
            return "Please enter the amount in Tomans: "

        except ValueError:
            return "Invalid category. Please try again."

    # 3. amount
    elif state["state"] == "WAITING_FOR_AMOUNT":
        try:
            amount = validate_amount(user_input)
            state["amount"] = amount
            state["state"] = "WAITING_FOR_ACCOUNT"
            tracker.update_user_state(user_id, state)
            return "Please enter your account name: "

        except ValueError:
            return "Invalid amount. Please try again."

    # 4. account
    elif state["state"] == "WAITING_FOR_ACCOUNT":
        try:
            account = validate_account(user_input)
            state["account"] = account
            state["state"] = "WAITING_FOR_DESCRIPTION"
            tracker.update_user_state(user_id, state)
            return "Please enter your description: "
        except ValueError:
            return "Invalid account. Please try again."

    # 5. description
    elif state["state"] == "WAITING_FOR_DESCRIPTION":
        description = user_input
        state["description"] = description

        # Saving Automatically
        save_transaction(state, user_id, tracker)
        tracker.delete_user_state(user_id)
        return "✅ Transaction saved successfully!"


def main():
    ...


if __name__ == "__main__":
    main()
