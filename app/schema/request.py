
from pydantic import BaseModel
from app.enum import ProductType, Gateway


class CreatePaymentRequest(BaseModel):
    target_id: int
    target: ProductType
    gateway: Gateway = Gateway.monobank


class GetPaymentRequest(BaseModel):
    payment_id: int
