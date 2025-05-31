
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import mapped_column, Mapped
import enum

from . import BaseModel


class ProductType(enum.Enum):
    sub = "Sub"
    ticket = "Ticket"


class AssignStatus(enum.Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class ProductAssign(BaseModel):
    __tablename__ = 'ProductAssign'

    payment_method_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('PaymentMethod.id'), nullable=False
    )
    payment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('Payment.id'), nullable=False
    )
    target_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    target: Mapped[ProductType] = mapped_column(
        Enum(ProductType), nullable=False
    )
    status: Mapped[AssignStatus] = mapped_column(
        Enum(AssignStatus), nullable=False, default=AssignStatus.pending
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
