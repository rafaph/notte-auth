from typing import Callable, TypeVar

from option import Err, Ok, Result
from pydantic import ValidationError

T = TypeVar("T")


def safe_parse(func: Callable[[], T]) -> Result[T, ValidationError]:
    try:
        result = Ok(func())
    except ValidationError as error:
        result = Err(error)

    return result
