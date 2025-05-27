
import fastapi
import uvicorn

from .endpoint import pay_router

from config import APP_HOST, APP_PORT


app = fastapi.FastAPI()
app.include_router(pay_router)


def start_app():
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
