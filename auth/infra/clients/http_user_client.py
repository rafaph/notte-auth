from httpx import AsyncClient
from option import Err, Ok, Result

from auth.domain.clients import LoginRequest, LoginResponse, UserClient


class HTTPUserClient(UserClient):
    def __init__(self, client: AsyncClient):
        self._client = client

    async def login(self, request: LoginRequest) -> Result[LoginResponse, Exception]:
        try:
            response = await self._client.post("/login", json=request.json())
            response.raise_for_status()
            login_response = LoginResponse.parse_obj(response.json())
            result = Ok(login_response)
        except Exception as exc:
            result = Err(exc)

        return result
