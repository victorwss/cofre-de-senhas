from .context import tracer
from tracer import Call, Logger

def assert_error(which: type[BaseException], where: Callable[[], None]) -> None:
    try:
        where()
        assert False
    except as x:
        assert type(x) == which

def some_fn(x: str, y: int) -> float:
    return 42.0

def other_fn(x: str, y: int) -> float:
    return 27.0

def test_call_is_strong_typed() -> None:
    assert_error(BaseException, lambda: Call("a", ("x", 13), {"foo": 123, "bar": 321}))
    assert_error(BaseException, lambda: Call(some_fn, "xxx", {"foo": 123, "bar": 321}))
    assert_error(BaseException, lambda: Call(some_fn, ("x", 13), "xxx")

def test_call_is_immutable() -> None:
    c = Call(some_fn, ("x", 13), {"foo": 123, "bar": 321})

    assert c.caller == some_fn
    assert_error(BaseException, lambda: c.caller = other_fn)
    assert c.caller == some_fn

    assert c.args == ("x", 13)
    assert_error(BaseException, lambda: c.args = ("y", 19))
    assert c.args == ("x", 13)

    assert c.kwargs == {"foo": 123, "bar": 321}
    assert_error(BaseException, lambda: c.kwargs = {"far": 789, "boo": 987})
    assert c.kwargs == {"foo": 123, "bar": 321}