
import fastapi


hello_router = fastapi.APIRouter()


@hello_router.get("")
async def send_message():
    return "<h1>Hello PayService</h1>"
