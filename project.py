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
    "Parsian"
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

    if not title:
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


def format_report(user_id, tracker) -> str:
    total_expenses = tracker.get_total_expenses(user_id) or 0
    total_incomes = tracker.get_total_incomes(user_id) or 0
    balance = total_incomes - total_expenses
    expense_breakdown = tracker.get_expense_breakdown(user_id)
    income_breakdown = tracker.get_income_breakdown(user_id)

    report = "Financial Report\n----------------\nIncomes:\n"
    if total_incomes != 0:
        for title, total in income_breakdown:
            report += f"{title.title()}: {total}\n"
    report += f"Total Income: {total_incomes}\n\n"

    report += "Expenses:\n"
    if total_expenses != 0:
        for category, total in expense_breakdown:
            report += f"{category}: {total}\n"
    report += f"Total Expenses: {total_expenses}\n\n"

    report += f"Balance: {balance}\n"
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
                state["state"] = "WAITING_FOR_AMOUNT"
                tracker.update_user_state(user_id, state)
                return "Please enter the amount: "
                
        else:
            return "Invalid action. Please try again."
            

    # 2. amount
    elif state["state"] == "WAITING_FOR_AMOUNT":
        try:
            amount = validate_amount(user_input)
            state["amount"] = amount
            if state["action"] == "income":
                state["state"] = "WAITING_FOR_TITLE"
                tracker.update_user_state(user_id, state)
                return "Please enter your income title: "
            elif state["action"] == "expense":
                state["state"] = "WAITING_FOR_CATEGORY"
                tracker.update_user_state(user_id, state)
                return "Please enter your expense category: "
            
        except ValueError:
            return ("Invalid amount. Please try again.")

    # 3. title/category
    elif state["state"] == "WAITING_FOR_TITLE":
        try:
            title = validate_title(user_input)
            state["title"] = title
            state["state"] = "WAITING_FOR_ACCOUNT"
            tracker.update_user_state(user_id, state)
            return "Please enter your account name: "
            
        except ValueError:
            return "Invalid title. Please try again."

    elif state["state"] == "WAITING_FOR_CATEGORY":
        try:
            category = validate_category(user_input)
            state["category"] = category
            state["state"] = "WAITING_FOR_ACCOUNT"
            tracker.update_user_state(user_id, state)
            return "Please enter your account name: "

        except ValueError:
            return "Invalid category. Please try again."


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
        return "Transaction saved successfully."





def main():
    tracker = Tracker()
    conversation_flow(tracker, 1234,"income")
    conversation_flow(tracker, 1234, "abc")
    conversation_flow(tracker, 1234, "600")
    conversation_flow(tracker, 1234, "first salary")
    conversation_flow(tracker, 1234, "saderat")
    conversation_flow(tracker, 1234, "monthly salary")
    conversation_flow(tracker, 1234, "/save")
    print(format_report(user_id=1234, tracker=tracker))

    # tracker = ExpenseTracker(":memory:")

    # print(conversation_flow(tracker, 1234, "income")
    # print(user_states)

    # print(conversation_flow(tracker, 1234, "2000")
    # print(user_states)



if __name__ == "__main__":
    main()

