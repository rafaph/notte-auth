from option import Result
from pydantic import BaseModel, ValidationError

from auth.lib.pydantic import UUIDStr, safe_parse


class Payload(BaseModel):
    user_id: UUIDStr

    @staticmethod
    def create(*, user_id: str) -> Result["Payload", ValidationError]:
        return safe_parse(lambda: Payload(user_id=user_id))
