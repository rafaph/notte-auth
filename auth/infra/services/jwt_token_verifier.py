import jwt
from option import Result

from auth.application.services import TokenVerifier
from auth.config import JwtConfig
from auth.domain.entities import Payload


class JwtTokenVerifier(TokenVerifier):
    def __init__(self, config: JwtConfig) -> None:
        self._config = config

    async def verify(self, token: str) -> Result[Payload, Exception]:
        try:
            token_payload = jwt.decode(
                token,
                self._config.public_key,
                algorithms=[self._config.algorithm],
            )
            payload = Payload.create(user_id=token_payload["user_id"]).unwrap()
            result = Result.Ok(payload)
        except Exception as exc:
            result = Result.Err(exc)

        return result
