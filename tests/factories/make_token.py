from datetime import datetime, timedelta, timezone

import jwt

from auth.config import JwtConfig
from auth.domain.entities import Payload


def make_token(config: JwtConfig, payload: Payload) -> str:
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(minutes=config.expiration_in_minutes)
    return jwt.encode(
        payload={
            **payload.dict(),
            "iat": now,
            "nbf": now,
            "exp": exp,
            "iss": "urn:notte",
        },
        key=config.private_key,
        algorithm=config.algorithm,
    )
