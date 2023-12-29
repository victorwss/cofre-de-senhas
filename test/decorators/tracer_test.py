from validator import TypeValidationError
from dataclasses import FrozenInstanceError
from decorators.tracer import Call, Logger
import pytest


class LocalTestException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def some_fn(x: str, y: int) -> float:
    return 42.0


def other_fn(x: str, y: int) -> float:
    return 27.0


def test_call_is_strong_typed_1() -> None:
    with pytest.raises(TypeValidationError):
        Call("a", ("x", 13), {"foo": 123, "bar": 321})  # type: ignore


def test_call_is_strong_typed_2() -> None:
    with pytest.raises(TypeValidationError):
        Call(some_fn, "xxx", {"foo": 123, "bar": 321})  # type: ignore


def test_call_is_strong_typed_3() -> None:
    with pytest.raises(TypeValidationError):
        Call(some_fn, ("x", 13), "xxx")  # type: ignore


def test_call_is_immutable() -> None:
    c = Call(some_fn, ("x", 13), {"foo": 123, "bar": 321})

    assert c.callee == some_fn
    with pytest.raises(FrozenInstanceError):
        c.callee = other_fn  # type: ignore
    assert c.callee == some_fn

    assert c.args == ("x", 13)
    with pytest.raises(FrozenInstanceError):
        c.args = ("y", 19)  # type: ignore
    assert c.args == ("x", 13)

    assert c.kwargs == {"foo": 123, "bar": 321}
    with pytest.raises(FrozenInstanceError):
        c.kwargs = {"far": 789, "boo": 987}  # type: ignore
    assert c.kwargs == {"foo": 123, "bar": 321}


def test_tracer_simple() -> None:
    x: list[str] = []

    def foo(y: str) -> None:
        nonlocal x
        x.append(y)

    log = Logger.for_print_fn(foo)

    @log.trace
    def bar() -> str:
        foo("Foo Foo")
        return "Sbrubbles"

    z: str = bar()
    assert z == "Sbrubbles"

    assert x[0] == "Calling test_tracer_simple.<locals>.bar - Args: () - Kwargs: {}."
    assert x[1] == "Foo Foo"
    assert x[2] == "Call on test_tracer_simple.<locals>.bar - returned Sbrubbles."


def test_tracer_raise() -> None:
    x: list[str] = []

    def foo(y: str) -> None:
        nonlocal x
        x.append(y)

    log = Logger.for_print_fn(foo)

    @log.trace
    def bar() -> None:
        foo("Foo Foo")
        raise LocalTestException("Muffles")

    with pytest.raises(LocalTestException, match = "^Muffles$") as z:  # noqa: F841
        bar()

    assert x[0] == "Calling test_tracer_raise.<locals>.bar - Args: () - Kwargs: {}."
    assert x[1] == "Foo Foo"
    assert x[2] == "Call on test_tracer_raise.<locals>.bar - raised Muffles."
