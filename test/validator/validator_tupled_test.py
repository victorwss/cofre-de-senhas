from validator import TypeValidationError, dataclass_validate
from dataclasses import dataclass
from typing import Tuple
from pytest import raises


def test_tupled1_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled1:
        x1: tuple[str, int, float, str]

    t1: Tupled1 = Tupled1(("a", 5, 3.3, "b"))
    assert t1.x1 == ("a", 5, 3.3, "b")


def test_tupled1_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled1:
        x1: tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled1(("a", 5, 3.3))  # type: ignore


def test_tupled1_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled1:
        x1: tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled1(("a", 5, 3.3, "b", "x"))  # type: ignore


def test_tupled1_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled1:
        x1: tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled1(("a", 5, 3.3, 4))  # type: ignore


def test_tupled1_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled1:
        x1: tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled1(())  # type: ignore


def test_tupled1_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled1:
        x1: tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled1("xxx")  # type: ignore


def test_tupled2_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled2:
        x1: Tuple[str, int, float, str]

    t1: Tupled2 = Tupled2(("a", 5, 3.3, "b"))
    assert t1.x1 == ("a", 5, 3.3, "b")


def test_tupled2_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled2:
        x1: Tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled2(("a", 5, 3.3))  # type: ignore


def test_tupled2_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled2:
        x1: Tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled2(("a", 5, 3.3, "b", "x"))  # type: ignore


def test_tupled2_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled2:
        x1: Tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled2(("a", 5, 3.3, 4))  # type: ignore


def test_tupled2_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled2:
        x1: Tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled2(())  # type: ignore


def test_tupled2_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled2:
        x1: Tuple[str, int, float, str]

    with raises(TypeValidationError):
        Tupled2("xxx")  # type: ignore


def test_tupled3_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    t1: Tupled3 = Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", ["c", "d"])))
    assert t1.x1 == ("a", (5, "xx"), 3.3, (2.0, "b", ["c", "d"]))


def test_tupled3_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx", "y"), 3.3, (2.0, "b", ["c", "d"])))  # type: ignore


def test_tupled3_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", (5, ), 3.3, (2.0, "b", ["c", "d"])))  # type: ignore


def test_tupled3_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", ("x", ), 3.3, (2.0, "b", ["c", "d"])))  # type: ignore


def test_tupled3_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, 5, ["c", "d"])))  # type: ignore


def test_tupled3_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", ["c", "d"], "e")))  # type: ignore


def test_tupled3_7() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b")))  # type: ignore


def test_tupled3_8() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", ("c", "d"))))  # type: ignore


def test_tupled3_9() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class Tupled3:
        x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", [4, 6])))  # type: ignore


def test_tupled_cont() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class TupledCont:
            # Invalid type! Should always fail!
            x1: tuple[str, int, float, str, ...]  # type: ignore


def test_bad_tupled_ellipsis() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadTupledEllipsis:
            # Invalid type! Should always fail!
            x1: tuple[...]  # type: ignore


def test_tupled_ellipsis_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    t1: TupledEllipsis = TupledEllipsis(())
    assert t1.x1 == ()


def test_tupled_ellipsis_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    t1: TupledEllipsis = TupledEllipsis(("a", ))
    assert t1.x1 == ("a", )


def test_tupled_ellipsis_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    t1: TupledEllipsis = TupledEllipsis(("a", 5))
    assert t1.x1 == ("a", 5)


def test_tupled_ellipsis_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    t1: TupledEllipsis = TupledEllipsis((8, "a", 5, "x"))
    assert t1.x1 == (8, "a", 5, "x")


def test_tupled_ellipsis_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    t1: TupledEllipsis = TupledEllipsis((1, 2, 3))
    assert t1.x1 == (1, 2, 3)


def test_tupled_ellipsis_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    with raises(TypeValidationError):
        TupledEllipsis("xxx")  # type: ignore


def test_tupled_ellipsis_7() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    with raises(TypeValidationError):
        TupledEllipsis((6.66, ))  # type: ignore


def test_tupled_ellipsis_8() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEllipsis:
        x1: tuple[str | int, ...]

    with raises(TypeValidationError):
        TupledEllipsis((1, 2, 3, 6.66))  # type: ignore


def test_tupled_empty_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEmpty:
        x1: tuple[()]

    t1: TupledEmpty = TupledEmpty(())
    assert t1.x1 == ()


def test_tupled_empty_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEmpty:
        x1: tuple[()]

    with raises(TypeValidationError):
        TupledEmpty(("a", ))  # type: ignore


def test_tupled_empty_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEmpty:
        x1: tuple[()]

    with raises(TypeValidationError):
        TupledEmpty(("a", "x"))  # type: ignore


def test_tupled_empty_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEmpty:
        x1: tuple[()]

    with raises(TypeValidationError):
        TupledEmpty(("a", 789))  # type: ignore


def test_tupled_empty_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class TupledEmpty:
        x1: tuple[()]

    with raises(TypeValidationError):
        TupledEmpty("xxx")  # type: ignore
