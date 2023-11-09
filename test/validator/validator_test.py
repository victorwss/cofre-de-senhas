from validator import TypeValidationError, dataclass_validate, dataclass_validate_local
from dataclasses import dataclass
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple, TypedDict
from pytest import raises

@dataclass_validate
@dataclass(frozen = True)
class Simple:
    x1: str

def test_simple_1() -> None:
    t1: Simple = Simple("a")
    assert t1.x1 == "a"

def test_simple_2() -> None:
    with raises(TypeValidationError):
        Simple(123) # type: ignore

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
    with raises(TypeValidationError):
        United(123.567) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class Tupled1:
    x1: tuple[str, int, float, str]

def test_tupled1_1() -> None:
    t1: Tupled1 = Tupled1(("a", 5, 3.3, "b"))
    assert t1.x1 == ("a", 5, 3.3, "b")

def test_tupled1_2() -> None:
    with raises(TypeValidationError):
        Tupled1(("a", 5, 3.3)) # type: ignore

def test_tupled1_3() -> None:
    with raises(TypeValidationError):
        Tupled1(("a", 5, 3.3, "b", "x")) # type: ignore

def test_tupled1_4() -> None:
    with raises(TypeValidationError):
        Tupled1(("a", 5, 3.3, 4)) # type: ignore

def test_tupled1_5() -> None:
    with raises(TypeValidationError):
        Tupled1(()) # type: ignore

def test_tupled1_6() -> None:
    with raises(TypeValidationError):
        Tupled1("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class Tupled2:
    x1: Tuple[str, int, float, str]

def test_tupled2_1() -> None:
    t1: Tupled2 = Tupled2(("a", 5, 3.3, "b"))
    assert t1.x1 == ("a", 5, 3.3, "b")

def test_tupled2_2() -> None:
    with raises(TypeValidationError):
        Tupled2(("a", 5, 3.3)) # type: ignore

def test_tupled2_3() -> None:
    with raises(TypeValidationError):
        Tupled2(("a", 5, 3.3, "b", "x")) # type: ignore

def test_tupled2_4() -> None:
    with raises(TypeValidationError):
        Tupled2(("a", 5, 3.3, 4)) # type: ignore

def test_tupled2_5() -> None:
    with raises(TypeValidationError):
        Tupled2(()) # type: ignore

def test_tupled2_6() -> None:
    with raises(TypeValidationError):
        Tupled2("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class Tupled3:
    x1: tuple[str, tuple[int, str], float, tuple[float, str, list[str]]]

def test_tupled3_1() -> None:
    t1: Tupled3 = Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", ["c", "d"])))
    assert t1.x1 == ("a", (5, "xx"), 3.3, (2.0, "b", ["c", "d"]))

def test_tupled3_2() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx", "y"), 3.3, (2.0, "b", ["c", "d"]))) # type: ignore

def test_tupled3_3() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", (5, ), 3.3, (2.0, "b", ["c", "d"]))) # type: ignore

def test_tupled3_4() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", ("x", ), 3.3, (2.0, "b", ["c", "d"]))) # type: ignore

def test_tupled3_5() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, 5, ["c", "d"]))) # type: ignore

def test_tupled3_6() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", ["c", "d"], "e"))) # type: ignore

def test_tupled3_7() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b"))) # type: ignore

def test_tupled3_8() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", ("c", "d")))) # type: ignore

def test_tupled3_9() -> None:
    with raises(TypeValidationError):
        Tupled3(("a", (5, "xx"), 3.3, (2.0, "b", [4, 6]))) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class TupledCont:
    # Invalid type! Should always fail!
    x1: tuple[str, int, float, str, ...] # type: ignore

def test_tupled_cont_1() -> None:
    with raises(TypeValidationError):
        TupledCont(("a", 5, 3.3, "b")) # type: ignore

def test_tupled_cont_2() -> None:
    with raises(TypeValidationError):
        TupledCont(("a", 5, 3.3)) # type: ignore

def test_tupled_cont_3() -> None:
    with raises(TypeValidationError):
        TupledCont(("a", 5, 3.3, "b", "x"))

def test_tupled_cont_4() -> None:
    with raises(TypeValidationError):
        TupledCont(("a", 5, 3.3, 4)) # type: ignore

def test_tupled_cont_5() -> None:
    with raises(TypeValidationError):
        TupledCont(("a", 5, 3.3, "x", 5))

def test_tupled_cont_6() -> None:
    with raises(TypeValidationError):
        TupledCont(()) # type: ignore

def test_tupled_cont_7() -> None:
    with raises(TypeValidationError):
        TupledCont("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadTupledEllipsis:
    # Invalid type! Should always fail!
    x1: tuple[...] # type: ignore

def test_bad_tupled_ellipsis_1() -> None:
    with raises(TypeValidationError):
        BadTupledEllipsis(()) # type: ignore

def test_bad_tupled_ellipsis_2() -> None:
    with raises(TypeValidationError):
        BadTupledEllipsis(("a", ))

def test_bad_tupled_ellipsis_3() -> None:
    with raises(TypeValidationError):
        BadTupledEllipsis(("a", 5)) # type: ignore

def test_bad_tupled_ellipsis_4() -> None:
    with raises(TypeValidationError):
        BadTupledEllipsis("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class TupledEllipsis:
    x1: tuple[str | int, ...]

def test_tupled_ellipsis_1() -> None:
    t1: TupledEllipsis = TupledEllipsis(())
    assert t1.x1 == ()

def test_tupled_ellipsis_2() -> None:
    t1: TupledEllipsis = TupledEllipsis(("a", ))
    assert t1.x1 == ("a", )

def test_tupled_ellipsis_3() -> None:
    t1: TupledEllipsis = TupledEllipsis(("a", 5))
    assert t1.x1 == ("a", 5)

def test_tupled_ellipsis_4() -> None:
    t1: TupledEllipsis = TupledEllipsis((8, "a", 5, "x"))
    assert t1.x1 == (8, "a", 5, "x")

def test_tupled_ellipsis_5() -> None:
    t1: TupledEllipsis = TupledEllipsis((1, 2, 3))
    assert t1.x1 == (1, 2, 3)

def test_tupled_ellipsis_6() -> None:
    with raises(TypeValidationError):
        TupledEllipsis("xxx") # type: ignore

def test_tupled_ellipsis_7() -> None:
    with raises(TypeValidationError):
        TupledEllipsis((6.66, )) # type: ignore

def test_tupled_ellipsis_8() -> None:
    with raises(TypeValidationError):
        TupledEllipsis((1, 2, 3, 6.66)) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class TupledEmpty:
    x1: tuple[()]

def test_tupled_empty_1() -> None:
    t1: TupledEmpty = TupledEmpty(())
    assert t1.x1 == ()

def test_tupled_empty_2() -> None:
    with raises(TypeValidationError):
        TupledEmpty(("a", )) # type: ignore

def test_tupled_empty_3() -> None:
    with raises(TypeValidationError):
        TupledEmpty(("a", "x")) # type: ignore

def test_tupled_empty_4() -> None:
    with raises(TypeValidationError):
        TupledEmpty(("a", 789)) # type: ignore

def test_tupled_empty_5() -> None:
    with raises(TypeValidationError):
        TupledEmpty("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasDict1:
    x1: dict[float, float]

def test_hasdict1_1() -> None:
    t1: HasDict1 = HasDict1({3.5: 7.8, 4.4: 3.9})
    assert t1.x1 == {3.5: 7.8, 4.4: 3.9}

def test_hasdict1_2() -> None:
    t1: HasDict1 = HasDict1({})
    assert t1.x1 == {}

def test_hasdict1_3() -> None:
    with raises(TypeValidationError):
        HasDict1({"a": 3.3}) # type: ignore

def test_hasdict1_4() -> None:
    with raises(TypeValidationError):
        HasDict1({3.3: "x"}) # type: ignore

def test_hasdict1_5() -> None:
    with raises(TypeValidationError):
        HasDict1("xxx") # type: ignore

def test_hasdict1_6() -> None:
    with raises(TypeValidationError):
        HasDict1([]) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasDict2:
    x1: Dict[float, float]

def test_hasdict2_1() -> None:
    t1: HasDict2 = HasDict2({3.5: 7.8, 4.4: 3.9})
    assert t1.x1 == {3.5: 7.8, 4.4: 3.9}

def test_hasdict2_2() -> None:
    t1: HasDict2 = HasDict2({})
    assert t1.x1 == {}

def test_hasdict2_3() -> None:
    with raises(TypeValidationError):
        HasDict2({"a": 3.3}) # type: ignore

def test_hasdict2_4() -> None:
    with raises(TypeValidationError):
        HasDict2({3.3: "x"}) # type: ignore

def test_hasdict2_5() -> None:
    with raises(TypeValidationError):
        HasDict2("xxx") # type: ignore

def test_hasdict2_6() -> None:
    with raises(TypeValidationError):
        HasDict2([]) # type: ignore

class SomeTyped(TypedDict):
    bla: str
    gua: float
    ta: int

@dataclass_validate
@dataclass(frozen = True)
class HasDict3:
    x1: SomeTyped

def test_hasdict3_1() -> None:
    t1: HasDict3 = HasDict3({"bla": "xx", "gua": 3.9, "ta": 6})
    assert [t1.x1["bla"], t1.x1["gua"], t1.x1["ta"]] == ["xx", 3.9, 6]
    assert len(t1.x1) == 3

def test_hasdict3_2() -> None:
    with raises(TypeValidationError):
        t1: HasDict3 = HasDict3({}) # type: ignore

def test_hasdict3_3() -> None:
    with raises(TypeValidationError):
        t1: HasDict3 = HasDict3({"hjhk": 555}) # type: ignore

def test_hasdict3_4() -> None:
    with raises(TypeValidationError):
        t1: HasDict3 = HasDict3({"bla": "xx", "ta": 6}) # type: ignore

def test_hasdict3_5() -> None:
    with raises(TypeValidationError):
        t1: HasDict3 = HasDict3({"bla": "xx", "gua": 3.9, "ta": 6, "jjjj": 4568}) # type: ignore

def test_hasdict3_6() -> None:
    with raises(TypeValidationError):
        t1: HasDict3 = HasDict3({"bla": 5, "gua": 3.9, "ta": 6}) # type: ignore

def test_hasdict3_7() -> None:
    with raises(TypeValidationError):
        t1: HasDict3 = HasDict3({"bla": "xx", "gua": 3.9, "ta": "6"}) # type: ignore

class SomeBadTyped(TypedDict):
    bla: "aaaa" # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasDict4:
    x1: SomeBadTyped

def test_hasdict4_1() -> None:
    with raises(TypeValidationError):
        HasDict4({"bla": "xx"})

@dataclass_validate
@dataclass(frozen = True)
class BadDict1:
    # Invalid type! Should always fail!
    x1: dict[str, float, int] # type: ignore

def test_bad_dict1_1() -> None:
    with raises(TypeValidationError):
        BadDict1({})

def test_bad_dict1_2() -> None:
    with raises(TypeValidationError):
        BadDict1("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadDict2:
    # Invalid type! Should always fail!
    x1: dict[str] # type: ignore

def test_bad_dict2_1() -> None:
    with raises(TypeValidationError):
        BadDict2({})

def test_bad_dict2_2() -> None:
    with raises(TypeValidationError):
        BadDict2("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadDict3:
    # Invalid type! Should always fail!
    x1: "Dict[str, float, int]" # type: ignore

def test_bad_dict3_1() -> None:
    with raises(TypeValidationError):
        BadDict3({})

def test_bad_dict3_2() -> None:
    with raises(TypeValidationError):
        BadDict3("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadDict4:
    # Invalid type! Should always fail!
    x1: "Dict[str]" # type: ignore

def test_bad_dict4_1() -> None:
    with raises(TypeValidationError):
        BadDict4({})

def test_bad_dict4_2() -> None:
    with raises(TypeValidationError):
        BadDict4("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadDict5:
    # Invalid type! Should always fail!
    x1: dict[str, ...] # type: ignore

def test_bad_dict5_1() -> None:
    with raises(TypeValidationError):
        BadDict5({})

def test_bad_dict5_2() -> None:
    with raises(TypeValidationError):
        BadDict5("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadDict6:
    # Invalid type! Should always fail!
    x1: dict[..., str] # type: ignore

def test_bad_dict6_1() -> None:
    with raises(TypeValidationError):
        BadDict6({})

def test_bad_dict6_2() -> None:
    with raises(TypeValidationError):
        BadDict6("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadDict7:
    # Invalid type! Should always fail!
    x1: dict[lambda x: x, str] # type: ignore

def test_bad_dict7_1() -> None:
    with raises(TypeValidationError):
        BadDict6({})

def test_bad_dict7_2() -> None:
    with raises(TypeValidationError):
        BadDict6("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class BadDict8:
    # Invalid type! Should always fail!
    x1: dict["compile error", "bad type"] # type: ignore

def test_bad_dict8_1() -> None:
    with raises(TypeValidationError):
        BadDict8({})

def test_bad_dict8_2() -> None:
    with raises(TypeValidationError):
        BadDict8("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasList1:
    x1: list[float]

def test_haslist1_1() -> None:
    t1: HasList1 = HasList1([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]

def test_haslist1_2() -> None:
    t1: HasList1 = HasList1([])
    assert t1.x1 == []

def test_haslist1_3() -> None:
    with raises(TypeValidationError):
        HasList1(["a", 3.3]) # type: ignore

def test_haslist1_4() -> None:
    with raises(TypeValidationError):
        HasList1([3.3, "x"]) # type: ignore

def test_haslist1_5() -> None:
    with raises(TypeValidationError):
        HasList1("xxx") # type: ignore

def test_haslist1_6() -> None:
    with raises(TypeValidationError):
        HasList1({3.5, 7.8}) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasList2:
    x1: List[float]

def test_haslist2_1() -> None:
    t1: HasList2 = HasList2([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]

def test_haslist2_2() -> None:
    t1: HasList2 = HasList2([])
    assert t1.x1 == []

def test_haslist2_3() -> None:
    with raises(TypeValidationError):
        HasList2(["a", 3.3]) # type: ignore

def test_haslist2_4() -> None:
    with raises(TypeValidationError):
        HasList2([3.3, "x"]) # type: ignore

def test_haslist2_5() -> None:
    with raises(TypeValidationError):
        HasList2("xxx") # type: ignore

def test_haslist2_6() -> None:
    with raises(TypeValidationError):
        HasList2({3.5, 7.8}) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasSet1:
    x1: set[float]

def test_hasset1_1() -> None:
    t1: HasSet1 = HasSet1({3.5, 7.8})
    assert t1.x1 == {3.5, 7.8}

def test_hasset1_2() -> None:
    t1: HasSet1 = HasSet1(set())
    assert t1.x1 == set()

def test_hasset1_3() -> None:
    with raises(TypeValidationError):
        HasSet1({"a", 3.3}) # type: ignore

def test_hasset1_4() -> None:
    with raises(TypeValidationError):
        HasSet1({3.3, "x"}) # type: ignore

def test_hasset1_5() -> None:
    with raises(TypeValidationError):
        HasSet1("xxx") # type: ignore

def test_hasset1_6() -> None:
    with raises(TypeValidationError):
        HasSet1([3.5, 7.8]) # type: ignore

def test_hasset1_7() -> None:
    with raises(TypeValidationError):
        HasSet1(frozenset([3.5, 7.8])) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasSet2:
    x1: Set[float]

def test_hasset2_1() -> None:
    t1: HasSet2 = HasSet2({3.5, 7.8})
    assert t1.x1 == {3.5, 7.8}

def test_hasset2_2() -> None:
    t1: HasSet2 = HasSet2(set())
    assert t1.x1 == set()

def test_hasset2_3() -> None:
    with raises(TypeValidationError):
        HasSet2({"a", 3.3}) # type: ignore

def test_hasset2_4() -> None:
    with raises(TypeValidationError):
        HasSet2({3.3, "x"}) # type: ignore

def test_hasset2_5() -> None:
    with raises(TypeValidationError):
        HasSet2("xxx") # type: ignore

def test_hasset2_6() -> None:
    with raises(TypeValidationError):
        HasSet2([3.5, 7.8]) # type: ignore

def test_hasset2_7() -> None:
    with raises(TypeValidationError):
        HasSet2(frozenset([3.5, 7.8])) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasFrozenSet1:
    x1: frozenset[float]

def test_hasfrozenset1_1() -> None:
    t1: HasFrozenSet1 = HasFrozenSet1(frozenset([3.5, 7.8]))
    assert t1.x1 == frozenset([3.5, 7.8])

def test_hasfrozenset1_2() -> None:
    t1: HasFrozenSet1 = HasFrozenSet1(frozenset())
    assert t1.x1 == frozenset([])

def test_hasfrozenset1_3() -> None:
    with raises(TypeValidationError):
        HasFrozenSet1(frozenset(["a", 3.3])) # type: ignore

def test_hasfrozenset1_4() -> None:
    with raises(TypeValidationError):
        HasFrozenSet1(frozenset([3.3, "x"])) # type: ignore

def test_hasfrozenset1_5() -> None:
    with raises(TypeValidationError):
        HasFrozenSet1("xxx") # type: ignore

def test_hasfrozenset1_6() -> None:
    with raises(TypeValidationError):
        HasFrozenSet1([3.5, 7.8]) # type: ignore

def test_hasfrozenset1_7() -> None:
    with raises(TypeValidationError):
        HasFrozenSet1({3.5, 7.8}) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasFrozenSet2:
    x1: FrozenSet[float]

def test_hasfrozenset2_1() -> None:
    t1: HasFrozenSet2 = HasFrozenSet2(frozenset([3.5, 7.8]))
    assert t1.x1 == frozenset([3.5, 7.8])

def test_hasfrozenset2_2() -> None:
    t1: HasFrozenSet2 = HasFrozenSet2(frozenset())
    assert t1.x1 == frozenset([])

def test_hasfrozenset2_3() -> None:
    with raises(TypeValidationError):
        HasFrozenSet2(frozenset(["a", 3.3])) # type: ignore

def test_hasfrozenset2_4() -> None:
    with raises(TypeValidationError):
        HasFrozenSet2(frozenset([3.3, "x"])) # type: ignore

def test_hasfrozenset2_5() -> None:
    with raises(TypeValidationError):
        HasFrozenSet2("xxx") # type: ignore

def test_hasfrozenset2_6() -> None:
    with raises(TypeValidationError):
        HasFrozenSet2([3.5, 7.8]) # type: ignore

def test_hasfrozenset2_7() -> None:
    with raises(TypeValidationError):
        HasFrozenSet2({3.5, 7.8}) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasIterable:
    x1: Iterable[float]

def test_hasiterable_1() -> None:
    t1: HasIterable = HasIterable([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]

def test_hasiterable_2() -> None:
    t1: HasIterable = HasIterable({3.5, 7.8})
    assert t1.x1 == {3.5, 7.8}

def test_hasiterable_3() -> None:
    t1: HasIterable = HasIterable(frozenset([3.5, 7.8]))
    assert t1.x1 == frozenset([3.5, 7.8])

def test_hasiterable_4() -> None:
    with raises(TypeValidationError):
        HasIterable(["a", 3.3]) # type: ignore

def test_hasiterable_5() -> None:
    with raises(TypeValidationError):
        HasIterable([3.3, "a"]) # type: ignore

def test_hasiterable_6() -> None:
    with raises(TypeValidationError):
        HasIterable("xxx") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class HasSequence:
    x1: Sequence[float]

def test_hassequence_1() -> None:
    t1: HasSequence = HasSequence([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]

def test_hassequence_2() -> None:
    with raises(TypeValidationError):
        HasSequence({3.5, 7.8}) # type: ignore

def test_hassequence_3() -> None:
    with raises(TypeValidationError):
        HasSequence(frozenset([3.5, 7.8])) # type: ignore

def test_hassequence_4() -> None:
    with raises(TypeValidationError):
        HasSequence(["a", 3.3]) # type: ignore

def test_hassequence_5() -> None:
    with raises(TypeValidationError):
        HasSequence([3.3, "a"]) # type: ignore

def test_hassequence_6() -> None:
    with raises(TypeValidationError):
        HasSequence("xxx") # type: ignore

def test_bad_list_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class BadList1:
        # Invalid type! Should always fail!
        x1: list["compile error", "bad type"] # type: ignore
    with raises(TypeValidationError):
        BadList1("xxx") # type: ignore

def test_bad_list_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class BadList2:
        # Invalid type! Should always fail!
        x1: list[str, int] # type: ignore
    with raises(TypeValidationError):
        BadList2("xxx") # type: ignore

def test_bad_list_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class BadList3:
        # Invalid type! Should always fail!
        x1: list[...] # type: ignore
    with raises(TypeValidationError):
        BadList3("xxx") # type: ignore

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
    x1: Callable[..., str]

@dataclass_validate
@dataclass(frozen = True)
class HasCall4:
    x1: Callable[..., None]

@dataclass_validate
@dataclass(frozen = True)
class HasCall5:
    x1: Callable[[str, int, int], Any]

@dataclass_validate
@dataclass(frozen = True)
class HasCall6:
    x1: Callable[..., Any]

@dataclass_validate
@dataclass(frozen = True)
class HasCall7:
    x1: Callable[[str, Any, int], int]

def test_hascall_1a() -> None:
    def u(x: float, y: int) -> str:
        return "z"

    t1: HasCall1 = HasCall1(u)
    assert t1.x1 == u

def test_hascall_1b() -> None:
    def u(x: float, y: int) -> int:
        return 6
    with raises(TypeValidationError):
        HasCall1(u) # type: ignore

def test_hascall_1c() -> None:
    def u(x: str, y: int) -> str:
        return "z"
    with raises(TypeValidationError):
        HasCall1(u) # type: ignore

def test_hascall_1d() -> None:
    def u(x: str) -> str:
        return "z"
    with raises(TypeValidationError):
        HasCall1(u) # type: ignore

def test_hascall_1e() -> None:
    def u(x: float, y: int, w: int) -> str:
        return "z"
    with raises(TypeValidationError):
        HasCall1(u) # type: ignore

def test_hascall_2a() -> None:
    def u(x: str, y: int, z: int) -> str:
        return "z"

    t1: HasCall2 = HasCall2(u)
    assert t1.x1 == u

def test_hascall_2b() -> None:
    def u(x: str, y: int) -> str:
        return "z"

    with raises(TypeValidationError):
        HasCall2(u) # type: ignore

def test_hascall_3a() -> None:
    def u(x: str, y: int) -> str:
        return "z"

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u

def test_hascall_3b() -> None:
    def u(x: str, y: int, z: float) -> str:
        return "z"

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u

def test_hascall_3c() -> None:
    def u() -> str:
        return "z"

    t1: HasCall3 = HasCall3(u)
    assert t1.x1 == u

def test_hascall_3d() -> None:
    def u() -> int:
        return 5

    with raises(TypeValidationError):
        HasCall3(u) # type: ignore

def test_hascall_4a() -> None:
    def u(x: str, y: int) -> None:
        pass

    t1: HasCall4 = HasCall4(u)
    assert t1.x1 == u

def test_hascall_4b() -> None:
    def u(x: str, y: int, z: float) -> None:
        pass

    t1: HasCall4 = HasCall4(u)
    assert t1.x1 == u

def test_hascall_4c() -> None:
    def u() -> None:
        pass

    t1: HasCall4 = HasCall4(u)
    assert t1.x1 == u

def test_hascall_4d() -> None:
    def u() -> int:
        return 5

    with raises(TypeValidationError):
        HasCall4(u) # type: ignore

def test_hascall_5a() -> None:
    def u(x: str, y: int, z: int) -> str:
        return "x"

    t1: HasCall5 = HasCall5(u)
    assert t1.x1 == u

def test_hascall_5b() -> None:
    def u(x: str, y: int, z: int) -> int:
        return 5

    t1: HasCall5 = HasCall5(u)
    assert t1.x1 == u

def test_hascall_5c() -> None:
    def u(x: str, y: int, z: int) -> Any:
        return 5

    t1: HasCall5 = HasCall5(u)
    assert t1.x1 == u

def test_hascall_5d() -> None:
    def u(x: str, y: str, z: int) -> Any:
        return 5

    with raises(TypeValidationError):
        HasCall5(u) # type: ignore

def test_hascall_6a() -> None:
    def u() -> str:
        return "x"

    t1: HasCall6 = HasCall6(u)
    assert t1.x1 == u

def test_hascall_6b() -> None:
    def u(x: str, y: int) -> int:
        return 5

    t1: HasCall6 = HasCall6(u)
    assert t1.x1 == u

def test_hascall_6c() -> None:
    def u(x: str) -> Any:
        return 5

    t1: HasCall6 = HasCall6(u)
    assert t1.x1 == u

def test_hascall_7a() -> None:
    def u(x: str, y: Any, z: int) -> int:
        return 5

    t1: HasCall7 = HasCall7(u)
    assert t1.x1 == u

def test_hascall_7b() -> None:
    def u(x: str, y: str, z: int) -> int:
        return 5

    with raises(TypeValidationError):
        HasCall7(u)

def test_hascall_8a() -> None:
    def u(x: "do_not_exist") -> int: # type: ignore
        return 5

    @dataclass_validate
    @dataclass(frozen = True)
    class HasCall8:
        x1: Callable[["do_not_exist"], int] # type: ignore

    with raises(TypeValidationError):
        HasCall8(u)

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
    with raises(TypeValidationError):
        SomeClass(123, 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3) # type: ignore

def test_validation_is_strong_typed_2() -> None:
    with raises(TypeValidationError):
        SomeClass("a", "b", "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3) # type: ignore

def test_validation_is_strong_typed_3() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, _foo_2, ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3) # type: ignore

def test_validation_is_strong_typed_4() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, "e", _foo_1, _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3) # type: ignore

def test_validation_is_strong_typed_5() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_2, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), _foo_3) # type: ignore

def test_validation_is_strong_typed_7() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, 123, _foo_2, ("1", "2", "3", "4", "5"), _foo_3) # type: ignore

def test_validation_is_strong_typed_8() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", "x", ("1", "2", "3", "4", "5"), _foo_3) # type: ignore

def test_validation_is_strong_typed_9a() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, 444, _foo_3) # type: ignore

def test_validation_is_strong_typed_9b() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, (444, ), _foo_3) # type: ignore

def test_validation_is_strong_typed_10() -> None:
    with raises(TypeValidationError):
        SomeClass("a", 123, "e", ("a", 5, 7.7), _foo_1, raises, "ss", _foo_2, ("1", "2", "3", "4", "5"), "x") # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class WithString:
    z: "int"

def test_with_string_typed() -> None:
    a: WithString = WithString(4)
    assert a.z == 4

@dataclass_validate
@dataclass(frozen = True)
class SelfRef:
    z: "SelfRef | None"

def test_with_string_self_typed() -> None:
    a: SelfRef = SelfRef(None)
    assert a.z == None
    b: SelfRef = SelfRef(a)
    assert b.z == a

@dataclass_validate
@dataclass(frozen = True)
class Circular1:
    og: "Circular2 | None"

@dataclass_validate
@dataclass(frozen = True)
class Circular2:
    og: "Circular1"

def test_circular_ok() -> None:
    a: Circular1 = Circular1(None)
    b: Circular2 = Circular2(a)
    c: Circular1 = Circular1(b)

    assert c.og == b
    assert b.og == a
    assert a.og == None

def test_circular_bad() -> None:
    with raises(TypeValidationError):
        Circular1("foo") # type: ignore

    with raises(TypeValidationError):
        Circular2("foo") # type: ignore

    a: Circular1 = Circular1(None)
    b: Circular2 = Circular2(a)

    with raises(TypeValidationError):
        Circular1(a) # type: ignore

    with raises(TypeValidationError):
        Circular2(b) # type: ignore

@dataclass_validate
@dataclass(frozen = True)
class Crazy1:
    x1: int

@dataclass_validate
@dataclass(frozen = True)
class Crazy2:
    x1: List[Crazy1]

@dataclass_validate
@dataclass(frozen = True)
class Crazy3:
    x1: "List[Crazy2]"

@dataclass_validate
@dataclass(frozen = True)
class Crazy4:
    x1: List["Crazy4"]

def test_crazy_1() -> None:
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
    with raises(TypeValidationError):
        Crazy2(5) # type: ignore

def test_crazy_3() -> None:
    with raises(TypeValidationError):
        Crazy3(Crazy1(5)) # type: ignore

def test_crazy_4() -> None:
    a: Crazy4 = Crazy4([])
    b: Crazy4 = Crazy4([a])
    c: Crazy4 = Crazy4([a, b, a])
    d: Crazy4 = Crazy4([c, b, a, b, c])
    e: Crazy4 = Crazy4([d, b, a, c, d, a, c])

@dataclass_validate
@dataclass(frozen = True)
class BadCrap:
    # Invalid type! Should always fail!
    x1: "compile error" # type: ignore

def test_bad_crap() -> None:
    with raises(TypeValidationError):
        BadCrap("aaa")
    with raises(TypeError):
        BadCrap() # type: ignore
    with raises(TypeError):
        BadCrap(5, 7) # type: ignore
    with raises(TypeValidationError):
        BadCrap(3)

def test_post_init() -> None:
    z: HasPostInit1 | None = None

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
    z: HasPostInit2 | None = None

    @dataclass_validate
    @dataclass(frozen = True)
    class HasPostInit2:
        x1: str

        def __post_init__(self) -> None:
            assert self.x1 == 1 # type: ignore
            nonlocal z
            z = self

    with raises(TypeValidationError):
        HasPostInit2(1) # type: ignore
    assert z.x1 == 1 # type: ignore

def test_post_validate() -> None:
    z: HasPostInit3 | None = None
    y: HasPostInit3 | None = None

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
    z: HasPostInit4 | None = None

    @dataclass_validate
    @dataclass(frozen = True)
    class HasPostInit4:
        x1: str

        def __post_init__(self) -> None:
            assert self.x1 == 1 # type: ignore
            nonlocal z
            z = self

        def __post_type_validate__(self) -> None:
            assert False

    with raises(TypeValidationError):
        HasPostInit4(1) # type: ignore
    assert z.x1 == 1 # type: ignore

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

    @dataclass_validate
    @dataclass(frozen = True)
    class NonLocal2:
        x1: "uuid.UUID"

    x: uuid.UUID = uuid.UUID("12345678123456781234567812345678")
    with raises(TypeValidationError):
        y: NonLocal2 = NonLocal2(x)

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

    @dataclass_validate
    @dataclass(frozen = True)
    class NonLocal4:
        x1: "Sbrubbles"

    x: Sbrubbles = Sbrubbles("12345678123456781234567812345678")
    with raises(TypeValidationError):
        y: NonLocal4 = NonLocal4(x)

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
    class NonLocal5:
        x1: "Crazy1"

    x: Crazy1 = Crazy1(4)
    y: NonLocal5 = NonLocal5(x)
    assert y.x1 is x

def test_non_local_6a() -> None:

    @dataclass_validate
    @dataclass(frozen = True)
    class NonLocal6A:
        x1: "Crazy1"

    @dataclass_validate
    @dataclass(frozen = True)
    class NonLocal6B:
        x1: "NonLocal6A"

    x: Crazy1 = Crazy1(4)
    y: NonLocal6A = NonLocal6A(x)
    with raises(TypeValidationError):
        z: NonLocal6B = NonLocal6B(y)

def test_non_local_6b() -> None:

    @dataclass_validate
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