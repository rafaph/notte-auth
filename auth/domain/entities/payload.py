from uuid import UUID

from option import Result
from pydantic import BaseModel, ValidationError, validator

from auth.lib.pydantic import safe_parse


class Payload(BaseModel):
    user_id: str

    @validator("user_id")
    def _validate_user_id(cls, value: str) -> str:
        UUID(value, version=4)
        return value

    @staticmethod
    def create(*, user_id: str) -> Result["Payload", ValidationError]:
        return safe_parse(lambda: Payload(user_id=user_id))
