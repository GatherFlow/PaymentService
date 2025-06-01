
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Enum, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped

from app.enum import Gateway
from . import BaseModel


class Payment(BaseModel):
    __tablename__ = 'Payment'

    gateway: Mapped[Gateway] = mapped_column(
        Enum(Gateway), nullable=False
    )
    url: Mapped[str] = mapped_column(
        String(255), nullable=True
    )
    external_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
