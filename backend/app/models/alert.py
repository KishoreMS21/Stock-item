from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AlertSeverity(str, PyEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertKind(str, PyEnum):
    CASH_FLOW = "cash_flow"
    OVERSPEND = "overspend"
    PROFIT_DECLINE = "profit_decline"
    DEBT = "debt"
    LOW_STOCK = "low_stock"
    OVERSTOCK = "overstock"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    kind: Mapped[AlertKind] = mapped_column(Enum(AlertKind))
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    message: Mapped[str] = mapped_column(String(1000))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
