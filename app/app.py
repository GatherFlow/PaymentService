
import fastapi
import uvicorn
from .pay import pay_router


app = fastapi.FastAPI()
app.include_router(pay_router)


def start_app():
    uvicorn.run(app, host="0.0.0.0", port=8000)
