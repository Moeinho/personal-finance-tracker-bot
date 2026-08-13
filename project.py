import sqlite3
from datetime import datetime


class ExpenseTracker:
    def __init__(self, db_path="expenses.db"):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                card TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                user_id INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                title TEXT NOT NULL,
                account TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                user_id INTEGER
            )
        """)

        self.connection.commit()

    def insert_expense(self, amount, category, card, description, timestamp, user_id):
        self.cursor.execute(
            """
            INSERT INTO expenses (
                amount,
                category,
                card,
                description,
                timestamp,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (amount, category, card, description, timestamp, user_id),
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
                card,
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
        dict_object["card"],
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
            report += f"{title}: {total}\n"
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

    # def create_listOfDicts(data_tuples):
    #     data_list = []
    #     if len(data_tuples) == 0:
    #         return 0
    #     else:
    #         for data_tuple in data_tuples:
    #             data_list.append({data_tuple[0]: data_tuple[1]})
    #     return data_list


# def format_balance():
#     ...


# def main():
#     ...


# if __name__ == "__main__":
#     main()
