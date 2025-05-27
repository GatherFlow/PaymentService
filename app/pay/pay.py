
import fastapi


pay_router = fastapi.APIRouter()


@pay_router.post("/")
async def create_payment():
    return "Created Payment: 123"


@pay_router.get("/")
async def get_payment():
    return "Status: ok"
