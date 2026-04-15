"""Trend analysis across sales, products, and seasonality."""
from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.ai.data import daily_product_sales, daily_sales, list_products


def revenue_growth_pct(db: Session, business_id: int) -> float:
    series = daily_sales(db, business_id).squeeze()
    if not isinstance(series, pd.Series) or len(series) < 60:
        return 0.0
    last = float(series.tail(30).sum())
    prior = float(series.iloc[-60:-30].sum())
    return round((last / prior - 1) * 100, 2) if prior else 0.0


def top_products(db: Session, business_id: int, limit: int = 5) -> list[dict]:
    results = []
    for p in list_products(db, business_id):
        series = daily_product_sales(db, business_id, p.id, days=30)
        results.append({
            "product_id": p.id,
            "name": p.name,
            "units_30d": float(series.sum()) if not series.empty else 0.0,
        })
    results.sort(key=lambda r: r["units_30d"], reverse=True)
    return results[:limit]


def seasonality_by_weekday(db: Session, business_id: int) -> list[dict]:
    series = daily_sales(db, business_id).squeeze()
    if not isinstance(series, pd.Series) or series.empty:
        return []
    df = series.to_frame(name="revenue")
    df["weekday"] = df.index.day_name()
    grouped = df.groupby("weekday")["revenue"].mean()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [{"weekday": d, "avg_revenue": float(grouped.get(d, 0))} for d in order]
