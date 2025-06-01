
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from app.enum import ProductType, AssignStatus
from . import BaseModel


class ProductAssign(BaseModel):
    __tablename__ = 'ProductAssign'

    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False
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
