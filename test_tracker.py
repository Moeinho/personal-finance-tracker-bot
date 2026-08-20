"""
test_tracker.py - Tests for the Tracker database layer.
Covers database operations, user state management, transaction retrieval, and deletion.
"""

from tracker import Tracker


def test_insert_expense():
    tracker = Tracker(":memory:")
    tracker.insert_expense(100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)

    assert tracker.fetch_expenses(1234) == [
        (100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    ]


def test_insert_income():
    tracker = Tracker(":memory:")
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )

    assert tracker.fetch_incomes(1234) == [
        (2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234)
    ]


def test_fetch_expenses():
    tracker = Tracker(":memory:")
    tracker.insert_expense(100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    tracker.insert_expense(
        200, "Book", "Bank", "Harry Potter", "2026-08-13 20:00", 1234
    )
    tracker.insert_expense(500, "Food", "Visa", "Other user", "2026-08-13 21:00", 9999)

    assert tracker.fetch_expenses(1234) == [
        (100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234),
        (200, "Book", "Bank", "Harry Potter", "2026-08-13 20:00", 1234),
    ]
    assert tracker.fetch_expenses(9999) == [
        (500, "Food", "Visa", "Other user", "2026-08-13 21:00", 9999)
    ]


def test_fetch_incomes():
    tracker = Tracker(":memory:")
    tracker.insert_income(2000, "Salary", "Bank", "Salary", "2026-08-13 10:00", 1234)
    tracker.insert_income(500, "Bonus", "Bank", "Bonus", "2026-08-13 11:00", 1234)
    tracker.insert_income(
        700, "Bonus", "Bank Meli", "Bonus Work", "2025-08-13 11:00", 1234
    )
    tracker.insert_income(
        10000, "Salary", "Bank", "Other user", "2026-08-13 12:00", 9999
    )

    assert tracker.fetch_incomes(1234) == [
        (2000, "Salary", "Bank", "Salary", "2026-08-13 10:00", 1234),
        (500, "Bonus", "Bank", "Bonus", "2026-08-13 11:00", 1234),
        (700, "Bonus", "Bank Meli", "Bonus Work", "2025-08-13 11:00", 1234),
    ]
    assert tracker.fetch_incomes(9999) == [
        (10000, "Salary", "Bank", "Other user", "2026-08-13 12:00", 9999)
    ]


def test_get_total_expenses():
    tracker = Tracker(":memory:")
    assert tracker.get_total_expenses(1234) is None
    tracker.insert_expense(100, "Food", "Visa", "test", "2026-08-13 19:00", 1234)
    assert tracker.get_total_expenses(1234) == 100

    tracker.insert_expense(160, "Book", "PeyPal", "test", "2026-08-13 19:26", 1234)
    assert tracker.get_total_expenses(1234) == 260
    assert tracker.get_total_expenses(7524) is None


def test_get_total_incomes():
    tracker = Tracker(":memory:")
    assert tracker.get_total_incomes(1234) is None
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )
    assert tracker.get_total_incomes(1234) == 2000
    tracker.insert_income(
        1200, "Loan", "Store", "Mr Sarafraz", "2026-08-13 10:00", 1234
    )
    tracker.insert_income(
        400, "Rent", "Bank Meli", "Monthly Rent", "2026-08-13 10:00", 1234
    )
    assert tracker.get_total_incomes(1234) == 3600
    assert tracker.get_total_incomes(4235) is None


def test_get_expense_breakdown():
    tracker = Tracker(":memory:")
    tracker.insert_expense(100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    tracker.insert_expense(
        50, "Food", "Master account", "test", "2026-08-13 19:57", 1234
    )
    tracker.insert_expense(
        200, "Book", "PeyPal", "Harry Potter Book", "2026-08-13 19:37", 1234
    )
    tracker.insert_expense(
        500, "Food", "Visa", "Other user's expense", "2026-08-13 20:00", 9999
    )
    assert tracker.get_expense_breakdown(1234) == [("Book", 200), ("Food", 150)]


def test_get_income_breakdown():
    tracker = Tracker(":memory:")

    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )

    tracker.insert_income(
        1200, "Loan", "Store", "Mr Sarafraz", "2026-08-13 10:30", 1234
    )

    tracker.insert_income(400, "Salary", "Bank Meli", "Bonus", "2026-08-13 11:00", 1234)

    assert tracker.get_income_breakdown(1234) == [("Loan", 1200), ("Salary", 2400)]


# test tracker new methods


def test_create_user_state():
    tracker = Tracker(":memory:")
    tracker.create_user_state(1234)
    state = tracker.get_user_state(1234)
    assert state["state"] == "WAITING_FOR_ACTION"


def test_update_user_state():
    tracker = Tracker(":memory:")
    tracker.create_user_state(1234)

    state = tracker.get_user_state(1234)
    state["state"] = "WAITING_FOR_AMOUNT"
    state["amount"] = 500

    tracker.update_user_state(1234, state)
    new_state = tracker.get_user_state(1234)

    assert new_state["state"] == "WAITING_FOR_AMOUNT"
    assert new_state["amount"] == 500


def test_delete_user_state():
    tracker = Tracker(":memory:")
    tracker.create_user_state(1234)
    tracker.delete_user_state(1234)

    assert tracker.get_user_state(1234) is None


def test_reset_user_state():
    tracker = Tracker(":memory:")
    tracker.create_user_state(1234)
    state = tracker.get_user_state(1234)
    state["state"] = "WAITING_FOR_AMOUNT"
    state["amount"] = 500

    tracker.update_user_state(1234, state)
    tracker.reset_user_state(1234)
    new_state = tracker.get_user_state(1234)

    assert new_state["state"] == "WAITING_FOR_ACTION"
    assert new_state["amount"] is None


def test_create_user_state_duplicate():
    tracker = Tracker(":memory:")
    tracker.create_user_state(1234)
    tracker.create_user_state(1234)
    state = tracker.get_user_state(1234)

    assert state["state"] == "WAITING_FOR_ACTION"


# new tests for new methods for getting last 5 transactions


def test_get_latest_incomes():
    tracker = Tracker(":memory:")

    tracker.insert_income(2000, "Salary", "Bank", "Salary", "2026-08-13 10:00", 1234)
    tracker.insert_income(500, "Bonus", "Bank", "Bonus", "2026-08-13 11:00", 1234)
    tracker.insert_income(700, "Salary", "Bank Meli", "test", "2026-08-15 11:00", 1234)
    tracker.insert_income(
        10000, "Salary", "Bank", "Other user", "2026-08-16 12:00", 9999
    )
    tracker.insert_income(400, "Salary", "Bank Meli", "test", "2026-08-17 11:00", 1234)
    tracker.insert_income(800, "Salary", "Bank Meli", "test", "2026-08-18 11:00", 1234)
    tracker.insert_income(2200, "Bonus", "Bank Meli", "test", "2026-08-18 13:00", 1234)
    tracker.insert_income(100, "Bonus", "Bank Meli", "test", "2026-08-18 17:00", 1234)

    assert tracker.get_latest_incomes(1234, 5) == [
        (100, "Bonus", "Bank Meli", "test", "2026-08-18 17:00"),
        (2200, "Bonus", "Bank Meli", "test", "2026-08-18 13:00"),
        (800, "Salary", "Bank Meli", "test", "2026-08-18 11:00"),
        (400, "Salary", "Bank Meli", "test", "2026-08-17 11:00"),
        (700, "Salary", "Bank Meli", "test", "2026-08-15 11:00"),
    ]


def test_get_latest_expenses():
    tracker = Tracker(":memory:")

    tracker.insert_expense(200, "Food", "Bank", "Lunch", "2026-08-13 10:00", 1234)
    tracker.insert_expense(500, "Transport", "Bank", "Taxi", "2026-08-13 11:00", 1234)
    tracker.insert_expense(
        700, "Shopping", "Bank Meli", "Clothes", "2026-08-15 11:00", 1234
    )
    tracker.insert_expense(
        10000, "Housing", "Bank", "Other user", "2026-08-16 12:00", 9999
    )
    tracker.insert_expense(400, "Food", "Bank Meli", "Dinner", "2026-08-17 11:00", 1234)
    tracker.insert_expense(
        800, "Bills", "Bank Meli", "Internet", "2026-08-18 11:00", 1234
    )
    tracker.insert_expense(
        2200, "Travel", "Bank Meli", "Hotel", "2026-08-18 13:00", 1234
    )
    tracker.insert_expense(100, "Food", "Bank Meli", "Coffee", "2026-08-18 17:00", 1234)

    assert tracker.get_latest_expenses(1234, 5) == [
        (100, "Food", "Bank Meli", "Coffee", "2026-08-18 17:00"),
        (2200, "Travel", "Bank Meli", "Hotel", "2026-08-18 13:00"),
        (800, "Bills", "Bank Meli", "Internet", "2026-08-18 11:00"),
        (400, "Food", "Bank Meli", "Dinner", "2026-08-17 11:00"),
        (700, "Shopping", "Bank Meli", "Clothes", "2026-08-15 11:00"),
    ]


def test_delete_user_transactions():
    tracker = Tracker(":memory:")

    tracker.insert_expense(100, "Food", "Bank", "Lunch", "2026-08-18 10:00", 1234)
    tracker.insert_income(
        1000, "Salary", "Bank", "Monthly salary", "2026-08-18 11:00", 1234
    )

    tracker.delete_user_transactions(1234)

    assert tracker.fetch_expenses(1234) == []
    assert tracker.fetch_incomes(1234) == []


def test_delete_user_transactions_only_for_user():
    tracker = Tracker(":memory:")

    tracker.insert_expense(100, "Food", "Bank", "User 1", "2026-08-18 10:00", 1234)
    tracker.insert_expense(200, "Food", "Bank", "User 2", "2026-08-18 11:00", 9999)

    tracker.insert_income(1000, "Salary", "Bank", "User 1", "2026-08-18 12:00", 1234)
    tracker.insert_income(2000, "Salary", "Bank", "User 2", "2026-08-18 13:00", 9999)

    tracker.delete_user_transactions(1234)

    assert tracker.fetch_expenses(1234) == []
    assert tracker.fetch_incomes(1234) == []

    assert tracker.fetch_expenses(9999) == [
        (200, "Food", "Bank", "User 2", "2026-08-18 11:00", 9999)
    ]
    assert tracker.fetch_incomes(9999) == [
        (2000, "Salary", "Bank", "User 2", "2026-08-18 13:00", 9999)
    ]
