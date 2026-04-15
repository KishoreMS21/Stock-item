"""Stock + cash flow forecasting helpers (Phase 2).

Uses pandas + statsmodels. Kept minimal and deterministic — caller supplies
historical series and receives a forecast horizon back.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def forecast_series(series: pd.Series, periods: int = 14) -> pd.Series:
    """Forecast a daily-indexed series `periods` steps ahead.

    Falls back to a naive mean forecast if the series is too short for
    Holt-Winters.
    """
    series = series.asfreq("D").fillna(0)
    if len(series) < 14:
        mean = float(series.mean()) if len(series) else 0.0
        idx = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=periods) if len(series) else pd.date_range(pd.Timestamp.utcnow().normalize(), periods=periods)
        return pd.Series(np.full(periods, mean), index=idx)

    model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
    fit = model.fit()
    return fit.forecast(periods)


def days_until_stockout(current_stock: int, recent_daily_sales: pd.Series) -> int | None:
    """Return estimated days until stockout given recent daily sales."""
    if current_stock <= 0:
        return 0
    avg = float(recent_daily_sales.mean()) if len(recent_daily_sales) else 0.0
    if avg <= 0:
        return None
    return int(current_stock // avg)
