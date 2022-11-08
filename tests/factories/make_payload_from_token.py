import jwt

from auth.config import JwtConfig
from auth.domain.entities import Payload


def make_payload_from_token(config: JwtConfig, token: str) -> Payload:
    token_claims = jwt.decode(token, config.public_key, algorithms=[config.algorithm])
    user_id: str = token_claims["user_id"]

    return Payload.create(user_id=user_id).unwrap()
