
import enum
from sqlalchemy import Column, Integer, String, Enum

from . import BaseModel


class PaymentStatus(enum.Enum):
    pending = "pending"
    declined = "declined"
    accepted = "accepted"


class Payment(BaseModel):
    __tablename__ = "Payment"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
