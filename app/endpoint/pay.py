
import aiohttp
from typing import Any

import fastapi
from datetime import datetime, timedelta

from aiomonobnk.types import InvoiceCreated

from app.enum import CreatePaymentStatus, ProductType, Gateway, GetPaymentStatus
from app.model import ProductAssign, Payment

from app.schema.request import CreatePaymentRequest, GetPaymentRequest
from app.schema.response import CreatePaymentResponse, GetPaymentResponse
from app.schema.response import CreatePaymentData, GetPaymentData

from app.database import get_async_session
from app.mono import mono_client

from config import get_settings


pay_router = fastapi.APIRouter()


async def get_event_ticket_id(ticket_id: int):
    if ticket_id == 1:
        return 1

    return None


async def get_ticket_price(event_ticket_id: int):
    if event_ticket_id == 1:
        return 10

    return None


async def get_sub_price(sub_id: int):
    if sub_id == 1:
        return 20

    return None


CREATE_PAYMENT_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {
        "description": "Not found target",
        "content": {
            "application/json": {
                "example": CreatePaymentResponse(
                    status=CreatePaymentStatus.no_event_ticket_error,
                    description=f"Can't find price of event_ticket with id=444"
                ).model_dump()
            }
        }
    }
}


GET_PAYMENT_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {
        "description": "Payment not found",
        "content": {
            "application/json": {
                "example": GetPaymentResponse(
                    status=GetPaymentStatus.no_payment_error,
                    description=f"Can't find price of event_ticket with id=444"
                ).model_dump()
            }
        }
    }
}


@pay_router.post(
    path="/",
    response_model=CreatePaymentResponse,
    responses=CREATE_PAYMENT_RESPONSES,
    description="Create new payment",
)
async def create_payment(
    data: CreatePaymentRequest,
    response: fastapi.Response,
    request: fastapi.Request
) -> CreatePaymentResponse:

    response.status_code = 404

    if data.target == ProductType.ticket:
        event_ticket_id = await get_event_ticket_id(data.target_id)
        if not event_ticket_id:
            return CreatePaymentResponse(
                status=CreatePaymentStatus.no_ticket_error,
                description=f"Can't find ticket with id={data.target_id}"
            )

        price = await get_ticket_price(event_ticket_id)
        if not price:
            return CreatePaymentResponse(
                status=CreatePaymentStatus.no_event_ticket_error,
                description=f"Can't find price of event_ticket with id={event_ticket_id}"
            )

    else:
        price = await get_sub_price(sub_id=data.target_id)
        if not price:
            return CreatePaymentResponse(
                status=CreatePaymentStatus.no_sub_error,
                description=f"Can't find price of sub with id={data.target_id}"
            )

    if data.gateway == Gateway.monobank:
        invoice: InvoiceCreated = await mono_client.create_invoice(
            amount=round(price * 100),
            validity=get_settings().monopay.lifetime_seconds
        )

        external_id = invoice.invoice_id
        gateway_url = invoice.page_url

    else:
        return CreatePaymentResponse(
            status=CreatePaymentStatus.unknown_gateway_error,
            description=f"Got unknown gateway={data.gateway}"
        )

    async with get_async_session() as session:
        payment = Payment(
            external_id=external_id,
            gateway=data.gateway,
            url=gateway_url
        )

        session.add(payment)
        await session.flush()

        assign = ProductAssign(
            user_id=request.state.user_id,
            payment_id=payment.id,
            target_id=data.target_id,
            target=data.target,
            expires_at=datetime.now() + timedelta(seconds=get_settings().monopay.lifetime_seconds)
        )

        session.add(assign)
        await session.commit()

    response.status_code = 200
    return CreatePaymentResponse(
        data=CreatePaymentData(
            payment_id=assign.id,
            payment_url=payment.url
        )
    )


@pay_router.get(
    path="/",
    response_model=GetPaymentResponse,
    responses=GET_PAYMENT_RESPONSES,
    description="Get status of created payment"
)
async def get_payment(
    data: GetPaymentRequest,
    response: fastapi.Response,
    request: fastapi.Request
) -> GetPaymentResponse:

    print(request.url)

    async with get_async_session() as session:
        assign = await session.get(ProductAssign, data.payment_id)
        if assign:
            payment = await session.get(Payment, data.payment_id)

    response.status_code = 404
    if not assign:
        return GetPaymentResponse(
            status=GetPaymentStatus.no_payment_error,
            description=f"Can't find payment with id={data.payment_id}"
        )

    response.status_code = 200
    return GetPaymentResponse(
        data=GetPaymentData(
            user_id=request.state.user_id,
            payment_id=assign.id,
            gateway=payment.gateway,
            url=payment.url,
            expires_at=round(assign.expires_at.timestamp()),
            status=assign.status
        )
    )
