
from pydantic import BaseModel

from app.enum import CreatePaymentStatus, GetPaymentStatus
from app.enum import AssignStatus, Gateway


class CreatePaymentData(BaseModel):
    payment_id: int
    payment_url: str


class GetPaymentData(BaseModel):
    user_id: str
    payment_id: int
    gateway: Gateway
    url: str
    expires_at: int
    status: AssignStatus


class CreatePaymentResponse(BaseModel):
    status: CreatePaymentStatus = CreatePaymentStatus.ok
    description: str = None

    data: CreatePaymentData | None = None


class GetPaymentResponse(BaseModel):
    status: GetPaymentStatus = GetPaymentStatus.ok
    description: str = None

    data: GetPaymentData | None = None
