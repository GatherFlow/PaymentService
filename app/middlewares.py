
import aiohttp

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class CheckAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def get_user_id(self, cookies: dict) -> str | None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url="https://gather.onelil.tech/api/me",
                    cookies=cookies,
                    raise_for_status=True
                ) as response:

                    data = await response.json()
                    return data["id"]

        except Exception as err:
            return None

    async def dispatch(self, request: Request, call_next):
        user_id = await self.get_user_id(request.cookies)

        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"detail": f"Иди нахуй"}
            )

        request.state.user_id = user_id

        response = await call_next(request)
        return response
