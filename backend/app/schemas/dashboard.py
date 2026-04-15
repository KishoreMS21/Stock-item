from pydantic import BaseModel


class KpiCard(BaseModel):
    label: str
    value: float
    delta_pct: float | None = None


class SeriesPoint(BaseModel):
    date: str
    value: float


class DashboardOut(BaseModel):
    revenue_30d: float
    expenses_30d: float
    profit_30d: float
    profit_margin_pct: float
    inventory_value: float
    low_stock_count: int
    revenue_series: list[SeriesPoint]
    expense_series: list[SeriesPoint]
    kpis: list[KpiCard]
