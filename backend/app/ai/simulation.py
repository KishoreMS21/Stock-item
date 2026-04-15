"""Scenario simulation — `what if I increase stock by 20%?` style queries."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai.data import daily_product_sales, list_products


def simulate_stock_change(
    db: Session,
    business_id: int,
    stock_increase_pct: float,
) -> dict:
    """Simulate raising stock for all products by a given %.

    Returns projected incremental revenue if the extra stock sells at
    current daily rate over 30 days, capped by the added inventory.
    """
    factor = 1 + stock_increase_pct / 100
    total_extra_units = 0
    projected_revenue = 0.0
    per_product: list[dict] = []

    for p in list_products(db, business_id):
        extra_units = int(p.stock_on_hand * (factor - 1))
        if extra_units <= 0:
            continue
        series = daily_product_sales(db, business_id, p.id, days=30)
        daily = float(series.mean()) if not series.empty else 0.0
        sellable = min(extra_units, int(daily * 30))
        revenue = sellable * float(p.unit_price)
        total_extra_units += extra_units
        projected_revenue += revenue
        per_product.append({
            "product_id": p.id,
            "name": p.name,
            "extra_units": extra_units,
            "projected_sellable_30d": sellable,
            "projected_revenue_30d": round(revenue, 2),
        })

    return {
        "stock_increase_pct": stock_increase_pct,
        "total_extra_units": total_extra_units,
        "projected_revenue_30d": round(projected_revenue, 2),
        "per_product": per_product,
    }
