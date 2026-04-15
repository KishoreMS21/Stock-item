"""Generate actionable recommendations from business state."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sqlalchemy.orm import Session

from app.ai.data import daily_expenses, daily_product_sales, list_products


@dataclass
class Suggestion:
    title: str
    rationale: str
    action: str


def generate_recommendations(db: Session, business_id: int) -> list[Suggestion]:
    out: list[Suggestion] = []

    # Reorder low inventory
    for p in list_products(db, business_id):
        if p.stock_on_hand <= p.reorder_point:
            series = daily_product_sales(db, business_id, p.id, days=30)
            avg = float(series.mean()) if not series.empty else 0.0
            reorder_qty = max(p.min_stock, int(avg * 30))
            out.append(Suggestion(
                title=f"Reorder {p.name}",
                rationale=f"Stock ({p.stock_on_hand}) is at or below reorder point ({p.reorder_point}).",
                action=f"Order ~{reorder_qty} units of {p.sku} to cover ~30 days of demand.",
            ))

    # Boost high-demand products (>50% growth month-over-month)
    for p in list_products(db, business_id):
        series = daily_product_sales(db, business_id, p.id, days=60)
        if len(series) < 45:
            continue
        last30 = float(series.tail(30).sum())
        prior30 = float(series.iloc[-60:-30].sum())
        if prior30 > 0 and last30 > prior30 * 1.5:
            growth = int((last30 / prior30 - 1) * 100)
            out.append(Suggestion(
                title=f"Increase stock for {p.name}",
                rationale=f"Demand grew {growth}% month-over-month.",
                action=f"Raise reorder point for {p.sku} and secure additional supply.",
            ))

    # Expense trimming suggestion
    exp = daily_expenses(db, business_id).squeeze()
    if isinstance(exp, pd.Series) and len(exp) >= 30:
        recent = float(exp.tail(7).mean())
        baseline = float(exp.iloc[-37:-7].mean()) if len(exp) >= 37 else float(exp.mean())
        if baseline > 0 and recent > baseline * 1.3:
            out.append(Suggestion(
                title="Review recent expenses",
                rationale=f"Last-7-day average spend is {int(recent / baseline * 100)}% of your baseline.",
                action="Audit operations/marketing line items for cuts.",
            ))

    return out


def persist_recommendations(db: Session, business_id: int, items: list[Suggestion]) -> None:
    from app.models import Recommendation

    for s in items:
        db.add(Recommendation(
            business_id=business_id, title=s.title, rationale=s.rationale, action=s.action,
        ))
    db.commit()
