from validator import TypeValidationError, dataclass_validate
from dataclasses import dataclass
from typing import Any, Callable, ParamSpec, TypeVar
from pytest import raises


def test_hascall_1a() -> None:
    def u(x: float, y: int) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall1:
        x1: Callable[[float, int], str]

    t1: HasCall1 = HasCall1(u)
    assert t1.x1 == u


def test_hascall_1b() -> None:
    def u(x: float, y: int) -> int:
        return 6

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall1:
        x1: Callable[[float, int], str]

    with raises(TypeValidationError):
        HasCall1(u)  # type: ignore


def test_hascall_1c() -> None:
    def u(x: str, y: int) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall1:
        x1: Callable[[float, int], str]

    with raises(TypeValidationError):
        HasCall1(u)  # type: ignore


def test_hascall_1d() -> None:
    def u(x: str) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall1:
        x1: Callable[[float, int], str]

    with raises(TypeValidationError):
        HasCall1(u)  # type: ignore


def test_hascall_1e() -> None:
    def u(x: float, y: int, w: int) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall1:
        x1: Callable[[float, int], str]

    with raises(TypeValidationError):
        HasCall1(u)  # type: ignore


def test_hascall_2a() -> None:
    def u(x: str, y: int, z: int) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall2:
        x1: Callable[[str, int, int], str]

    t1: HasCall2 = HasCall2(u)
    assert t1.x1 == u


def test_hascall_2b() -> None:
    def u(x: str, y: int) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall2:
        x1: Callable[[str, int, int], str]

    with raises(TypeValidationError):
        HasCall2(u)  # type: ignore


def test_hascall_3a() -> None:
    def u(x: str, y: int) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall3:
        x1: Callable[..., str]

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u


def test_hascall_3b() -> None:
    def u(x: str, y: int, z: float) -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall3:
        x1: Callable[..., str]

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u


def test_hascall_3c() -> None:
    def u() -> str:
        return "z"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall3:
        x1: Callable[..., str]

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u


def test_hascall_3d() -> None:
    def u() -> int:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall3:
        x1: Callable[..., str]

    with raises(TypeValidationError):
        HasCall3(u)  # type: ignore


def test_hascall_4a() -> None:
    def u(x: str, y: int) -> None:
        pass

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall4:
        x1: Callable[..., None]

    t1: HasCall4 = HasCall4(u)
    assert t1.x1 == u


def test_hascall_4b() -> None:
    def u(x: str, y: int, z: float) -> None:
        pass

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall4:
        x1: Callable[..., None]

    t1: HasCall4 = HasCall4(u)
    assert t1.x1 == u


def test_hascall_4c() -> None:
    def u() -> None:
        pass

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall4:
        x1: Callable[..., None]

    t1: HasCall4 = HasCall4(u)
    assert t1.x1 == u


def test_hascall_4d() -> None:
    def u() -> int:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall4:
        x1: Callable[..., None]

    with raises(TypeValidationError):
        HasCall4(u)  # type: ignore


def test_hascall_5a() -> None:
    def u(x: str, y: int, z: int) -> str:
        return "x"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall5:
        x1: Callable[[str, int, int], Any]

    t1: HasCall5 = HasCall5(u)
    assert t1.x1 == u


def test_hascall_5b() -> None:
    def u(x: str, y: int, z: int) -> int:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall5:
        x1: Callable[[str, int, int], Any]

    t1: HasCall5 = HasCall5(u)
    assert t1.x1 == u


def test_hascall_5c() -> None:
    def u(x: str, y: int, z: int) -> Any:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall5:
        x1: Callable[[str, int, int], Any]

    t1: HasCall5 = HasCall5(u)
    assert t1.x1 == u


def test_hascall_5d() -> None:
    def u(x: str, y: str, z: int) -> Any:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall5:
        x1: Callable[[str, int, int], Any]

    with raises(TypeValidationError):
        HasCall5(u)  # type: ignore


def test_hascall_6a() -> None:
    def u() -> str:
        return "x"

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall6:
        x1: Callable[..., Any]

    t1: HasCall6 = HasCall6(u)
    assert t1.x1 == u


def test_hascall_6b() -> None:
    def u(x: str, y: int) -> int:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall6:
        x1: Callable[..., Any]

    t1: HasCall6 = HasCall6(u)
    assert t1.x1 == u


def test_hascall_6c() -> None:
    def u(x: str) -> Any:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall6:
        x1: Callable[..., Any]

    t1: HasCall6 = HasCall6(u)
    assert t1.x1 == u


def test_hascall_7a() -> None:
    def u(x: str, y: Any, z: int) -> int:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall7:
        x1: Callable[[str, Any, int], int]

    t1: HasCall7 = HasCall7(u)
    assert t1.x1 == u


def test_hascall_7b() -> None:
    def u(x: str, y: str, z: int) -> int:
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall7:
        x1: Callable[[str, Any, int], int]

    with raises(TypeValidationError):
        HasCall7(u)


def test_hascall_8a() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class HasCall8:
            x1: Callable[["do_not_exist"], int]  # type: ignore  # noqa: F821


_P = ParamSpec("_P")
_R = TypeVar("_R")


def test_with_paramspec() -> None:
    def foo(what: Callable[_P, _R]) -> Callable[_P, _R]:
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            assert False
        return inner

    def bar() -> None:
        assert False

    @dataclass_validate
    @dataclass(frozen = True)
    class WithParamSpec:
        jj: Callable[..., Any]

    WithParamSpec(foo(bar))
