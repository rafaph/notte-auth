from abc import ABCMeta, abstractmethod

from option import Result
from pydantic import BaseModel, EmailStr

from auth.lib.pydantic import UUIDStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    id: UUIDStr


class UserClient(metaclass=ABCMeta):
    @abstractmethod
    async def login(self, request: LoginRequest) -> Result[LoginResponse, Exception]:
        raise NotImplementedError()  # pragma: no cover
