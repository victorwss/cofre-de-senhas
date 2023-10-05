from typing import Any, Callable, ForwardRef, List, Literal, Optional, TypedDict, TypeVar, TYPE_CHECKING

def _just_some_func_dont_call() -> None: # pragma: no cover
    assert False

CallableTypeReal1 = type(_just_some_func_dont_call)
CallableTypeReal2 = type(print)

if TYPE_CHECKING: # pragma: no cover

    class UnionType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class OptionalType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class LiteralType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class GenericType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

        @property
        def __origin__(self) -> type:
            pass

    class GenericAlias(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

        @property
        def __origin__(self) -> type:
            pass

    class EllipsisType(type):
        pass

    class CallableTypeFormal(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class TypedDictType(type):
        pass

else:
    UnionType          = type(str | int)
    OptionalType       = type(Optional[int])
    LiteralType        = type(Literal[True])
    GenericType        = type(list[str])
    GenericAlias       = type(List[str])
    EllipsisType       = type(...)
    CallableTypeFormal = type(Callable[[], Any])
    TypedDictType      = type(TypedDict('X', {'x': int}))

TT1 = GenericAlias | ForwardRef | str | None
TT2 = type[Any] | UnionType | OptionalType | LiteralType | GenericType | CallableTypeFormal | TypedDictType
TT3 = [type, UnionType, OptionalType, LiteralType, GenericType, CallableTypeFormal, TypedDictType]