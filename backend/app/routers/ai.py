from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.chatbot import ask
from app.ai.data import daily_expenses, daily_product_sales, daily_sales, list_products
from app.ai.forecasting import days_until_stockout, forecast_series
from app.ai.recommendations import generate_recommendations, persist_recommendations
from app.ai.risk import generate_risk_signals, persist_signals
from app.ai.simulation import simulate_stock_change
from app.ai.trends import revenue_growth_pct, seasonality_by_weekday, top_products
from app.auth.deps import get_current_user
from app.database import get_db
from app.models import Alert, Business, Recommendation, User
from app.schemas.ai import (
    AlertOut,
    ChatRequest,
    ChatResponse,
    ForecastPoint,
    ProfitForecastOut,
    RecommendationOut,
    SimulationRequest,
    StockForecastOut,
    TrendsOut,
)


router = APIRouter(prefix="/api/ai", tags=["ai"])


def _require_business(db: Session, business_id: int, user: User) -> Business:
    biz = db.query(Business).filter(
        Business.id == business_id, Business.owner_id == user.id
    ).first()
    if not biz:
        raise HTTPException(404, "Business not found")
    return biz


@router.get("/alerts", response_model=list[AlertOut])
def alerts(
    business_id: int,
    refresh: bool = True,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Alert]:
    _require_business(db, business_id, user)
    if refresh:
        persist_signals(db, business_id, generate_risk_signals(db, business_id))
    return (
        db.query(Alert)
        .filter(Alert.business_id == business_id, Alert.acknowledged.is_(False))
        .order_by(Alert.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/alerts/{alert_id}/ack", response_model=AlertOut)
def ack_alert(
    alert_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Alert:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    _require_business(db, alert.business_id, user)
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/recommendations", response_model=list[RecommendationOut])
def recommendations(
    business_id: int,
    refresh: bool = True,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Recommendation]:
    _require_business(db, business_id, user)
    if refresh:
        persist_recommendations(db, business_id, generate_recommendations(db, business_id))
    return (
        db.query(Recommendation)
        .filter(Recommendation.business_id == business_id)
        .order_by(Recommendation.created_at.desc())
        .limit(25)
        .all()
    )


@router.get("/forecast/stock", response_model=list[StockForecastOut])
def stock_forecast(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StockForecastOut]:
    _require_business(db, business_id, user)
    out: list[StockForecastOut] = []
    for p in list_products(db, business_id):
        series = daily_product_sales(db, business_id, p.id, days=90)
        eta = days_until_stockout(p.stock_on_hand, series.tail(30)) if not series.empty else None
        forecast = forecast_series(series, periods=14) if not series.empty else []
        points = (
            [ForecastPoint(date=str(idx.date()), value=float(v)) for idx, v in forecast.items()]
            if len(forecast) else []
        )
        avg = float(series.tail(30).mean()) if not series.empty else 0.0
        out.append(StockForecastOut(
            product_id=p.id,
            product_name=p.name,
            current_stock=p.stock_on_hand,
            days_until_stockout=eta,
            reorder_qty_suggested=max(p.min_stock, int(avg * 30)),
            demand_forecast_14d=points,
        ))
    return out


@router.get("/forecast/profit", response_model=ProfitForecastOut)
def profit_forecast(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfitForecastOut:
    _require_business(db, business_id, user)
    rev = daily_sales(db, business_id).squeeze()
    exp = daily_expenses(db, business_id).squeeze()
    rev_fc = forecast_series(rev, periods=30) if hasattr(rev, "__len__") and len(rev) else []
    exp_fc = forecast_series(exp, periods=30) if hasattr(exp, "__len__") and len(exp) else []
    total_rev = float(sum(rev_fc)) if len(rev_fc) else 0.0
    total_exp = float(sum(exp_fc)) if len(exp_fc) else 0.0
    series = []
    if len(rev_fc) and len(exp_fc):
        for idx in rev_fc.index:
            series.append(ForecastPoint(
                date=str(idx.date()),
                value=float(rev_fc.get(idx, 0) - exp_fc.get(idx, 0)),
            ))
    return ProfitForecastOut(
        next_30d_revenue=round(total_rev, 2),
        next_30d_expenses=round(total_exp, 2),
        next_30d_profit=round(total_rev - total_exp, 2),
        series=series,
    )


@router.get("/trends", response_model=TrendsOut)
def trends(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrendsOut:
    _require_business(db, business_id, user)
    return TrendsOut(
        revenue_growth_mom_pct=revenue_growth_pct(db, business_id),
        top_products_30d=top_products(db, business_id),
        seasonality_by_weekday=seasonality_by_weekday(db, business_id),
    )


@router.post("/simulate")
def simulate(
    business_id: int,
    payload: SimulationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    _require_business(db, business_id, user)
    return simulate_stock_change(db, business_id, payload.stock_increase_pct)


@router.post("/chat", response_model=ChatResponse)
def chat(
    business_id: int,
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    _require_business(db, business_id, user)
    return ChatResponse(answer=ask(db, business_id, payload.question))
