import os
from typing import Annotated

from option import Result
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ValidationError,
    confloat,
    conint,
    constr,
    validator,
)

from auth.lib.pydantic import safe_parse


class JwtConfig(BaseModel):
    expiration_in_minutes: Annotated[float, confloat(gt=0)]
    private_key: Annotated[str, constr(min_length=1)]
    public_key: Annotated[str, constr(min_length=1)]
    algorithm: str = "EdDSA"

    @validator("private_key", "public_key")
    def remove_extra_backslash(cls, value: str) -> str:
        return value.replace(r"\n", "\n")


class UserConfig(BaseModel):
    base_url: AnyHttpUrl


class AppConfig(BaseModel):
    port: Annotated[int, conint(ge=80)]


class Config(BaseModel):
    app: AppConfig
    jwt: JwtConfig
    user: UserConfig

    @staticmethod
    def create() -> Result["Config", ValidationError]:
        return safe_parse(
            lambda: Config.parse_obj(
                {
                    "app": {"port": os.environ.get("PORT")},
                    "jwt": {
                        "expiration_in_minutes": os.environ.get(
                            "JWT_EXPIRATION_IN_MINUTES"
                        ),
                        "private_key": os.environ.get("JWT_PRIVATE_KEY"),
                        "public_key": os.environ.get("JWT_PUBLIC_KEY"),
                    },
                    "user": {"base_url": os.environ.get("USER_BASE_URL")},
                }
            )
        )
