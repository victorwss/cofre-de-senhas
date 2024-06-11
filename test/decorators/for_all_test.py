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


def test_simple_wrapped_method() -> None:

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


def test_parameter_wrapped_method() -> None:

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


def test_raising_wrapped_method() -> None:

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


def test_static_wrapped() -> None:

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


def test_wrapped_property_get() -> None:

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


def test_wrapped_property_set() -> None:

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


def test_wrapped_property_set_no_get() -> None:

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        def test5(self, x: str) -> None:
            pass

        test5 = property().setter(test5)  # type: ignore

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    f.test5 = "z"  # type: ignore
    assert which == ["test5"]


def test_wrapped_property_del() -> None:

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


def test_wrapped_property_del_no_get() -> None:

    @for_all_methods(the_wrapper)
    class Foo:

        def __init__(self) -> None:
            pass

        def test5(self) -> None:
            pass

        test5 = property().deleter(test5)  # type: ignore

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    del f.test5
    assert which == ["test5"]


def test_wrapped_dunders() -> None:

    @for_all_methods(the_wrapper, even_dunders = True)
    class Foo:

        def __init__(self) -> None:
            pass

        def __str__(self) -> str:
            return "x"

        def __foofoo__(self) -> str:
            return "x"

    global which
    which = []

    f: Foo = Foo()
    assert which == ["__new__", "__init__"]

    f"{f}"
    assert which == ["__new__", "__init__", "__str__", "__format__"]

    f.__foofoo__()
    assert which == ["__new__", "__init__", "__str__", "__format__", "__getattribute__", "__foofoo__"]


def test_was_wrapped_sequence() -> None:

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

        @test5.setter
        def test5(self, v: str) -> None:
            pass

        @test5.deleter
        def test5(self) -> None:
            pass

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

    f.test5 = "u"
    assert which == ["test1", "test2", "test3", "test4", "test5", "test5"]

    del f.test5
    assert which == ["test1", "test2", "test3", "test4", "test5", "test5", "test5"]


def test_was_wrapped_sequence_with_dunders() -> None:

    @for_all_methods(the_wrapper, even_dunders = True)
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

        @test5.setter
        def test5(self, v: str) -> None:
            pass

        @test5.deleter
        def test5(self) -> None:
            pass

        def __str__(self) -> str:
            return "x"

        def __test6__(self) -> str:
            return "x"

        def test7__(self) -> str:
            return "x"

        @property
        def test8__(self) -> str:
            return "x"

    r: list[str] = [
        "__new__", "__init__", "__getattribute__", "test1", "__getattribute__", "test2", "__getattribute__", "test3",
        "test4", "test5", "__getattribute__", "test5", "__setattr__", "test5", "__delattr__", "__str__",
        "__format__", "__getattribute__", "__test6__", "__getattribute__", "test7__", "test8__", "__getattribute__"
    ]

    global which
    which = []

    f: Foo = Foo()
    assert which == r[:2]

    assert f.test1() == "x"
    assert which == r[:4]

    assert f.test2(5) == 10
    assert which == r[:6]

    with raises(ValueError, match = "^fooooo$"):
        f.test3()
    assert which == r[:8]

    assert Foo.test4() == "y"
    assert which == r[:9]

    assert f.test5 == "z"
    assert which == r[:11]

    f.test5 = "u"
    assert which == r[:13]

    del f.test5
    assert which == r[:15]

    f"{f}"
    assert which == r[:17]

    assert "x" == f.__test6__()
    assert which == r[:19]

    assert "x" == f.test7__()
    assert which == r[:21]

    assert "x" == f.test8__
    assert which == r


def test_was_wrapped_sequence_without_dunders() -> None:

    @for_all_methods(the_wrapper, even_dunders = False)
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

        @test5.setter
        def test5(self, v: str) -> None:
            pass

        @test5.deleter
        def test5(self) -> None:
            pass

        def __str__(self) -> str:
            return "x"

        def __test6__(self) -> str:
            return "x"

        def test7__(self) -> str:
            return "x"

        @property
        def test8__(self) -> str:
            return "x"

    r: list[str] = ["test1", "test2", "test3", "test4", "test5", "test5", "test5", "test7__", "test8__"]

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    assert f.test1() == "x"
    assert which == r[:1]

    assert f.test2(5) == 10
    assert which == r[:2]

    with raises(ValueError, match = "^fooooo$"):
        f.test3()
    assert which == r[:3]

    assert Foo.test4() == "y"
    assert which == r[:4]

    assert f.test5 == "z"
    assert which == r[:5]

    f.test5 = "u"
    assert which == r[:6]

    del f.test5
    assert which == r[:7]

    f"{f}"
    assert which == r[:7]

    assert "x" == f.__test6__()
    assert which == r[:7]

    assert "x" == f.test7__()
    assert which == r[:8]

    assert "x" == f.test8__
    assert which == r


def test_dunders_privates() -> None:

    @for_all_methods(the_wrapper, even_dunders = True, even_privates = True)
    class Foo:

        def __test1(self) -> str:
            return "a"

        def __test2__(self) -> str:
            return "b"

        @property
        def __test3(self) -> str:
            return "c"

        @property
        def __test4__(self) -> str:
            return "d"

        def work(self) -> str:
            return self.__test1() + self.__test2__() + self.__test3 + self.__test4__

    global which
    which = []

    f: Foo = Foo()
    assert which == ["__new__", "__init__"]

    assert "abcd" == f.work()
    assert [i for i in which if i != "__getattribute__"] == ["__new__", "__init__", "__test1", "__test2__", "__test3", "__test4__", "work"]


def test_dunders_no_privates() -> None:

    @for_all_methods(the_wrapper, even_dunders = True, even_privates = False)
    class Foo:

        def __test1(self) -> str:
            return "a"

        def __test2__(self) -> str:
            return "b"

        @property
        def __test3(self) -> str:
            return "c"

        @property
        def __test4__(self) -> str:
            return "d"

        def work(self) -> str:
            return self.__test1() + self.__test2__() + self.__test3 + self.__test4__

    global which
    which = []

    f: Foo = Foo()
    assert which == ["__new__", "__init__"]

    assert "abcd" == f.work()
    assert [i for i in which if i != "__getattribute__"] == ["__new__", "__init__", "__test2__", "__test4__", "work"]


def test_no_dunders_privates() -> None:

    @for_all_methods(the_wrapper, even_dunders = False, even_privates = True)
    class Foo:

        def __test1(self) -> str:
            return "a"

        def __test2__(self) -> str:
            return "b"

        @property
        def __test3(self) -> str:
            return "c"

        @property
        def __test4__(self) -> str:
            return "d"

        def work(self) -> str:
            return self.__test1() + self.__test2__() + self.__test3 + self.__test4__

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    assert "abcd" == f.work()
    assert which == ["__test1", "__test3", "work"]


def test_no_dunders_no_privates() -> None:

    @for_all_methods(the_wrapper, even_dunders = False, even_privates = False)
    class Foo:

        def __test1(self) -> str:
            return "a"

        def __test2__(self) -> str:
            return "b"

        @property
        def __test3(self) -> str:
            return "c"

        @property
        def __test4__(self) -> str:
            return "d"

        def work(self) -> str:
            return self.__test1() + self.__test2__() + self.__test3 + self.__test4__

    global which
    which = []

    f: Foo = Foo()
    assert which == []

    assert "abcd" == f.work()
    assert which == ["work"]


def test_for_subclasses() -> None:

    class Super:

        def test1(self) -> None:
            pass

        def __test2__(self) -> None:
            pass

        def __test3(self) -> None:
            pass

        def test4(self) -> None:
            self.__test3()

        @property
        def test5(self) -> str:
            return "x"

        @property
        def __test6(self) -> str:
            return "x"

        @property
        def test7(self) -> str:
            return self.__test6

    @for_all_methods(the_wrapper, even_dunders = True, even_privates = True)
    class Sub(Super):
        pass

    r: list[str] = ["__new__", "__init__", "test1", "__test2__", "__test3", "test4", "test5", "__test6", "test7"]

    global which
    which = []

    f: Sub = Sub()
    assert [i for i in which if i != "__getattribute__"] == r[:2]

    f.test1()
    assert [i for i in which if i != "__getattribute__"] == r[:3]

    f.__test2__()
    assert [i for i in which if i != "__getattribute__"] == r[:4]

    f.test4()
    assert [i for i in which if i != "__getattribute__"] == r[:6]

    assert "x" == f.test5
    assert [i for i in which if i != "__getattribute__"] == r[:7]

    assert "x" == f.test7
    assert [i for i in which if i != "__getattribute__"] == r
