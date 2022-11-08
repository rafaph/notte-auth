from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from option import Result


@dataclass
class LoginRequest:
    email: str
    password: str


@dataclass
class LoginResponse:
    id: str


class UserClient(metaclass=ABCMeta):
    @abstractmethod
    async def login(self, *, request: LoginRequest) -> Result[LoginResponse, Exception]:
        raise NotImplementedError()  # pragma: no cover
