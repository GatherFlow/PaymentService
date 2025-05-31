
from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from . import BaseModel


class PaymentMethod(BaseModel):
    __tablename__ = "PaymentMethod"

    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    card: Mapped[str] = mapped_column(
        String(19), nullable=False
    )
    expiration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    cvv: Mapped[str] = mapped_column(
        Integer, nullable=False
    )
    holder: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
