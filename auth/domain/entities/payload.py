from auth.lib.pydantic import BaseModel, UUIDStr


class Payload(BaseModel):
    user_id: UUIDStr
