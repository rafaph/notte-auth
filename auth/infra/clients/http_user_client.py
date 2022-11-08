from dataclasses import asdict

from httpx import AsyncClient
from option import Err, Ok, Result

from auth.application.clients import LoginRequest, LoginResponse, UserClient


class HTTPUserClient(UserClient):
    def __init__(self, client: AsyncClient):
        self._client = client

    async def login(self, *, request: LoginRequest) -> Result[LoginResponse, Exception]:
        try:
            response = await self._client.post("/users/verify", json=asdict(request))
            response.raise_for_status()
            login_response = LoginResponse(**response.json())
            result = Ok(login_response)
        except Exception as exc:
            result = Err(exc)

        return result
