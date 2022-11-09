from abc import ABCMeta
from typing import TYPE_CHECKING, Annotated, Any, Callable, Generator, Type, TypeVar
from uuid import UUID

from option import Err, Ok, Result
from pydantic import BaseModel as DefaultBaseModel
from pydantic import ValidationError

T = TypeVar("T")


def safe_parse(func: Callable[[], T]) -> Result[T, ValidationError]:
    try:
        result = Ok(func())
    except ValidationError as error:
        result = Err(error)

    return result


if TYPE_CHECKING:
    UUIDStr = Annotated[str, ...]  # pragma: no cover
else:

    class UUIDStr(str):
        @classmethod
        def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
            yield cls.validate

        @classmethod
        def validate(cls, value: Any) -> str:
            if not isinstance(value, str):
                raise TypeError("string required")  # pragma: no cover
            UUID(value, version=4)
            return value


Model = TypeVar("Model", bound="BaseModel")


class BaseModel(DefaultBaseModel, metaclass=ABCMeta):
    @classmethod
    def create(cls: Type["Model"], **kwargs: Any) -> Result["Model", ValidationError]:
        return safe_parse(lambda: cls(**kwargs))
