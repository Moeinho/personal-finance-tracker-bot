from project import ExpenseTracker, format_report


def test_insert_expense():
    tracker = ExpenseTracker(":memory:")
    tracker.insert_expense(100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)

    assert tracker.fetch_expenses(1234) == [
        (100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    ]


def test_insert_income():
    tracker = ExpenseTracker(":memory:")
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )

    assert tracker.fetch_incomes(1234) == [
        (2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234)
    ]


def test_fetch_expenses():
    tracker = ExpenseTracker(":memory:")
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
    tracker = ExpenseTracker(":memory:")
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
    tracker = ExpenseTracker(":memory:")
    assert tracker.get_total_expenses(1234) is None
    tracker.insert_expense(100, "Food", "Visa", "test", "2026-08-13 19:00", 1234)
    assert tracker.get_total_expenses(1234) == 100

    tracker.insert_expense(160, "Book", "PeyPal", "test", "2026-08-13 19:26", 1234)
    assert tracker.get_total_expenses(1234) == 260
    assert tracker.get_total_expenses(7524) is None


def test_get_total_incomes():
    tracker = ExpenseTracker(":memory:")
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
    tracker = ExpenseTracker(":memory:")
    tracker.insert_expense(100, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    tracker.insert_expense(50, "Food", "Master Card", "test", "2026-08-13 19:57", 1234)
    tracker.insert_expense(
        200, "Book", "PeyPal", "Harry Potter Book", "2026-08-13 19:37", 1234
    )
    tracker.insert_expense(
        500, "Food", "Visa", "Other user's expense", "2026-08-13 20:00", 9999
    )
    assert tracker.get_expense_breakdown(1234) == [("Book", 200), ("Food", 150)]


def test_get_income_breakdown():
    tracker = ExpenseTracker(":memory:")

    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )

    tracker.insert_income(
        1200, "Loan", "Store", "Mr Sarafraz", "2026-08-13 10:30", 1234
    )

    tracker.insert_income(400, "Salary", "Bank Meli", "Bonus", "2026-08-13 11:00", 1234)

    assert tracker.get_income_breakdown(1234) == [("Loan", 1200), ("Salary", 2400)]


# test format_roport
def test_format_report_empty():
    tracker = ExpenseTracker(":memory:")
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 0" in report
    assert "Total Expenses: 0" in report
    assert "Balance: 0" in report
    assert "No transactions yet." in report


def test_format_report_income_only():
    tracker = ExpenseTracker(":memory:")
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 2000" in report
    assert "Total Expenses: 0" in report
    assert "Balance: 2000" in report


def test_format_report_expense_only():
    tracker = ExpenseTracker(":memory:")
    tracker.insert_expense(500, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 0" in report
    assert "Total Expenses: 500" in report
    assert "Balance: -500" in report


def test_format_report_income_and_expense():
    tracker = ExpenseTracker(":memory:")
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )
    tracker.insert_expense(500, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 2000" in report
    assert "Total Expenses: 500" in report
    assert "Balance: 1500" in report


def test_format_report_negative_balance():
    tracker = ExpenseTracker(":memory:")
    tracker.insert_income(500, "Salary", "Bank Meli", "Bonus", "2026-08-13 11:00", 1234)
    tracker.insert_expense(700, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    tracker.insert_expense(
        100, "Book", "PeyPal", "Harry Potter Book", "2026-08-13 19:37", 1234
    )
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 500" in report
    assert "Book: 100" in report
    assert "Food: 700" in report
    assert "Total Expenses: 800" in report
    assert "Balance: -300" in report


def test_format_report_breakdown():
    tracker = ExpenseTracker(":memory:")
    tracker.insert_income(500, "Salary", "Bank Meli", "Bonus", "2026-08-13 11:00", 1234)
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )
    tracker.insert_expense(500, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    tracker.insert_expense(
        100, "Book", "PeyPal", "Harry Potter Book", "2026-08-13 19:37", 1234
    )
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Salary: 2500" in report
    assert "Total Income: 2500" in report
    assert "Book: 100" in report
    assert "Food: 500" in report
    assert "Total Expenses: 600" in report
    assert "Balance: 1900" in report
