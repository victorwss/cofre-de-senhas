from validator import TypeValidationError, dataclass_validate, dataclass_validate_local
from dataclasses import dataclass
from typing import Any, Callable, List, Literal
from pytest import raises


def test_simple_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Simple:
        x1: str

    t1: Simple = Simple("a")
    assert t1.x1 == "a"


def test_simple_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Simple:
        x1: str

    with raises(TypeValidationError):
        Simple(123)  # type: ignore


def test_united_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class United:
        x1: str | int

    t1: United = United("a")
    assert t1.x1 == "a"


def test_united_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class United:
        x1: str | int

    t1: United = United(123)
    assert t1.x1 == 123


def test_united_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class United:
        x1: str | int

    with raises(TypeValidationError):
        United(123.567)  # type: ignore


def test_united_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class UnitedAlias:
        x1: "str | int"

    t1: UnitedAlias = UnitedAlias("a")
    assert t1.x1 == "a"

    t2: UnitedAlias = UnitedAlias(123)
    assert t2.x1 == 123

    with raises(TypeValidationError):
        UnitedAlias(123.567)  # type: ignore


def test_united_6() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class UnitedAliasBad:
            x1: "xxx | yyy"  # type: ignore  # noqa: F821


def test_instantiation_works() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class SomeClass:
        x1: str
        x2: int
        x3: int | str
        x4: tuple[str, int, float]
        x5: list[str]
        x6: Any
        x7: str | None
        x8: dict[str, str]
        x9: tuple[str, ...]
        x10: Callable[[str, float], int]

    _foo_1: list[str] = ["a", "b"]
    _foo_2: dict[str, str] = {"a": "b", "c": "d"}

    def _foo_3(a: str, b: float) -> int:
        return 42

    t1: SomeClass = SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)
    assert t1.x1 == "a"
    assert t1.x2 == 123
    assert t1.x3 == "e"
    assert t1.x4 == ("a", 5, 7.7)
    assert t1.x5 is _foo_1
    assert t1.x6 is raises
    assert t1.x7 == "ss"
    assert t1.x8 == _foo_2
    assert t1.x9 == ("1", "2", "3", "4", "5")
    assert t1.x10 == _foo_3

    t2: SomeClass = SomeClass("a", 123, 777, ("a", 5, 7.7), _foo_1, None, None, _foo_2, ("1", "2"), _foo_3)
    assert t2.x1 == "a"
    assert t2.x2 == 123
    assert t2.x3 == 777
    assert t2.x4 == ("a", 5, 7.7)
    assert t2.x5 is _foo_1
    assert t2.x6 is None
    assert t2.x7 is None
    assert t2.x8 == _foo_2
    assert t2.x9 == ("1", "2")
    assert t2.x10 == _foo_3


def test_validation_is_strong_typed() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class SomeClass:
        x1: str
        x2: int
        x3: int | str
        x4: tuple[str, int, float]
        x5: list[str]
        x6: Any
        x7: str | None
        x8: dict[str, str]
        x9: tuple[str, ...]
        x10: Callable[[str, float], int]

    _foo_1: list[str] = ["a", "b"]
    _foo_2: dict[str, str] = {"a": "b", "c": "d"}

    def _foo_3(a: str, b: float) -> int:
        return 42

    with raises(TypeValidationError):
        SomeClass(123, 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", "b", "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, _foo_2, ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, "e", _foo_1, _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_2, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, 123, _foo_2, ("1", "2", "3", "4", "5"), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", "x", ("1", "2", "3", "4", "5"), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, 444, _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, (444, ), _foo_3)  # type: ignore

    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), "x")  # type: ignore


def test_with_string_typed() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class WithString:
        z: "int"

    a: WithString = WithString(4)
    assert a.z == 4


def test_with_string_self_typed() -> None:
    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class SelfRef:
        z: "SelfRef | None"

    a: SelfRef = SelfRef(None)
    assert a.z is None
    b: SelfRef = SelfRef(a)
    assert b.z == a


def test_circular_ok() -> None:
    # @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Circular1:
        og: "Circular2 | None"

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Circular2:
        og: "Circular1"

    Circular1 = dataclass_validate_local(locals())(Circular1)  # type: ignore

    a: Circular1 = Circular1(None)
    b: Circular2 = Circular2(a)
    c: Circular1 = Circular1(b)

    assert c.og == b
    assert b.og == a
    assert a.og is None


def test_circular_bad() -> None:
    # @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Circular1:
        og: "Circular2 | None"

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Circular2:
        og: "Circular1"

    Circular1 = dataclass_validate_local(locals())(Circular1)  # type: ignore

    with raises(TypeValidationError):
        Circular1("foo")  # type: ignore

    with raises(TypeValidationError):
        Circular2("foo")  # type: ignore

    a: Circular1 = Circular1(None)
    b: Circular2 = Circular2(a)

    with raises(TypeValidationError):
        Circular1(a)  # type: ignore

    with raises(TypeValidationError):
        Circular2(b)  # type: ignore


def test_crazy_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Crazy1:
        x1: int

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Crazy2:
        x1: List[Crazy1]

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Crazy3:
        x1: "List[Crazy2]"

    a: Crazy1 = Crazy1(5)
    b: Crazy1 = Crazy1(8)
    c: Crazy1 = Crazy1(4)
    d: Crazy2 = Crazy2([a, b, c])
    e: Crazy2 = Crazy2([b, c])
    f: Crazy3 = Crazy3([d, e])

    assert a.x1 == 5
    assert b.x1 == 8
    assert c.x1 == 4
    assert d.x1 == [a, b, c]
    assert e.x1 == [b, c]
    assert f.x1 == [d, e]


def test_crazy_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Crazy1:
        x1: int

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Crazy2:
        x1: List[Crazy1]

    with raises(TypeValidationError):
        Crazy2(5)  # type: ignore


def test_crazy_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Crazy1:
        x1: int

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Crazy2:
        x1: List[Crazy1]

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Crazy3:
        x1: "List[Crazy2]"

    with raises(TypeValidationError):
        Crazy3(Crazy1(5))  # type: ignore


def test_crazy_4() -> None:
    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class Crazy4:
        x1: List["Crazy4"]

    a: Crazy4 = Crazy4([])
    b: Crazy4 = Crazy4([a])
    c: Crazy4 = Crazy4([a, b, a])
    d: Crazy4 = Crazy4([c, b, a, b, c])
    e: Crazy4 = Crazy4([d, b, a, c, d, a, c])


def test_bad_crap() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadCrap:
            # Invalid type! Should always fail!
            x1: "compile error"  # type: ignore  # noqa: F722


def test_post_init() -> None:
    z: HasPostInit1 | None = None  # noqa: F821

    @dataclass_validate
    @dataclass(frozen = True)
    class HasPostInit1:
        x1: int

        def __post_init__(self) -> None:
            assert self.x1 == 1
            nonlocal z
            z = self

    x: HasPostInit1 = HasPostInit1(1)
    assert x is z


def test_post_init_invalid() -> None:
    z: HasPostInit2 | None = None  # noqa: F821

    @dataclass_validate
    @dataclass(frozen = True)
    class HasPostInit2:
        x1: str

        def __post_init__(self) -> None:
            assert self.x1 == 1  # type: ignore
            nonlocal z
            z = self

    with raises(TypeValidationError):
        HasPostInit2(1)  # type: ignore
    assert z.x1 == 1  # type: ignore


def test_post_validate() -> None:
    z: HasPostInit3 | None = None  # noqa: F821
    y: HasPostInit3 | None = None  # noqa: F821

    @dataclass_validate
    @dataclass(frozen = True)
    class HasPostInit3:
        x1: int

        def __post_init__(self) -> None:
            assert self.x1 == 1
            nonlocal z
            z = self

        def __post_type_validate__(self) -> None:
            nonlocal z, y
            assert z is self
            assert y is None
            y = self

    x: HasPostInit3 = HasPostInit3(1)
    assert x is z
    assert y is z


def test_post_validate_invalid() -> None:
    z: HasPostInit4 | None = None  # noqa: F821

    @dataclass_validate
    @dataclass(frozen = True)
    class HasPostInit4:
        x1: str

        def __post_init__(self) -> None:
            assert self.x1 == 1  # type: ignore
            nonlocal z
            z = self

        def __post_type_validate__(self) -> None:
            assert False

    with raises(TypeValidationError):
        HasPostInit4(1)  # type: ignore
    assert z.x1 == 1  # type: ignore


def test_non_local_1() -> None:

    import uuid

    @dataclass_validate
    @dataclass(frozen = True)
    class NonLocal1:
        x1: uuid.UUID

    x: uuid.UUID = uuid.UUID("12345678123456781234567812345678")
    y: NonLocal1 = NonLocal1(x)
    assert y.x1 is x


def test_non_local_2a() -> None:

    import uuid

    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class NonLocal2:
            x1: "uuid.UUID"


def test_non_local_2b() -> None:

    import uuid

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class NonLocal2:
        x1: "uuid.UUID"

    x: uuid.UUID = uuid.UUID("12345678123456781234567812345678")
    y: NonLocal2 = NonLocal2(x)
    assert y.x1 is x


def test_non_local_3() -> None:

    from uuid import UUID as Sbrubbles

    @dataclass_validate
    @dataclass(frozen = True)
    class NonLocal3:
        x1: Sbrubbles

    x: Sbrubbles = Sbrubbles("12345678123456781234567812345678")
    y: NonLocal3 = NonLocal3(x)
    assert y.x1 is x


def test_non_local_4a() -> None:

    from uuid import UUID as Sbrubbles

    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class NonLocal4:
            x1: "Sbrubbles"


def test_non_local_4b() -> None:

    from uuid import UUID as Sbrubbles

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class NonLocal4:
        x1: "Sbrubbles"

    x: Sbrubbles = Sbrubbles("12345678123456781234567812345678")
    y: NonLocal4 = NonLocal4(x)
    assert y.x1 is x


def test_non_local_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Crazy1:
        x1: int

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class NonLocal5:
        x1: "Crazy1"

    x: Crazy1 = Crazy1(4)
    y: NonLocal5 = NonLocal5(x)
    assert y.x1 is x


def test_non_local_6a() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Crazy1:
        x1: int

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class NonLocal6A:
        x1: "Crazy1"

    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class NonLocal6B:
            x1: "NonLocal6A"


def test_non_local_6b() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Crazy1:
        x1: int

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class NonLocal6A:
        x1: "Crazy1"

    @dataclass_validate_local(locals())
    @dataclass(frozen = True)
    class NonLocal6B:
        x1: "NonLocal6A"

    x: Crazy1 = Crazy1(4)
    y: NonLocal6A = NonLocal6A(x)
    z: NonLocal6B = NonLocal6B(y)
    assert z.x1 is y


def test_literal_1() -> None:

    @dataclass_validate
    @dataclass(frozen = True)
    class HasLiteral1:
        x1: Literal[5]

    x: HasLiteral1 = HasLiteral1(5)
    assert x.x1 == 5


def test_literal_2() -> None:

    @dataclass_validate
    @dataclass(frozen = True)
    class HasLiteral2:
        x1: Literal[5]

    with raises(TypeValidationError):
        HasLiteral2(7)  # type: ignore


def test_literal_3() -> None:
    z: int = 5 if 1 < 2 else 7

    @dataclass_validate
    @dataclass(frozen = True)
    class HasLiteral3:
        x1: Literal[5]

    x: HasLiteral3 = HasLiteral3(z)  # type: ignore
    assert x.x1 == 5


def test_bad_ellipsis() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadEllipsis:
            # Invalid type! Should always fail!
            x1: ...  # type: ignore


def test_bad_alias() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadAlias:
            # Invalid type! Should always fail!
            x1: "List[mumble]"  # type: ignore  # noqa: F821
