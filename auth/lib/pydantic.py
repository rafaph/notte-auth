from typing import TYPE_CHECKING, Annotated, Any, Callable, Generator, TypeVar
from uuid import UUID

from option import Err, Ok, Result
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
