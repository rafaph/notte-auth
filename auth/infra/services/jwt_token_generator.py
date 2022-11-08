from datetime import datetime, timedelta, timezone

import jwt
from option import Err, Ok, Result

from auth.application.services import TokenGenerator
from auth.config import JwtConfig
from auth.domain.entities import Payload


class JwtTokenGenerator(TokenGenerator):
    def __init__(self, config: JwtConfig) -> None:
        self._config = config

    def _generate(self, payload: Payload) -> str:
        now = datetime.now(tz=timezone.utc)
        exp = now + timedelta(minutes=self._config.expiration_in_minutes)
        return jwt.encode(
            payload={
                **payload.dict(),
                "iat": now,
                "nbf": now,
                "exp": exp,
                "iss": "urn:notte",
            },
            key=self._config.private_key,
            algorithm=self._config.algorithm,
        )

    async def generate(self, payload: Payload) -> Result[str, Exception]:
        try:
            result = Ok(self._generate(payload))
        except Exception as exc:
            result = Err(exc)

        return result
