import inspect
from typing import Any, Callable, cast, TypeVar

__all__ = ["for_all_methods"]

_T = TypeVar("_T")
_X = TypeVar("_X")
_F = TypeVar("_F", bound = Callable[..., _X])
_D = TypeVar("_D", bound = Callable[[_F], _F])

# From https://stackoverflow.com/a/6307868/540552 and https://stackoverflow.com/a/9087626/540552
# Unknown author (used to be named delnan, but now is simply presented as user395760)
def for_all_methods(decorator: _D, *, even_dunders: bool = False, even_privates: bool = True) -> Callable[[type[_T]], type[_T]]:

    def inner_decorate(cls: type[_T]) -> type[_T]:
        for name, fn in inspect.getmembers(cls, inspect.isroutine):
            meth_name = fn.__name__
            dunder_method : bool = meth_name.startswith("__") and meth_name.endswith("__")
            private_method: bool = meth_name != name
            if (even_dunders and dunder_method) or (even_privates and private_method) or (not dunder_method and not private_method):
                setattr(cls, name, decorator(fn))

        for name, fn in inspect.getmembers(cls, lambda x: isinstance(x, property)):
            prop: property = cast(property, fn)
            prop_name: str | None = prop.fget.__name__ if prop.fget else prop.fset.__name__ if prop.fset else  prop.fdel.__name__ if prop.fdel else None
            assert prop_name is not None
            dunder_prop : bool = prop_name.startswith("__") and prop_name.endswith("__")
            private_prop: bool = prop_name != name
            if (even_dunders and dunder_prop) or (even_privates and private_prop) or (not dunder_prop and not private_prop):
                setter: Callable[[Callable[[Any, Any], None]], Callable[[Any, Any], None]] = cast(Callable[[Callable[[Any, Any], None]], Callable[[Any, Any], None]], decorator)
                deleter: Callable[[Callable[[Any], None]], Callable[[Any], None]] = cast(Callable[[Callable[[Any], None]], Callable[[Any], None]], decorator)
                p: property = prop
                if prop.fget: p = property(decorator(prop.fget))
                if prop.fset: p = p.setter(setter(prop.fset))
                if prop.fdel: p = p.deleter(deleter(prop.fdel))
                setattr(cls, name, p)

        return cls
    return inner_decorate