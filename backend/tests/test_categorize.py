from app.ai.categorize import categorize
from app.models.expense import ExpenseCategory


def test_marketing_keywords() -> None:
    assert categorize("Facebook ads campaign") == ExpenseCategory.MARKETING


def test_salary_keywords() -> None:
    assert categorize("Monthly payroll run") == ExpenseCategory.SALARIES


def test_inventory_keywords() -> None:
    assert categorize("Supplier restock order") == ExpenseCategory.INVENTORY


def test_unknown_falls_through() -> None:
    assert categorize("misc") == ExpenseCategory.OTHER


def test_none_description() -> None:
    assert categorize(None) == ExpenseCategory.OTHER
