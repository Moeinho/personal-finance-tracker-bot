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

    def insert_expense(
        self,
        amount,
        category,
        card,
        description,
        timestamp,
        user_id
    ):
        self.cursor.execute("""
            INSERT INTO expenses (
                amount,
                category,
                card,
                description,
                timestamp,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            amount,
            category,
            card,
            description,
            timestamp,
            user_id
        ))

        self.connection.commit()

    def insert_income(
        self,
        amount,
        title,
        account,
        description,
        timestamp,
        user_id
    ):
        self.cursor.execute("""
            INSERT INTO incomes (
                amount,
                title,
                account,
                description,
                timestamp,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            amount,
            title,
            account,
            description,
            timestamp,
            user_id
        ))

        self.connection.commit()

    def fetch_expenses(self, user_id):
        self.cursor.execute("""
            SELECT
                amount,
                category,
                card,
                description,
                timestamp,
                user_id
            FROM expenses
            WHERE user_id = ?
        """, (user_id,))

        return self.cursor.fetchall()

    def fetch_incomes(self, user_id):
        self.cursor.execute("""
            SELECT
                amount,
                title,
                account,
                description,
                timestamp,
                user_id
            FROM incomes
            WHERE user_id = ?
        """, (user_id,))

        return self.cursor.fetchall()


def save_income(dict_object, tracker):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    tracker.insert_income(
        dict_object["amount"],
        dict_object["title"],
        dict_object["account"],
        dict_object["description"],
        timestamp,
        dict_object["user_id"]
    )


def save_expense(dict_object, tracker):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    tracker.insert_expense(
        dict_object["amount"],
        dict_object["category"],
        dict_object["card"],
        dict_object["description"],
        timestamp,
        dict_object["user_id"]
    )


# def format_report():
#     ...


# def format_balance():
#     ...


# def main():
#     ...


if __name__ == "__main__":
    main()