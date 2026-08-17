from tracker import Tracker
from project import format_report, save_income, save_expense
from project import validate_amount, validate_account, validate_category, validate_title
from project import conversation_flow
import pytest


# test format_roport
def test_format_report_empty():
    tracker = Tracker(":memory:")
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 0" in report
    assert "Total Expenses: 0" in report
    assert "Balance: 0" in report
    assert "No transactions yet." in report


def test_format_report_income_only():
    tracker = Tracker(":memory:")
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 2000" in report
    assert "Total Expenses: 0" in report
    assert "Balance: 2000" in report


def test_format_report_expense_only():
    tracker = Tracker(":memory:")
    tracker.insert_expense(500, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    report = format_report(tracker=tracker, user_id=1234)

    assert "Financial Report" in report
    assert "Total Income: 0" in report
    assert "Total Expenses: 500" in report
    assert "Balance: -500" in report


def test_format_report_income_and_expense():
    tracker = Tracker(":memory:")
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
    tracker = Tracker(":memory:")
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
    tracker = Tracker(":memory:")
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


def test_save_income():
    tracker = Tracker(":memory:")
    income = {
        "amount": 2000,
        "title": "Salary",
        "account": "Bank",
        "description": "Monthly salary",
        "user_id": 1234,
    }
    save_income(income, tracker)
    incomes = tracker.fetch_incomes(1234)

    assert len(incomes) == 1
    assert incomes[0][0] == 2000
    assert incomes[0][1] == "Salary"
    assert incomes[0][2] == "Bank"
    assert incomes[0][3] == "Monthly salary"
    assert incomes[0][5] == 1234


def test_save_expense():
    tracker = Tracker(":memory:")
    expense = {
        "amount": 200,
        "category": "Food",
        "account": "Visa",
        "description": "Dinner",
        "user_id": 1234,
    }

    save_expense(expense, tracker)
    expenses = tracker.fetch_expenses(1234)

    assert len(expenses) == 1
    assert expenses[0][0] == 200
    assert expenses[0][1] == "Food"
    assert expenses[0][2] == "Visa"
    assert expenses[0][3] == "Dinner"
    assert expenses[0][5] == 1234


def test_validate_amount():
    assert validate_amount("5000") == 5000
    with pytest.raises(ValueError):
        validate_amount("-500")
    with pytest.raises(ValueError):
        validate_amount("abc")
    with pytest.raises(ValueError):
        validate_amount("0")
    with pytest.raises(ValueError):
        validate_amount("10.7")


def test_validate_account():
    assert validate_account("saderat") == "Saderat"
    assert validate_account("   saderat") == "Saderat"
    assert validate_account("saderat   ") == "Saderat"
    assert validate_account("pasargad") == "Pasargad"
    with pytest.raises(ValueError):
        validate_account("  ")
    with pytest.raises(ValueError):
        validate_account("")


def test_validate_category():
    assert validate_category("food") == "Food"
    assert validate_category("   FOOD") == "Food"
    assert validate_category("Food") == "Food"
    with pytest.raises(ValueError):
        validate_category("Fast Food")
    with pytest.raises(ValueError):
        validate_category("rice")
    with pytest.raises(ValueError):
        validate_category("")


def test_validate_title():
    assert validate_title("Salary") == "salary"
    assert validate_title("   Salary") == "salary"
    assert validate_title("freelance") == "freelance"
    assert validate_title("SALARY") == "salary"
    with pytest.raises(ValueError):
        validate_title("")
    with pytest.raises(ValueError):
        validate_title("  ")


def test_conversation_flow_action():
    tracker = Tracker(":memory:")
    conversation_flow(tracker, 1234, "income")
    state = tracker.get_user_state(1234)

    assert state["state"] == "WAITING_FOR_AMOUNT"
    assert state["action"] == "income"



def test_conversation_flow_amount():
    tracker = Tracker(":memory:")

    conversation_flow(tracker, 1234, "income")
    conversation_flow(tracker, 1234, "1300")

    state = tracker.get_user_state(1234)

    assert state["state"] == "WAITING_FOR_TITLE"
    assert state["amount"] == 1300


def test_conversation_flow_invalid_amount():
    tracker = Tracker(":memory:")
    conversation_flow(tracker, 1234, "income")
    conversation_flow(tracker, 1234, "abc",)
    state = tracker.get_user_state(1234)
    
    assert state["state"] == "WAITING_FOR_AMOUNT"
    assert state["amount"] is None


def test_conversation_flow_save_income():
    tracker = Tracker(":memory:")
    conversation_flow(tracker, 1234, "income")
    conversation_flow(tracker, 1234, "1300")
    conversation_flow(tracker, 1234, "salary")
    conversation_flow(tracker, 1234, "meli")
    conversation_flow(tracker, 1234, "monthly salary")

    incomes = tracker.fetch_incomes(1234)

    assert len(incomes) == 1
    assert incomes[0][0] == 1300
    assert incomes[0][1] == "salary"
    assert incomes[0][2] == "Meli"
    assert incomes[0][3] == "monthly salary"
    assert incomes[0][5] == 1234
    assert tracker.get_user_state(1234) is None
    
