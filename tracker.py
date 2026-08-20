"""
tracker.py - SQLite database layer for the Personal Finance Tracker.
Handles all direct database operations (CRUD) for expenses, incomes, and conversation state.
"""

import sqlite3


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

    def insert_expense(
        self, amount, category, account, description, timestamp, user_id
    ):
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

    # User state management
    def create_user_state(self, user_id):
        # OR IGNORE prevents error if user_state already exists
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO user_states (user_id, state)
            VALUES (?, ?)
            """,
            (user_id, "WAITING_FOR_ACTION"),
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
            (user_id,),
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

    def update_user_state(self, user_id, state_data):
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
                state_data.get("state"),
                state_data.get("action"),
                state_data.get("amount"),
                state_data.get("title"),
                state_data.get("category"),
                state_data.get("account"),
                state_data.get("description"),
                user_id,
            ),
        )

        self.connection.commit()

    def delete_user_state(self, user_id):
        self.cursor.execute(
            """
            DELETE FROM user_states
            WHERE user_id = ?
            """,
            (user_id,),
        )

        self.connection.commit()

    def reset_user_state(self, user_id):
        self.delete_user_state(user_id)
        self.create_user_state(user_id)

    # Latest transactions
    def get_latest_expenses(self, user_id, limit=5):
        self.cursor.execute(
            """
            SELECT
                amount,
                category,
                account,
                description,
                timestamp
            FROM expenses
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )

        return self.cursor.fetchall()

    def get_latest_incomes(self, user_id, limit=5):
        self.cursor.execute(
            """
            SELECT
                amount,
                title,
                account,
                description,
                timestamp
            FROM incomes
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )

        return self.cursor.fetchall()

    # reset both tables
    def delete_user_transactions(self, user_id):
        self.cursor.execute(
            """
            DELETE FROM expenses
            WHERE user_id = ?
            """,
            (user_id,),
        )
        self.cursor.execute(
            """
            DELETE FROM incomes
            WHERE user_id = ?
            """,
            (user_id,),
        )
        self.connection.commit()
