"""Rule + stats-based risk alert generation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.ai.data import daily_expenses, daily_sales, list_products, daily_product_sales
from app.ai.forecasting import days_until_stockout
from app.models.alert import AlertKind, AlertSeverity


@dataclass
class RiskSignal:
    kind: AlertKind
    severity: AlertSeverity
    message: str


def generate_risk_signals(db: Session, business_id: int) -> list[RiskSignal]:
    signals: list[RiskSignal] = []

    rev = daily_sales(db, business_id).squeeze()
    exp = daily_expenses(db, business_id).squeeze()

    # Cash flow projection: burn rate vs current net over 30d
    if isinstance(exp, pd.Series) and not exp.empty:
        daily_burn = float(exp.tail(30).mean())
        daily_income = float(rev.tail(30).mean()) if isinstance(rev, pd.Series) and not rev.empty else 0.0
        net_daily = daily_income - daily_burn
        cash_30d = (daily_income - daily_burn) * 30
        if net_daily < 0 and daily_burn > 0:
            days = int(abs(cash_30d) / daily_burn) if daily_burn else 999
            signals.append(RiskSignal(
                AlertKind.CASH_FLOW,
                AlertSeverity.WARNING,
                f"Warning: Based on current spending, cash reserves may drop below safe levels in {days} days.",
            ))

    # Profit decline: compare last 15d vs prior 15d
    if isinstance(rev, pd.Series) and len(rev) >= 30 and isinstance(exp, pd.Series):
        last = float(rev.tail(15).sum() - exp.tail(15).sum())
        prior_rev = rev.iloc[-30:-15].sum() if len(rev) >= 30 else 0
        prior_exp = exp.iloc[-30:-15].sum() if len(exp) >= 30 else 0
        prior = float(prior_rev - prior_exp)
        if prior > 0 and last < prior * 0.8:
            drop = int((1 - last / prior) * 100) if prior else 0
            signals.append(RiskSignal(
                AlertKind.PROFIT_DECLINE,
                AlertSeverity.WARNING,
                f"Profit declined {drop}% vs the previous 15 days.",
            ))

    # Overspend: last 7 days avg > 1.5x prior 30 days avg
    if isinstance(exp, pd.Series) and len(exp) >= 30:
        recent = float(exp.tail(7).mean())
        baseline = float(exp.iloc[-37:-7].mean()) if len(exp) >= 37 else float(exp.iloc[:-7].mean())
        if baseline > 0 and recent > baseline * 1.5:
            signals.append(RiskSignal(
                AlertKind.OVERSPEND,
                AlertSeverity.WARNING,
                f"Weekly spending is {int(recent / baseline * 100)}% of your 30-day baseline.",
            ))

    # Stock risk per product
    for p in list_products(db, business_id):
        series = daily_product_sales(db, business_id, p.id, days=60)
        if series.empty:
            if p.stock_on_hand == 0:
                signals.append(RiskSignal(
                    AlertKind.LOW_STOCK,
                    AlertSeverity.INFO,
                    f"{p.name} is out of stock.",
                ))
            continue
        eta = days_until_stockout(p.stock_on_hand, series.tail(30))
        if eta is not None and eta <= 7:
            sev = AlertSeverity.CRITICAL if eta <= 3 else AlertSeverity.WARNING
            signals.append(RiskSignal(
                AlertKind.LOW_STOCK,
                sev,
                f"Stock for {p.name} will run out in {eta} days based on current sales trend.",
            ))
        elif eta is not None and eta > 180 and p.stock_on_hand > p.min_stock * 3:
            signals.append(RiskSignal(
                AlertKind.OVERSTOCK,
                AlertSeverity.INFO,
                f"{p.name} is overstocked — ~{eta} days of inventory on hand.",
            ))

    return signals


def persist_signals(db: Session, business_id: int, signals: list[RiskSignal]) -> None:
    from app.models import Alert

    # Deduplicate against recent identical messages (last 24h)
    cutoff = datetime.utcnow() - timedelta(hours=24)
    existing = {
        (a.kind, a.message)
        for a in db.query(Alert).filter(Alert.business_id == business_id, Alert.created_at >= cutoff).all()
    }
    for s in signals:
        if (s.kind, s.message) in existing:
            continue
        db.add(Alert(business_id=business_id, kind=s.kind, severity=s.severity, message=s.message))
    db.commit()
