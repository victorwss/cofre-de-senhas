from validator import TypeValidationError, dataclass_validate
from dataclasses import dataclass
from typing import Dict, TypedDict
from pytest import raises


def test_hasdict1_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict1:
        x1: dict[float, float]

    t1: HasDict1 = HasDict1({3.5: 7.8, 4.4: 3.9})
    assert t1.x1 == {3.5: 7.8, 4.4: 3.9}


def test_hasdict1_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict1:
        x1: dict[float, float]

    t1: HasDict1 = HasDict1({})
    assert t1.x1 == {}


def test_hasdict1_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict1:
        x1: dict[float, float]

    with raises(TypeValidationError):
        HasDict1({"a": 3.3})  # type: ignore


def test_hasdict1_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict1:
        x1: dict[float, float]

    with raises(TypeValidationError):
        HasDict1({3.3: "x"})  # type: ignore


def test_hasdict1_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict1:
        x1: dict[float, float]

    with raises(TypeValidationError):
        HasDict1("xxx")  # type: ignore


def test_hasdict1_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict1:
        x1: dict[float, float]

    with raises(TypeValidationError):
        HasDict1([])  # type: ignore


def test_hasdict2_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict2:
        x1: Dict[float, float]

    t1: HasDict2 = HasDict2({3.5: 7.8, 4.4: 3.9})
    assert t1.x1 == {3.5: 7.8, 4.4: 3.9}


def test_hasdict2_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict2:
        x1: Dict[float, float]

    t1: HasDict2 = HasDict2({})
    assert t1.x1 == {}


def test_hasdict2_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict2:
        x1: Dict[float, float]

    with raises(TypeValidationError):
        HasDict2({"a": 3.3})  # type: ignore


def test_hasdict2_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict2:
        x1: Dict[float, float]

    with raises(TypeValidationError):
        HasDict2({3.3: "x"})  # type: ignore


def test_hasdict2_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict2:
        x1: Dict[float, float]

    with raises(TypeValidationError):
        HasDict2("xxx")  # type: ignore


def test_hasdict2_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict2:
        x1: Dict[float, float]

    with raises(TypeValidationError):
        HasDict2([])  # type: ignore


class SomeTyped(TypedDict):
    bla: str
    gua: float
    ta: int


def test_hasdict3_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict3:
        x1: SomeTyped

    t1: HasDict3 = HasDict3({"bla": "xx", "gua": 3.9, "ta": 6})
    assert [t1.x1["bla"], t1.x1["gua"], t1.x1["ta"]] == ["xx", 3.9, 6]
    assert len(t1.x1) == 3


def test_hasdict3_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict3:
        x1: SomeTyped

    with raises(TypeValidationError):
        HasDict3({})  # type: ignore


def test_hasdict3_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict3:
        x1: SomeTyped

    with raises(TypeValidationError):
        HasDict3({"hjhk": 555})  # type: ignore


def test_hasdict3_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict3:
        x1: SomeTyped

    with raises(TypeValidationError):
        HasDict3({"bla": "xx", "ta": 6})  # type: ignore


def test_hasdict3_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict3:
        x1: SomeTyped

    with raises(TypeValidationError):
        HasDict3({"bla": "xx", "gua": 3.9, "ta": 6, "jjjj": 4568})  # type: ignore


def test_hasdict3_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict3:
        x1: SomeTyped

    with raises(TypeValidationError):
        HasDict3({"bla": 5, "gua": 3.9, "ta": 6})  # type: ignore


def test_hasdict3_7() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasDict3:
        x1: SomeTyped

    with raises(TypeValidationError):
        HasDict3({"bla": "xx", "gua": 3.9, "ta": "6"})  # type: ignore


def test_hasdict4_1() -> None:
    class SomeBadTyped(TypedDict):
        bla: "aaaa"  # type: ignore  # noqa: F821

    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class HasDict4:
            x1: SomeBadTyped


def test_bad_dict1() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict1:
            # Invalid type! Should always fail!
            x1: dict[str, float, int]  # type: ignore


def test_bad_dict2() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict2:
            # Invalid type! Should always fail!
            x1: dict[str]  # type: ignore


def test_bad_dict3() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict3:
            # Invalid type! Should always fail!
            x1: "Dict[str, float, int]"  # type: ignore


def test_bad_dict4() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict4:
            # Invalid type! Should always fail!
            x1: "Dict[str]"  # type: ignore


def test_bad_dict5() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict5:
            # Invalid type! Should always fail!
            x1: dict[str, ...]  # type: ignore


def test_bad_dict6() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict6:
            # Invalid type! Should always fail!
            x1: dict[..., str]  # type: ignore


def test_bad_dict7() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict7:
            # Invalid type! Should always fail!
            x1: dict[lambda x: x, str]  # type: ignore


def test_bad_dict8() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadDict8:
            # Invalid type! Should always fail!
            x1: dict["compile error", "bad type"]  # type: ignore  # noqa: F722
