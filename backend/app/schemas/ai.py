from datetime import datetime

from pydantic import BaseModel

from app.models.alert import AlertKind, AlertSeverity


class AlertOut(BaseModel):
    id: int
    kind: AlertKind
    severity: AlertSeverity
    message: str
    acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    id: int
    title: str
    rationale: str
    action: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ForecastPoint(BaseModel):
    date: str
    value: float


class StockForecastOut(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    days_until_stockout: int | None
    reorder_qty_suggested: int
    demand_forecast_14d: list[ForecastPoint]


class ProfitForecastOut(BaseModel):
    next_30d_revenue: float
    next_30d_expenses: float
    next_30d_profit: float
    series: list[ForecastPoint]


class TrendsOut(BaseModel):
    revenue_growth_mom_pct: float
    top_products_30d: list[dict]
    seasonality_by_weekday: list[dict]


class SimulationRequest(BaseModel):
    stock_increase_pct: float


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
