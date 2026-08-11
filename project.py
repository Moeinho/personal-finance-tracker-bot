import sqlite3


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
                timestamp TEXT NOT NULL,
                user_id INTEGER
                )
            """)

        self.connection.commit()


    def insert_expense(self, amount, category, card, timestamp, user_id):
        self.cursor.execute("""
            INSERT INTO expenses (amount, category, card, timestamp, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (amount, category, card, timestamp, user_id))
        self.connection.commit()


    def insert_incomes(self, amount, title, account, timestamp, user_id):
        self.cursor.execute("""
            INSERT INTO incomes (amount, title, account, timestamp, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (amount, title, account, timestamp, user_id))
        self.connection.commit()


    def fetch_expenses(self, user_id):
        self.cursor.execute("""
            SELECT amount, category, card, timestamp, user_id
            FROM expenses
            WHERE user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()


    def fetch_incomes(self, user_id):
        self.cursor.execute("""
            SELECT amount, title, account, timestamp, user_id
            FROM incomes
            WHERE user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()


def parse_user_input():
    ...

def save_expense():
    ...

def save_income():
    ...

def format_report():
    ...

def format_balace():
    ???
