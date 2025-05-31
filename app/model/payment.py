
import enum
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from . import BaseModel


class PaymentStatus(enum.Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class Payment(BaseModel):
    __tablename__ = "Payment"

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending
    )
