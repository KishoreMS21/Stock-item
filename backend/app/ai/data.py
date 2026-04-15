"""Pull historical data into pandas DataFrames for the AI layer."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Expense, Product, Sale, SaleItem


def daily_sales(db: Session, business_id: int, days: int = 180) -> pd.DataFrame:
    start = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(Sale.sold_at, Sale.total)
        .filter(Sale.business_id == business_id, Sale.sold_at >= start)
        .all()
    )
    if not rows:
        return pd.DataFrame(columns=["date", "revenue"]).set_index("date")
    df = pd.DataFrame(rows, columns=["date", "revenue"])
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    return df.groupby("date")["revenue"].sum().astype(float).to_frame()


def daily_expenses(db: Session, business_id: int, days: int = 180) -> pd.DataFrame:
    start = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(Expense.incurred_at, Expense.amount)
        .filter(Expense.business_id == business_id, Expense.incurred_at >= start)
        .all()
    )
    if not rows:
        return pd.DataFrame(columns=["date", "amount"]).set_index("date")
    df = pd.DataFrame(rows, columns=["date", "amount"])
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    return df.groupby("date")["amount"].sum().astype(float).to_frame()


def daily_product_sales(db: Session, business_id: int, product_id: int, days: int = 180) -> pd.Series:
    start = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(Sale.sold_at, SaleItem.quantity)
        .join(SaleItem, SaleItem.sale_id == Sale.id)
        .filter(
            Sale.business_id == business_id,
            SaleItem.product_id == product_id,
            Sale.sold_at >= start,
        )
        .all()
    )
    if not rows:
        return pd.Series(dtype=float)
    df = pd.DataFrame(rows, columns=["date", "qty"])
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    return df.groupby("date")["qty"].sum().astype(float)


def list_products(db: Session, business_id: int) -> list[Product]:
    return db.query(Product).filter(Product.business_id == business_id).all()
