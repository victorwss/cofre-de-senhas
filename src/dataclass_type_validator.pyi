from typing import Any, Callable, TypeVar

T = TypeVar("T")

class TypeValidationError(Exception):
    ...

def dataclass_type_validator(target: Any, strict: bool = ...) -> None:
    ...

def dataclass_validate(cls: Callable[..., T] = ..., *, strict: bool = ..., before_post_init: bool = ...) -> Callable[..., T]:
    ...

del T