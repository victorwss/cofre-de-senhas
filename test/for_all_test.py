from decorators.for_all import for_all_methods
from typing import Any, Callable, cast, TypeVar
from functools import wraps
from pytest import raises

_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

which: list[str] = []

def the_wrapper(operation: _TRANS) -> _TRANS:

    @wraps(operation)
    def inner(*args: Any, **kwargs: Any) -> Any:
        global which
        try:
            return operation(*args, **kwargs)
        finally:
            which.append(operation.__name__)

    return cast(_TRANS, inner)

def test_simple_wrapped_method():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        def test1(self) -> str:
            return "x"

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    assert f.test1() == "x"
    assert which == ["test1"]

def test_parameter_wrapped_method():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        def test2(self, x: int) -> int:
            return 2 * x

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    assert f.test2(5) == 10
    assert which == ["test2"]

def test_raising_wrapped_method():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        def test3(self) -> None:
            raise ValueError("fooooo")

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    with raises(ValueError, match = "^fooooo$"):
        f.test3()
    assert which == ["test3"]

def test_static_wrapped():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        @staticmethod
        def test4() -> str:
            return "y"

        @property
        def test5(self) -> str:
            return "z"

    global which
    which = []

    assert Foo.test4() == "y"
    assert which == ["test4"]

def test_wrapped_property_get():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        @property
        def test5(self) -> str:
            return "z"

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    assert f.test5 == "z"
    assert which == ["test5"]

def test_wrapped_property_set():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        @property
        def test5(self) -> str:
            assert False

        @test5.setter
        def test5(self, x: str) -> None:
            pass

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    f.test5 = "z"
    assert which == ["test5"]

def test_wrapped_property_del():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        @property
        def test5(self) -> str:
            assert False

        @test5.deleter
        def test5(self) -> None:
            pass

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    del f.test5
    assert which == ["test5"]

def test_was_wrapped_sequence():

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        def test1(self) -> str:
            return "x"

        def test2(self, x: int) -> int:
            return 2 * x

        def test3(self) -> None:
            raise ValueError("fooooo")

        @staticmethod
        def test4() -> str:
            return "y"

        @property
        def test5(self) -> str:
            return "z"

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    assert f.test1() == "x"
    assert which == ["test1"]

    assert f.test2(5) == 10
    assert which == ["test1", "test2"]

    with raises(ValueError, match = "^fooooo$"):
        f.test3()
    assert which == ["test1", "test2", "test3"]

    assert Foo.test4() == "y"
    assert which == ["test1", "test2", "test3", "test4"]

    assert f.test5 == "z"
    assert which == ["test1", "test2", "test3", "test4", "test5"]