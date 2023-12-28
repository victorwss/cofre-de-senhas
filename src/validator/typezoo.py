from typing import Any, Callable, ForwardRef, List, Literal, Optional, ParamSpecArgs, ParamSpecKwargs, TypeAlias, TypeVar, TypedDict, TYPE_CHECKING


def _just_some_func_dont_call() -> None:  # pragma: no cover
    assert False


CallableTypeRealUserDefined = type(_just_some_func_dont_call)
CallableTypeRealBuiltIn = type(print)


if TYPE_CHECKING:  # pragma: no cover

    class UnionType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            assert False

    class OptionalType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            assert False

    class LiteralType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            assert False

    class GenericType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            assert False

        @property
        def __origin__(self) -> type:
            assert False

    class GenericAlias(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            assert False

        @property
        def __origin__(self) -> type:
            assert False

    class EllipsisType(type):
        pass

    class CallableTypeFormal(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            assert False

    class TypedDictType(type):
        pass

else:
    UnionType          = type(str | int)                   # noqa: E221
    OptionalType       = type(Optional[int])               # noqa: E221
    LiteralType        = type(Literal[True])               # noqa: E221
    GenericType        = type(list[str])                   # noqa: E221
    GenericAlias       = type(List[str])                   # noqa: E221
    EllipsisType       = type(...)                         # noqa: E221
    CallableTypeFormal = type(Callable[[], Any])           # noqa: E221
    TypedDictType      = type(TypedDict("X", {"x": int}))  # noqa: E221

TT1: TypeAlias = GenericAlias | ForwardRef | str | None

TT2: TypeAlias = type[Any] | UnionType | OptionalType | LiteralType | GenericType | CallableTypeFormal | TypedDictType \
    | ParamSpecArgs | ParamSpecKwargs | TypeVar

TT3: list[type[Any]] = [
    type, UnionType, OptionalType, LiteralType, GenericType, CallableTypeFormal, TypedDictType, ParamSpecArgs,
    ParamSpecKwargs, TypeVar
]
