from validator import TypeValidationError, dataclass_validate
from dataclasses import dataclass
from typing import Any, Callable
import pytest

@dataclass_validate
@dataclass(frozen = True)
class Simple:
    x1: str

def test_simple_1() -> None:
    t1: Simple = Simple("a")
    assert t1.x1 == "a"

def test_simple_2() -> None:
    with pytest.raises(TypeValidationError):
        Simple(123)

@dataclass_validate
@dataclass(frozen = True)
class United:
    x1: str | int

def test_united_1() -> None:
    t1: United = United("a")
    assert t1.x1 == "a"

def test_united_2() -> None:
    t1: United = United(123)
    assert t1.x1 == 123

def test_united_3() -> None:
    with pytest.raises(TypeValidationError):
        United(123.567)

@dataclass_validate
@dataclass(frozen = True)
class Tupled:
    x1: tuple[str, int, float, str]

def test_tupled_1() -> None:
    t1: Tupled = Tupled(("a", 5, 3.3, "b"))
    assert t1.x1[0] == "a"
    assert t1.x1[1] == 5
    assert t1.x1[2] == 3.3
    assert t1.x1[3] == "b"
    assert len(t1.x1) == 4

def test_tupled_2() -> None:
    with pytest.raises(TypeValidationError):
        Tupled(("a", 5, 3.3))

def test_tupled_3() -> None:
    with pytest.raises(TypeValidationError):
        Tupled(("a", 5, 3.3, "b", "x"))

def test_tupled_4() -> None:
    with pytest.raises(TypeValidationError):
        Tupled(("a", 5, 3.3, 4))

def test_tupled_5() -> None:
    with pytest.raises(TypeValidationError):
        Tupled(())

def test_tupled_6() -> None:
    with pytest.raises(TypeValidationError):
        Tupled("xxx")

@dataclass_validate
@dataclass(frozen = True)
class TupledCont:
    x1: tuple[str, int, float, str, ...] # Invalid type! Should always fail!

def test_tupled_cont_1() -> None:
    with pytest.raises(TypeValidationError):
        t1: TupledCont = TupledCont(("a", 5, 3.3, "b"))

def test_tupled_cont_2() -> None:
    with pytest.raises(TypeValidationError):
        TupledCont(("a", 5, 3.3))

def test_tupled_cont_3() -> None:
    with pytest.raises(TypeValidationError):
        t1: TupledCont = TupledCont(("a", 5, 3.3, "b", "x"))

def test_tupled_cont_4() -> None:
    with pytest.raises(TypeValidationError):
        TupledCont(("a", 5, 3.3, 4))

def test_tupled_cont_5() -> None:
    with pytest.raises(TypeValidationError):
        TupledCont(("a", 5, 3.3, "x", 5))

def test_tupled_cont_6() -> None:
    with pytest.raises(TypeValidationError):
        TupledCont(())

def test_tupled_cont_7() -> None:
    with pytest.raises(TypeValidationError):
        TupledCont("xxx")

@dataclass_validate
@dataclass(frozen = True)
class BadTupledEllipsis:
    x1: tuple[...] # Invalid type! Should always fail!

def test_bad_tupled_ellipsis_1() -> None:
    with pytest.raises(TypeValidationError):
        BadTupledEllipsis(())

def test_bad_tupled_ellipsis_2() -> None:
    with pytest.raises(TypeValidationError):
        BadTupledEllipsis(("a", ))

def test_bad_tupled_ellipsis_3() -> None:
    with pytest.raises(TypeValidationError):
        BadTupledEllipsis(("a", 5))

def test_bad_tupled_ellipsis_4() -> None:
    with pytest.raises(TypeValidationError):
        BadTupledEllipsis("xxx")

@dataclass_validate
@dataclass(frozen = True)
class TupledEllipsis:
    x1: tuple[str | int, ...]

def test_tupled_ellipsis_1() -> None:
    t1: TupledEllipsis = TupledEllipsis(())
    assert len(t1.x1) == 0

def test_tupled_ellipsis_2() -> None:
    t1: TupledEllipsis = TupledEllipsis(("a", ))
    assert t1.x1[0] == "a"
    assert len(t1.x1) == 1

def test_tupled_ellipsis_3() -> None:
    t1: TupledEllipsis = TupledEllipsis(("a", 5))
    assert t1.x1[0] == "a"
    assert t1.x1[1] == 5
    assert len(t1.x1) == 2

def test_tupled_ellipsis_4() -> None:
    t1: TupledEllipsis = TupledEllipsis((8, "a", 5, "x"))
    assert t1.x1[0] == 8
    assert t1.x1[1] == "a"
    assert t1.x1[2] == 5
    assert t1.x1[3] == "x"
    assert len(t1.x1) == 4

def test_tupled_ellipsis_5() -> None:
    t1: TupledEllipsis = TupledEllipsis((1, 2, 3))
    assert t1.x1[0] == 1
    assert t1.x1[1] == 2
    assert t1.x1[2] == 3
    assert len(t1.x1) == 3

def test_tupled_ellipsis_6() -> None:
    with pytest.raises(TypeValidationError):
        TupledEllipsis("xxx")

def test_tupled_ellipsis_7() -> None:
    with pytest.raises(TypeValidationError):
        TupledEllipsis((6.66, ))

def test_tupled_ellipsis_8() -> None:
    with pytest.raises(TypeValidationError):
        TupledEllipsis((1, 2, 3, 6.66))

@dataclass_validate
@dataclass(frozen = True)
class TupledEmpty:
    x1: tuple[()]

def test_tupled_empty_1() -> None:
    t1: TupledEmpty = TupledEmpty(())
    assert len(t1.x1) == 0

def test_tupled_empty_2() -> None:
    with pytest.raises(TypeValidationError):
        TupledEmpty(("a", ))

def test_tupled_empty_3() -> None:
    with pytest.raises(TypeValidationError):
        TupledEmpty(("a", "x"))

def test_tupled_empty_4() -> None:
    with pytest.raises(TypeValidationError):
        TupledEmpty(("a", 789))

def test_tupled_empty_5() -> None:
    with pytest.raises(TypeValidationError):
        TupledEmpty("xxx")

@dataclass_validate
@dataclass(frozen = True)
class HasDict:
    x1: dict[float, float]

def test_hasdict_1() -> None:
    t1: HasDict = HasDict({3.5: 7.8, 4.4: 3.9})
    assert t1.x1[3.5] == 7.8
    assert t1.x1[4.4] == 3.9
    assert len(t1.x1) == 2

def test_hasdict_2() -> None:
    t1: HasDict = HasDict({})
    assert len(t1.x1) == 0

def test_hasdict_3() -> None:
    with pytest.raises(TypeValidationError):
        HasDict({"a": 3.3})

def test_hasdict_4() -> None:
    with pytest.raises(TypeValidationError):
        HasDict({3.3: "x"})

def test_hasdict_5() -> None:
    with pytest.raises(TypeValidationError):
        HasDict("xxx")

@dataclass_validate
@dataclass(frozen = True)
class BadDict1:
    x1: dict[str, float, int] # Invalid type! Should always fail!

def test_bad_dict1_1() -> None:
    with pytest.raises(TypeValidationError):
        BadDict1({})

def test_bad_dict1_2() -> None:
    with pytest.raises(TypeValidationError):
        BadDict1("xxx")

@dataclass_validate
@dataclass(frozen = True)
class BadDict2:
    x1: dict[str] # Invalid type! Should always fail!

def test_bad_dict2_1() -> None:
    with pytest.raises(TypeValidationError):
        BadDict2({})

def test_bad_dict2_2() -> None:
    with pytest.raises(TypeValidationError):
        BadDict1("xxx")

@dataclass_validate
@dataclass(frozen = True)
class HasList:
    x1: list[float]

def test_haslist_1() -> None:
    t1: HasList = HasList([3.5, 7.8])
    assert t1.x1[0] == 3.5
    assert t1.x1[1] == 7.8
    assert len(t1.x1) == 2

def test_haslist_2() -> None:
    t1: HasList = HasList([])
    assert len(t1.x1) == 0

def test_haslist_3() -> None:
    with pytest.raises(TypeValidationError):
        HasList(["a", 3.3])

def test_haslist_4() -> None:
    with pytest.raises(TypeValidationError):
        HasList([3.3, "x"])

def test_haslist_5() -> None:
    with pytest.raises(TypeValidationError):
        HasList("xxx")

@dataclass_validate
@dataclass(frozen = True)
class HasCall1:
    x1: Callable[[float, int], str]

@dataclass_validate
@dataclass(frozen = True)
class HasCall2:
    x1: Callable[[str, int, int], str]

@dataclass_validate
@dataclass(frozen = True)
class HasCall3:
    x1: Callable[[...], str]

def test_hascall_1() -> None:
    def u(x: float, y: int) -> str:
        return "z"

    t1: HasCall1 = HasCall1(u)
    assert t1.x1 == u

def test_hascall_2() -> None:
    def u(x: float, y: int) -> int:
        return 6
    with pytest.raises(TypeValidationError):
        HasCall1(u)

def test_hascall_3() -> None:
    def u(x: str, y: int) -> str:
        return "z"
    with pytest.raises(TypeValidationError):
        HasCall1(u)

def test_hascall_4() -> None:
    def u(x: str) -> str:
        return "z"
    with pytest.raises(TypeValidationError):
        HasCall1(u)

def test_hascall_5() -> None:
    def u(x: float, y: int, w: int) -> str:
        return "z"
    with pytest.raises(TypeValidationError):
        HasCall1(u)

def test_hascall_6() -> None:
    def u(x: str, y: int, z: int) -> str:
        return "z"

    t1: HasCall2 = HasCall2(u)
    assert t1.x1 == u

def test_hascall_7() -> None:
    def u(x: str, y: int) -> str:
        return "z"

    with pytest.raises(TypeValidationError):
        HasCall2(u)

def test_hascall_8() -> None:
    def u(x: str, y: int) -> str:
        return "z"

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u

def test_hascall_8() -> None:
    def u(x: str, y: int, z: float) -> str:
        return "z"

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u

def test_hascall_9() -> None:
    def u() -> str:
        return "z"

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u

def test_hascall_10() -> None:
    def u() -> int:
        return "z"

    with pytest.raises(TypeValidationError):
        HasCall3(u)

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

def test_instantiation_works_1() -> None:
    t1: SomeClass = SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, pytest, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)
    assert t1.x1 == "a"
    assert t1.x2 == 123
    assert t1.x3 == "e"
    assert t1.x4 == ("a", 5, 7.7)
    assert t1.x5 is _foo_1
    assert t1.x6 is pytest
    assert t1.x7 == "ss"
    assert t1.x8 == _foo_2
    assert t1.x9 == ("1", "2", "3", "4", "5")
    assert t1.x10 == _foo_3

def test_instantiation_works_2() -> None:
    t1: SomeClass = SomeClass("a", 123, 777, ("a", 5, 7.7), _foo_1, None, None, _foo_2, ("1", "2"), _foo_3)
    assert t1.x1 == "a"
    assert t1.x2 == 123
    assert t1.x3 == 777
    assert t1.x4 == ("a", 5, 7.7)
    assert t1.x5 is _foo_1
    assert t1.x6 is None
    assert t1.x7 is None
    assert t1.x8 == _foo_2
    assert t1.x9 == ("1", "2")
    assert t1.x10 == _foo_3

def test_validation_is_strong_typed_1() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass(123, 123, "e", ("a", 5, 7.7), _foo_1, pytest, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)

def test_validation_is_strong_typed_2() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", "b", "e", ("a", 5, 7.7), _foo_1, pytest, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)

def test_validation_is_strong_typed_3() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, _foo_2, ("a", 5, 7.7), _foo_1, pytest, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)

def test_validation_is_strong_typed_4() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, "e", _foo_1, _foo_1, pytest, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)

def test_validation_is_strong_typed_5() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_2, pytest, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3)

def test_validation_is_strong_typed_7() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, pytest, 123, _foo_2, ("1", "2", "3", "4", "5"), _foo_3)

def test_validation_is_strong_typed_8() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, pytest, "ss", "x", ("1", "2", "3", "4", "5"), _foo_3)

def test_validation_is_strong_typed_9a() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, pytest, "ss", _foo_2, 444, _foo_3)

def test_validation_is_strong_typed_9b() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, pytest, "ss", _foo_2, (444, ), _foo_3)

def test_validation_is_strong_typed_10() -> None:
    with pytest.raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, pytest, "ss", _foo_2, ("1", "2", "3", "4", "5"), "x")
