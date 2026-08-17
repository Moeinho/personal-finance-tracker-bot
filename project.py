import sqlite3
from datetime import datetime

VALID_ACCOUNTS = [
    "Meli",
    "Saderat",
    "Pasargad",
    "Melat",
    "Saman",
    "Mehr",
    "Keshavarzi",
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


class Tracker:
    def __init__(self, db_path="expenses.db"):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                category TEXT NOT NULL,
                account TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                user_id INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                title TEXT NOT NULL,
                account TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                user_id INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                state TEXT NOT NULL,
                action TEXT,
                amount INTEGER,
                title TEXT,
                category TEXT,
                account TEXT,
                description TEXT
            )
        """)

        self.connection.commit()

    def insert_expense(self, amount, category, account, description, timestamp, user_id):
        self.cursor.execute(
            """
            INSERT INTO expenses (
                amount,
                category,
                account,
                description,
                timestamp,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (amount, category, account, description, timestamp, user_id),
        )

        self.connection.commit()

    def insert_income(self, amount, title, account, description, timestamp, user_id):
        self.cursor.execute(
            """
            INSERT INTO incomes (
                amount,
                title,
                account,
                description,
                timestamp,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (amount, title, account, description, timestamp, user_id),
        )

        self.connection.commit()

    def fetch_expenses(self, user_id):
        self.cursor.execute(
            """
            SELECT
                amount,
                category,
                account,
                description,
                timestamp,
                user_id
            FROM expenses
            WHERE user_id = ?
        """,
            (user_id,),
        )

        return self.cursor.fetchall()

    def fetch_incomes(self, user_id):
        self.cursor.execute(
            """
            SELECT
                amount,
                title,
                account,
                description,
                timestamp,
                user_id
            FROM incomes
            WHERE user_id = ?
        """,
            (user_id,),
        )

        return self.cursor.fetchall()

    def get_total_expenses(self, user_id):
        self.cursor.execute(
            """
            SELECT SUM(amount)
            FROM expenses
            WHERE user_id = ?
        """,
            (user_id,),
        )

        result = self.cursor.fetchone()
        return result[0]

    def get_total_incomes(self, user_id):
        self.cursor.execute(
            """
            SELECT SUM(amount)
            FROM incomes
            WHERE user_id = ?
        """,
            (user_id,),
        )

        result = self.cursor.fetchone()
        return result[0]

    def get_expense_breakdown(self, user_id):
        self.cursor.execute(
            """
            SELECT category, SUM(amount)
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY category
        """,
            (user_id,),
        )

        return self.cursor.fetchall()

    def get_income_breakdown(self, user_id):
        self.cursor.execute(
            """
            SELECT title, SUM(amount)
            FROM incomes
            WHERE user_id = ?
            GROUP BY title
            ORDER BY title
        """,
            (user_id,),
        )

        return self.cursor.fetchall()

    # New methods for user_states table
    
    def create_user_state(self, user_id):
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO user_states (user_id, state)
            VALUES (?, ?)
            """,
            (user_id, "WAITING_FOR_ACTION")
        )

        self.connection.commit()


    def get_user_state(self, user_id):
        self.cursor.execute(
            """
            SELECT
                state,
                action,
                amount,
                title,
                category,
                account,
                description
            FROM user_states
            WHERE user_id = ?
            """,
            (user_id,)
        )

        result = self.cursor.fetchone()

        if result is None:
            return None

        return {
            "state": result[0],
            "action": result[1],
            "amount": result[2],
            "title": result[3],
            "category": result[4],
            "account": result[5],
            "description": result[6],
        }


    def update_user_state(self, user_id, data):
        self.cursor.execute(
            """
            UPDATE user_states
            SET
                state = ?,
                action = ?,
                amount = ?,
                title = ?,
                category = ?,
                account = ?,
                description = ?
            WHERE user_id = ?
            """,
            (
                data.get("state"),
                data.get("action"),
                data.get("amount"),
                data.get("title"),
                data.get("category"),
                data.get("account"),
                data.get("description"),
                user_id
            )
        )

        self.connection.commit()


    def delete_user_state(self, user_id):
        self.cursor.execute(
            """
            DELETE FROM user_states
            WHERE user_id = ?
            """,
            (user_id,)
        )

        self.connection.commit()



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



def conversation_flow(tracker, user_id, user_input, user_states):
    # format user input
    user_input = user_input.strip().lower()

    if user_id not in user_states:
        user_states[user_id] = {"state":"WAITING_FOR_ACTION"}
    # 1. action

    if user_states[user_id]["state"] == "WAITING_FOR_ACTION":
        action = user_input
        if action in ["income", "expense"]:
                user_states[user_id]["action"] = action
                user_states[user_id]["state"] = "WAITING_FOR_AMOUNT"
                return "Please enter the amount: "
                
        else:
            return "Invalid action. Please try again."
            

    # 2. amount
    elif user_states[user_id]["state"] == "WAITING_FOR_AMOUNT":
        try:
            amount = validate_amount(user_input)
            user_states[user_id]["amount"] = amount
            if user_states[user_id]["action"] == "income":
                user_states[user_id]["state"] = "WAITING_FOR_TITLE"
                return "Please enter your income title: "
            elif user_states[user_id]["action"] == "expense":
                user_states[user_id]["state"] = "WAITING_FOR_CATEGORY"
                return "Please enter your expense category: "
            
        except ValueError:
            return ("Invalid amount. Please try again.")

    # 3. title/category
    elif user_states[user_id]["state"] == "WAITING_FOR_TITLE":
        try:
            title = validate_title(user_input)
            user_states[user_id]["title"] = title
            user_states[user_id]["state"] = "WAITING_FOR_ACCOUNT"
            return "Please enter your account name: "
            
        except ValueError:
            return "Invalid title. Please try again."

    elif user_states[user_id]["state"] == "WAITING_FOR_CATEGORY":
        try:
            category = validate_category(user_input)
            user_states[user_id]["category"] = category
            user_states[user_id]["state"] = "WAITING_FOR_ACCOUNT"
            return "Please enter your account name: "

        except ValueError:
            return "Invalid category. Please try again."


    # 4. account
    elif user_states[user_id]["state"] == "WAITING_FOR_ACCOUNT":
        try:
            account = validate_account(user_input)
            user_states[user_id]["account"] = account
            user_states[user_id]["state"] = "WAITING_FOR_DESCRIPTION"
            return "Please enter your description: "
        except ValueError:
            return "Invalid account. Please try again."

    # 5. description
    elif user_states[user_id]["state"] == "WAITING_FOR_DESCRIPTION":
        description = user_input
        user_states[user_id]["description"] = description
        user_states[user_id]["state"] = "WAITING_FOR_SAVING"
        return "Description saved. Send /save to store transaction."


    # 6. save
    elif (
        user_states[user_id]["state"] == "WAITING_FOR_SAVING"
        and user_input =="/save"
    ):
        if user_states[user_id]["action"] == "income":
            final_dict = {
                "amount": user_states[user_id]["amount"],
                "title":user_states[user_id]["title"],
                "account": user_states[user_id]["account"],
                "description": user_states[user_id]["description"],
                "user_id": user_id,
                }
            save_income(final_dict, tracker)

        else:
            final_dict = {
                "amount": user_states[user_id]["amount"],
                "category":user_states[user_id]["category"],
                "account": user_states[user_id]["account"],
                "description": user_states[user_id]["description"],
                "user_id": user_id,
                }
            save_expense(final_dict, tracker)
        user_states[user_id] = {"state": "WAITING_FOR_ACTION"}
        return "Transaction saved successfully."




def main():
    tracker = Tracker()
    user_states = {}
    conversation_flow(tracker, 1234,"income", user_states)
    conversation_flow(tracker, 1234, "abc", user_states)
    conversation_flow(tracker, 1234, "2000", user_states)
    conversation_flow(tracker, 1234, "salary", user_states)
    conversation_flow(tracker, 1234, "saderat", user_states)
    conversation_flow(tracker, 1234, "monthly salary", user_states)
    conversation_flow(tracker, 1234, "/save", user_states)
    print(format_report(user_id=1234, tracker=tracker))

    # tracker = ExpenseTracker(":memory:")
    # user_states = {}

    # print(conversation_flow(tracker, 1234, "income", user_states))
    # print(user_states)

    # print(conversation_flow(tracker, 1234, "2000", user_states))
    # print(user_states)



if __name__ == "__main__":
    main()

