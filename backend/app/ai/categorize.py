"""Heuristic expense auto-categorization.

Deterministic keyword rules are fast, dependency-free, and good enough for
v1. Can be swapped for an LLM call later.
"""
from __future__ import annotations

from app.models.expense import ExpenseCategory


KEYWORDS: dict[ExpenseCategory, tuple[str, ...]] = {
    ExpenseCategory.MARKETING: ("ads", "ad ", "facebook", "google ads", "campaign", "seo", "influencer"),
    ExpenseCategory.INVENTORY: ("supplier", "purchase order", "restock", "wholesale", "raw material"),
    ExpenseCategory.SALARIES: ("salary", "payroll", "wage", "stipend", "bonus"),
    ExpenseCategory.OPERATIONS: ("rent", "electric", "utility", "internet", "saas", "subscription", "hosting", "shipping"),
}


def categorize(description: str | None) -> ExpenseCategory:
    if not description:
        return ExpenseCategory.OTHER
    text = description.lower()
    for cat, kws in KEYWORDS.items():
        if any(k in text for k in kws):
            return cat
    return ExpenseCategory.OTHER
