import inspect
from typing import Any, Callable, cast, Self, TypeVar

__all__ = ["for_all_methods"]

_T = TypeVar("_T")
_X = TypeVar("_X")
_F = TypeVar("_F", bound = Callable[..., _X])
_D = TypeVar("_D", bound = Callable[[_F], _F])

# From https://stackoverflow.com/a/6307868/540552 and https://stackoverflow.com/a/9087626/540552
# Unknown author (used to be named delnan, but now is simply presented as user395760)
def for_all_methods(decorator: _D, *, even_dunders: bool = False) -> Callable[[type[_T]], type[_T]]:

    def decorate(cls: type[_T]) -> type[_T]:
        for name, fn in inspect.getmembers(cls, inspect.isroutine):
            if even_dunders or (not name.startswith("__") and not name.endswith("__")):
                setattr(cls, name, decorator(fn))

        for name, fn in inspect.getmembers(cls, lambda x: isinstance(x, property)):
            if even_dunders or (not name.startswith("__") and not name.endswith("__")):
                prop: property = cast(property, fn)
                setter: Callable[[Callable[[Any, Any], None]], Callable[[Any, Any], None]] = cast(Callable[[Callable[[Any, Any], None]], Callable[[Any, Any], None]], decorator)
                deleter: Callable[[Callable[[Any], None]], Callable[[Any], None]] = cast(Callable[[Callable[[Any], None]], Callable[[Any], None]], decorator)
                p: property = prop
                if prop.fget: p = property(decorator(prop.fget))
                if prop.fset: p = p.setter(setter(prop.fset))
                if prop.fdel: p = p.deleter(deleter(prop.fdel))
                setattr(cls, name, p)

        return cls
    return decorate