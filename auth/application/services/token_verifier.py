from abc import ABCMeta, abstractmethod

from option import Result

from auth.domain.entities import Payload


class TokenVerifier(metaclass=ABCMeta):
    @abstractmethod
    async def verify(self, token: str) -> Result[Payload, Exception]:
        raise NotImplementedError()  # pragma: no cover
