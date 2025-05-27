
import fastapi

from app.schema.request import CreatePaymentRequest, GetPaymentRequest
from app.schema.response import CreatePaymentResponse, GetPaymentResponse


pay_router = fastapi.APIRouter()


@pay_router.post(
    path="/",
    response_model=CreatePaymentResponse,
    description="Create new payment"
)
async def create_payment(
    data: CreatePaymentRequest
) -> CreatePaymentResponse:

    return "Created Payment: 123"


@pay_router.get(
    path="/",
    response_model=GetPaymentResponse,
    description="Get status of created payment"
)
async def get_payment(
    data: GetPaymentRequest
) -> GetPaymentResponse:

    return "Status: ok"
