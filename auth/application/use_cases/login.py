import logging
from dataclasses import asdict, dataclass

from option import Result

from auth.application.clients import LoginRequest, UserClient
from auth.application.services import TokenGenerator
from auth.domain.entities import Payload


class Login:
    @dataclass
    class Input:
        email: str
        password: str

    @dataclass
    class Output:
        token: str

    def __init__(
        self, *, user_client: UserClient, token_generator: TokenGenerator
    ) -> None:
        self._user_client = user_client
        self._token_generator = token_generator

    async def execute(self, *, input: Input) -> Result[Output, Exception]:
        request = LoginRequest(**asdict(input))
        login_result = await self._user_client.login(request=request)

        if login_result.is_err:
            logging.info(
                "failt to fetch user data from UserClient",
                extra={"error": login_result.unwrap_err()},
            )
            return Result.Err(Exception("invalid credentials"))

        response = login_result.unwrap()
        payload_result = Payload.create(user_id=response.id)
        if payload_result.is_err:
            logging.info(
                "fail to create Payload from UserClient response",
                extra={"error": payload_result.unwrap_err()},
            )
            return Result.Err(Exception("unknown error"))

        payload = payload_result.unwrap()
        token_result = await self._token_generator.generate(payload=payload)
        if token_result.is_err:
            logging.info(
                "fail to generate token from payload",
                extra={"error": token_result.unwrap_err()},
            )
            return Result.Err(Exception("unknown error"))

        return Result.Ok(self.Output(token=token_result.unwrap()))
