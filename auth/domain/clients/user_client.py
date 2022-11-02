from abc import ABCMeta, abstractmethod

from option import Result
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user_id: str


class UserClient(metaclass=ABCMeta):
    @abstractmethod
    async def login(self, request: LoginRequest) -> Result[LoginResponse, Exception]:
        ...
