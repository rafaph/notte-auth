from abc import ABCMeta, abstractmethod

from option import Result

from auth.domain.entities import Payload


class TokenGenerator(metaclass=ABCMeta):
    @abstractmethod
    async def generate(self, *, payload: Payload) -> Result[str, Exception]:
        raise NotImplementedError()  # pragma: no cover
