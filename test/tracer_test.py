from .context import prepare_imports
prepare_imports()
from decorators.tracer import Call, Logger
import pytest

def some_fn(x: str, y: int) -> float:
    return 42.0

def other_fn(x: str, y: int) -> float:
    return 27.0

def test_call_is_strong_typed() -> None:
    with pytest.raises(BaseException) as xxx1: Call("a", ("x", 13), {"foo": 123, "bar": 321})
    with pytest.raises(BaseException) as xxx2: Call(some_fn, "xxx", {"foo": 123, "bar": 321})
    with pytest.raises(BaseException) as xxx3: Call(some_fn, ("x", 13), "xxx")

def test_call_is_immutable() -> None:
    c = Call(some_fn, ("x", 13), {"foo": 123, "bar": 321})

    assert c.callee == some_fn
    with pytest.raises(BaseException) as xxx1: c.callee = other_fn
    assert c.callee == some_fn

    assert c.args == ("x", 13)
    with pytest.raises(BaseException) as xxx2: c.args = ("y", 19)
    assert c.args == ("x", 13)

    assert c.kwargs == {"foo": 123, "bar": 321}
    with pytest.raises(BaseException) as xxx3: c.kwargs = {"far": 789, "boo": 987}
    assert c.kwargs == {"foo": 123, "bar": 321}

def test_tracer_simple():
    x = []
    def foo(y):
        global x
        x += y

    log = Logger.for_print_fn(foo)

    @log.trace
    def bar():
        foo("Foo Foo")
        return "Sbrubbles"

    bar()

    assert x[0] == "Calling test_tracer.<locals>.bar - Args: () - Kwargs: {}."
    assert x[1] == "Foo Foo"
    assert x[2] == "Call on test_tracer.<locals>.bar - returned Sbrubbles."

def test_tracer_raise():
    x = []
    def foo(y):
        global x
        x += y

    log = Logger.for_print_fn(foo)

    @log.trace
    def bar():
        raise Exception("Muffles")

    bar()

    assert x[0] == "Calling test_tracer.<locals>.bar - Args: () - Kwargs: {}."
    assert x[1] == "Foo Foo"
    assert x[2] == "Call on test_tracer.<locals>.bar - raised Muffles."