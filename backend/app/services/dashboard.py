from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Expense, Product, Sale
from app.schemas.dashboard import DashboardOut, KpiCard, SeriesPoint


def build_dashboard(db: Session, business_id: int) -> DashboardOut:
    now = datetime.utcnow()
    start = now - timedelta(days=30)

    revenue_30d = float(
        db.query(func.coalesce(func.sum(Sale.total), 0))
        .filter(Sale.business_id == business_id, Sale.sold_at >= start)
        .scalar()
    )
    expenses_30d = float(
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.business_id == business_id, Expense.incurred_at >= start)
        .scalar()
    )
    profit_30d = revenue_30d - expenses_30d
    margin = (profit_30d / revenue_30d * 100) if revenue_30d else 0.0

    inventory_value = float(
        db.query(func.coalesce(func.sum(Product.unit_cost * Product.stock_on_hand), 0))
        .filter(Product.business_id == business_id)
        .scalar()
    )
    low_stock = (
        db.query(func.count(Product.id))
        .filter(
            Product.business_id == business_id,
            Product.stock_on_hand <= Product.reorder_point,
        )
        .scalar()
    )

    rev_series = _daily_series(db, business_id, Sale, Sale.sold_at, Sale.total, start, now)
    exp_series = _daily_series(db, business_id, Expense, Expense.incurred_at, Expense.amount, start, now)

    return DashboardOut(
        revenue_30d=revenue_30d,
        expenses_30d=expenses_30d,
        profit_30d=profit_30d,
        profit_margin_pct=round(margin, 2),
        inventory_value=inventory_value,
        low_stock_count=int(low_stock or 0),
        revenue_series=rev_series,
        expense_series=exp_series,
        kpis=[
            KpiCard(label="Revenue (30d)", value=revenue_30d),
            KpiCard(label="Expenses (30d)", value=expenses_30d),
            KpiCard(label="Profit (30d)", value=profit_30d),
            KpiCard(label="Inventory Value", value=inventory_value),
        ],
    )


def _daily_series(db, business_id, model, date_col, value_col, start, end):
    rows = (
        db.query(func.date(date_col).label("d"), func.coalesce(func.sum(value_col), 0))
        .filter(model.business_id == business_id, date_col >= start)
        .group_by("d")
        .order_by("d")
        .all()
    )
    return [SeriesPoint(date=str(d), value=float(v)) for d, v in rows]
