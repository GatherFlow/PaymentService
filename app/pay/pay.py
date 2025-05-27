
import fastapi


pay_router = fastapi.APIRouter()


@pay_router.get("/")
async def send_message():
    return "<h1>Hello PayService</h1>"
