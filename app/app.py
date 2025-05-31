
import fastapi
import uvicorn

from .endpoint import pay_router

from config import get_settings


app = fastapi.FastAPI()
app.include_router(pay_router)


def start_app():
    settings = get_settings()
    uvicorn.run(app, host=settings.app.host, port=settings.app.port)
