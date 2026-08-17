from tracker import Tracker

# test expenses and incomes tables

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