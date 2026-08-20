"""
test_project.py - Tests for the Personal Finance Tracker's core logic.
Covers validation, transaction processing, reporting, recent transactions, and conversation flow.
"""

from tracker import Tracker
from project import recent_transactions, expense_to_dict, income_to_dict, format_report
from project import save_income, save_expense
from project import (
    validate_amount,
    validate_account,
    validate_description,
    validate_category,
    validate_title,
)
from project import conversation_flow, save_transaction
import pytest


def test_format_report_empty():
    tracker = Tracker(":memory:")
    report = format_report(tracker=tracker, user_id=1234)

    assert "📊 FINANCIAL REPORT\n" in report
    assert "💰 INCOMES\n" in report
    assert "\nTotal Incomes: 0 T\n\n" in report
    assert "💸 EXPENSES\n" in report
    assert "\nTotal Expenses: 0 T\n\n" in report
    assert "💵 BALANCE\n" in report
    assert "0 T\n\n" in report
    assert "No transactions yet." in report


def test_format_report_income_only():
    tracker = Tracker(":memory:")
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )
    report = format_report(tracker=tracker, user_id=1234)

    assert "📊 FINANCIAL REPORT\n" in report
    assert "💰 INCOMES\n" in report
    assert "\nTotal Incomes: 2,000 T\n\n" in report
    assert "💸 EXPENSES\n" in report
    assert "\nTotal Expenses: 0 T\n\n" in report
    assert "💵 BALANCE\n" in report
    assert "2,000 T\n\n" in report
    assert "No transactions yet." not in report


def test_format_report_expense_only():
    tracker = Tracker(":memory:")
    tracker.insert_expense(500, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    report = format_report(tracker=tracker, user_id=1234)

    assert "📊 FINANCIAL REPORT\n" in report
    assert "💰 INCOMES\n" in report
    assert "\nTotal Incomes: 0 T\n\n" in report
    assert "💸 EXPENSES\n" in report
    assert "\nTotal Expenses: 500 T\n\n" in report
    assert "💵 BALANCE\n" in report
    assert "-500 T\n\n" in report
    assert "No transactions yet." not in report


def test_format_report_income_and_expense():
    tracker = Tracker(":memory:")
    tracker.insert_income(
        2000, "Salary", "Bank", "Monthly salary", "2026-08-13 10:00", 1234
    )
    tracker.insert_expense(500, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    report = format_report(tracker=tracker, user_id=1234)

    assert "📊 FINANCIAL REPORT\n" in report
    assert "💰 INCOMES\n" in report
    assert "\nTotal Incomes: 2,000 T\n\n" in report
    assert "💸 EXPENSES\n" in report
    assert "\nTotal Expenses: 500 T\n\n" in report
    assert "💵 BALANCE\n" in report
    assert "1,500 T\n\n" in report
    assert "No transactions yet." not in report


def test_format_report_negative_balance():
    tracker = Tracker(":memory:")
    tracker.insert_income(500, "Salary", "Bank Meli", "Bonus", "2026-08-13 11:00", 1234)
    tracker.insert_expense(700, "Food", "Visa", "Dinner", "2026-08-13 19:00", 1234)
    tracker.insert_expense(
        100, "Book", "PeyPal", "Harry Potter Book", "2026-08-13 19:37", 1234
    )
    report = format_report(tracker=tracker, user_id=1234)

    assert "📊 FINANCIAL REPORT\n" in report
    assert "💰 INCOMES\n" in report
    assert "\nTotal Incomes: 500 T\n\n" in report
    assert "💸 EXPENSES\n" in report
    assert "Book: 100 T" in report
    assert "Food: 700 T" in report
    assert "\nTotal Expenses: 800 T\n\n" in report
    assert "💵 BALANCE\n" in report
    assert "-300 T\n\n" in report
    assert "No transactions yet." not in report


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

    assert "📊 FINANCIAL REPORT\n" in report
    assert "💰 INCOMES\n" in report
    assert "Salary: 2,500 T" in report
    assert "\nTotal Incomes: 2,500 T\n\n" in report
    assert "💸 EXPENSES\n" in report
    assert "Book: 100 T" in report
    assert "Food: 500 T" in report
    assert "\nTotal Expenses: 600 T\n\n" in report
    assert "💵 BALANCE\n" in report
    assert "1,900 T\n\n" in report
    assert "No transactions yet." not in report


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
    assert validate_account("dey") == "Dey"
    assert validate_account(" Dey ") == "Dey"

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
    assert validate_title("حقوق") == "حقوق"
    assert validate_title("123 salary") == "123 salary"
    with pytest.raises(ValueError):
        validate_title("")
    with pytest.raises(ValueError):
        validate_title("  ")
    with pytest.raises(ValueError):
        validate_title("123456")
    with pytest.raises(ValueError):
        validate_title("!!!")
    with pytest.raises(ValueError):
        validate_title("#$%")


def test_validate_description():
    long_txt = """
Lorem ipsum dolor sit amet,
consectetuer adipiscing elit.
Aenean commodo ligula eget dolor.
Aenean massa. Cum sociis natoque
penatibus et magnis dis parturient montes,
nascetur ridiculus mus. Donec quam felis,
ultricies nec, pellentesque eu, pretium quis, sem.
Nulla consequat massa quis enim.
Donec pede justo, fringilla vel,
aliquet nec, vulputate eget, arcu. In enim justo,
"""
    assert validate_description("test") == "test"
    assert validate_description("test    Salary") == "test    Salary"
    assert validate_description("freelance     ") == "freelance"
    assert validate_description("حقوق") == "حقوق"
    assert validate_description("123#$%salary") == "123#$%salary"
    with pytest.raises(ValueError):
        validate_description("")
    with pytest.raises(ValueError):
        validate_description("  ")
    with pytest.raises(ValueError):
        validate_description(long_txt)


def test_conversation_flow_action():
    tracker = Tracker(":memory:")
    conversation_flow(tracker, 1234, "income")
    state = tracker.get_user_state(1234)

    assert state["state"] == "WAITING_FOR_TITLE"
    assert state["action"] == "income"


def test_conversation_flow_amount():
    tracker = Tracker(":memory:")

    conversation_flow(tracker, 1234, "income")
    conversation_flow(tracker, 1234, "salary")
    conversation_flow(tracker, 1234, "1300")

    state = tracker.get_user_state(1234)

    assert state["state"] == "WAITING_FOR_ACCOUNT"
    assert state["title"] == "salary"
    assert state["amount"] == 1300


def test_conversation_flow_invalid_amount():
    tracker = Tracker(":memory:")
    conversation_flow(tracker, 1234, "income")
    conversation_flow(tracker, 1234, "salary")
    conversation_flow(
        tracker,
        1234,
        "abc",
    )
    state = tracker.get_user_state(1234)

    assert state["state"] == "WAITING_FOR_AMOUNT"
    assert state["amount"] is None


def test_conversation_flow_save_income():
    tracker = Tracker(":memory:")
    conversation_flow(tracker, 1234, "income")
    conversation_flow(tracker, 1234, "salary")
    conversation_flow(tracker, 1234, "1300")
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


def test_conversation_flow_save_expense():
    tracker = Tracker(":memory:")
    conversation_flow(tracker, 1234, "expense")
    conversation_flow(tracker, 1234, "food")
    conversation_flow(tracker, 1234, "1000")
    conversation_flow(tracker, 1234, "dey")
    conversation_flow(tracker, 1234, "test food")

    incomes = tracker.fetch_expenses(1234)

    assert len(incomes) == 1
    assert incomes[0][0] == 1000
    assert incomes[0][1] == "Food"
    assert incomes[0][2] == "Dey"
    assert incomes[0][3] == "test food"
    assert incomes[0][5] == 1234
    assert tracker.get_user_state(1234) is None


# test recent_transactions


def test_recent_transactions_no_transactions():
    tracker = Tracker(":memory:")
    recent = recent_transactions(1234, tracker, 5)
    assert "🕐 LATEST TRANSACTIONS" in recent
    assert "No transactions yet." in recent


def test_recent_transactions():
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

    tracker.insert_income(2000, "Salary", "Bank", "Salary", "2026-08-13 10:30", 1234)
    tracker.insert_income(500, "Bonus", "Bank", "Bonus", "2026-08-13 11:30", 1234)
    tracker.insert_income(700, "Salary", "Bank Meli", "test", "2026-08-15 11:30", 1234)
    tracker.insert_income(
        10000, "Salary", "Bank", "Other user", "2026-08-16 12:00", 9999
    )
    tracker.insert_income(400, "Salary", "Bank Meli", "test", "2026-08-17 11:30", 1234)
    tracker.insert_income(800, "Salary", "Bank Meli", "test", "2026-08-18 11:30", 1234)
    tracker.insert_income(2200, "Bonus", "Bank Meli", "test", "2026-08-18 13:30", 1234)
    tracker.insert_income(100, "Bonus", "Bank Meli", "test", "2026-08-18 17:30", 1234)
    recent = recent_transactions(1234, tracker, 10)

    assert "🕐 LATEST TRANSACTIONS" in recent
    assert "💰 Bonus\n100 T" in recent
    assert "💰 Bonus\n2,200 T" in recent
    assert "💸 Food\n100 T" in recent
    assert "💸 Travel\n2,200 T" in recent
    assert "Other user" not in recent


def test_recent_transactions_fewer_than_limit():
    tracker = Tracker(":memory:")
    tracker.insert_income(2000, "Salary", "Meli", "Salary", "2026-08-18 10:00", 1234)
    tracker.insert_expense(500, "Food", "Meli", "Lunch", "2026-08-18 11:00", 1234)
    recent = recent_transactions(1234, tracker, 5)

    assert "Salary" in recent
    assert "Food" in recent
    assert recent.count("📅") == 2


def test_recent_transactions_respects_limit():
    tracker = Tracker(":memory:")
    for i in range(7):
        tracker.insert_income(
            100 * (i + 1),
            "Salary",
            "Meli",
            f"Test {i}",
            f"2026-08-18 10:0{i}:00",
            1234,
        )

    recent = recent_transactions(1234, tracker, 5)
    assert recent.count("📅") == 5


def test_income_to_dict():
    incomes = [(2000, "salary", "Meli", "monthly salary", "2026-08-18 13:00", 1234)]
    result = income_to_dict(incomes)
    assert result == [
        {
            "type": "income",
            "amount": 2000,
            "name": "salary",
            "account": "Meli",
            "description": "monthly salary",
            "timestamp": "2026-08-18 13:00",
        }
    ]


def test_expense_to_dict():
    expenses = [(500, "Food", "Meli", "Dinner", "2026-08-18 19:00", 1234)]
    result = expense_to_dict(expenses)
    assert result == [
        {
            "type": "expense",
            "amount": 500,
            "name": "Food",
            "account": "Meli",
            "description": "Dinner",
            "timestamp": "2026-08-18 19:00",
        }
    ]


def test_save_transaction():
    tracker = Tracker(":memory:")
    state = {
        "action": "income",
        "amount": 2000,
        "title": "salary",
        "account": "Meli",
        "description": "monthly salary",
    }
    save_transaction(state, 1234, tracker)
    incomes = tracker.fetch_incomes(1234)

    assert len(incomes) == 1
    assert incomes[0][0] == 2000
    assert incomes[0][1] == "salary"
    assert incomes[0][2] == "Meli"
    assert incomes[0][3] == "monthly salary"
    assert incomes[0][5] == 1234
