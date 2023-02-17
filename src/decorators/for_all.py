import inspect
from typing import Any, Callable, TypeVar

__all__ = ["for_all_methods"]

F = TypeVar("F", bound = Callable[..., Any])
T = TypeVar("T")

# From https://stackoverflow.com/a/6307868/540552 and https://stackoverflow.com/a/9087626/540552
# Unknown author (used to be named delnan, but now is simply presented as user395760)
def for_all_methods(decorator: Callable[[F], F]) -> Callable[[type[T]], type[T]]:
    def decorate(cls: type[T]) -> type[T]:
        for name, fn in inspect.getmembers(cls, inspect.isroutine):
            setattr(cls, name, decorator(fn))
        return cls
    return decorate

del T
del F