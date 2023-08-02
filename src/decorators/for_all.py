import inspect
from typing import Any, Callable, Self, TypeVar

__all__ = ["for_all_methods"]

_F = TypeVar("_F", bound = Callable[..., Any])
_A = TypeVar("_A")
_T = TypeVar("_T")

class EmulatedProperty:
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(
            self: Self, \
            fget: Callable[[Any], _T] | None = None, \
            fset: Callable[[Any, Any], None] | None = None, \
            fdel: Callable[[Any], None] | None = None, \
            doc: str | None = None \
    ) -> None:
        self.fget: Callable[[Any], _T] | None = fget
        self.fset: Callable[[Any, _T], None] | None = fset
        self.fdel: Callable[[Any], None] | None = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__: str | None = doc

    def __get__(self: Self, obj: Any, objtype: Any = None) -> Any:
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self: Self, obj: Any, value: Any) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self: Self, obj: Any) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self: Self, fget: Callable[[Any], Any]) -> Self:
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self: Self, fset: Callable[[Any, Any], None]) -> Self:
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self: Self, fdel: Callable[[Any], None]) -> Self:
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

# From https://stackoverflow.com/a/6307868/540552 and https://stackoverflow.com/a/9087626/540552
# Unknown author (used to be named delnan, but now is simply presented as user395760)
def for_all_methods(decorator: Callable[[_F], _F], even_dunders: bool = False) -> Callable[[type[_T]], type[_T]]:

    def decorate(cls: type[_T]) -> type[_T]:
        for name, fn in inspect.getmembers(cls, inspect.isroutine):
            if even_dunders or (not name.startswith("__") and not name.endswith("__")):
                setattr(cls, name, decorator(fn))

        for name, fn in inspect.getmembers(cls, lambda x: isinstance(x, property)):
            if even_dunders or (not name.startswith("__") and not name.endswith("__")):
                p: property = property(decorator(fn.fget))
                if fn.fset: p = p.setter(decorator(fn.fset))
                if fn.fdel: p = p.deleter(decorator(fn.fdel))
                print(f"********************************** {name}")
                #p: EmulatedProperty = EmulatedProperty(fn.fget, fn.fset, fn.fdel, None)
                setattr(cls, name, p)

        return cls
    return decorate