import inspect
from typing import Any, Callable, TypeVar

__all__ = ["for_all_methods"]

_F = TypeVar("_F", bound = Callable[..., Any])
_T = TypeVar("_T")

# From https://stackoverflow.com/a/6307868/540552 and https://stackoverflow.com/a/9087626/540552
# Unknown author (used to be named delnan, but now is simply presented as user395760)
def for_all_methods(decorator: Callable[[_F], _F], even_dunders: bool = False) -> Callable[[type[_T]], type[_T]]:
    def decorate(cls: type[_T]) -> type[_T]:
        for name, fn in inspect.getmembers(cls, inspect.isroutine):
            if even_dunders or (not name.startswith("__") and not name.endswith("__")):
                setattr(cls, name, decorator(fn))
        return cls
    return decorate