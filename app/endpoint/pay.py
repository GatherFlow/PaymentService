
import aiohttp
from typing import Any
from loguru import logger

import fastapi
from datetime import datetime, timedelta

from aiomonobnk.types import InvoiceCreated

from app.enum import CreatePaymentStatus, ProductType, Gateway, GetPaymentStatus
from app.model import ProductAssign, Payment

from app.schema.request import CreatePaymentRequest
from app.schema.response import CreatePaymentResponse, GetPaymentResponse
from app.schema.response import CreatePaymentData, GetPaymentData

from app.database import get_async_session
from app.mono import mono_client

from config import get_settings


pay_router = fastapi.APIRouter()


async def create_ticket(event_ticket_id: int, user_id: str, cookies: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=f"{get_settings()}/ticket",
            json={
                event_ticket_id: event_ticket_id,
                user_id: user_id
            },
            cookies=cookies
        ) as response:
            logger.debug(f"{response} -> {await response.text()}")


async def get_ticket_price(event_ticket_id: int, cookies: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"{get_settings()}/event_ticket",
            params={"id": event_ticket_id},
            cookies=cookies,
            raise_for_status=False
        ) as response:
            logger.debug(f"{response} -> {await response.text()}")

            data = await response.json()

    return data.get("price")


async def get_sub_price(sub_id: int, cookies: dict):
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

    try:
        if data.target == ProductType.ticket:
            price = await get_ticket_price(data.target_id, cookies=request.cookies)
            if not price:
                return CreatePaymentResponse(
                    status=CreatePaymentStatus.no_event_ticket_error,
                    description=f"Can't find price of event_ticket with id={data.target_id}"
                )

            await create_ticket(
                event_ticket_id=data.target_id,
                user_id=request.state.user_id,
                cookies=request.cookies
            )

        else:
            price = await get_sub_price(sub_id=data.target_id, cookies=request.cookies)
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

    except Exception as err:
        logger.exception(err)

        return CreatePaymentResponse(
            status=CreatePaymentStatus.unexpected_error,
            description=str(err)
        )

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
    payment_id: int,
    response: fastapi.Response,
    request: fastapi.Request
) -> GetPaymentResponse:

    async with get_async_session() as session:
        assign = await session.get(ProductAssign, payment_id)
        if assign:
            payment = await session.get(Payment, payment_id)

    response.status_code = 404
    if not assign:
        return GetPaymentResponse(
            status=GetPaymentStatus.no_payment_error,
            description=f"Can't find payment with id={payment_id}"
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
