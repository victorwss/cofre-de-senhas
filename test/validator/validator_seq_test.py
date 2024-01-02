from validator import TypeValidationError, dataclass_validate
from dataclasses import dataclass
from typing import FrozenSet, Iterable, List, Sequence, Set
from pytest import raises


def test_haslist1_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList1:
        x1: list[float]

    t1: HasList1 = HasList1([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]


def test_haslist1_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList1:
        x1: list[float]

    t1: HasList1 = HasList1([])
    assert t1.x1 == []


def test_haslist1_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList1:
        x1: list[float]

    with raises(TypeValidationError):
        HasList1(["a", 3.3])  # type: ignore


def test_haslist1_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList1:
        x1: list[float]

    with raises(TypeValidationError):
        HasList1([3.3, "x"])  # type: ignore


def test_haslist1_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList1:
        x1: list[float]

    with raises(TypeValidationError):
        HasList1("xxx")  # type: ignore


def test_haslist1_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList1:
        x1: list[float]

    with raises(TypeValidationError):
        HasList1({3.5, 7.8})  # type: ignore


def test_haslist2_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList2:
        x1: List[float]

    t1: HasList2 = HasList2([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]


def test_haslist2_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList2:
        x1: List[float]

    t1: HasList2 = HasList2([])
    assert t1.x1 == []


def test_haslist2_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList2:
        x1: List[float]

    with raises(TypeValidationError):
        HasList2(["a", 3.3])  # type: ignore


def test_haslist2_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList2:
        x1: List[float]

    with raises(TypeValidationError):
        HasList2([3.3, "x"])  # type: ignore


def test_haslist2_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList2:
        x1: List[float]

    with raises(TypeValidationError):
        HasList2("xxx")  # type: ignore


def test_haslist2_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasList2:
        x1: List[float]

    with raises(TypeValidationError):
        HasList2({3.5, 7.8})  # type: ignore


def test_hasset1_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet1:
        x1: set[float]

    t1: HasSet1 = HasSet1({3.5, 7.8})
    assert t1.x1 == {3.5, 7.8}


def test_hasset1_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet1:
        x1: set[float]

    t1: HasSet1 = HasSet1(set())
    assert t1.x1 == set()


def test_hasset1_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet1:
        x1: set[float]

    with raises(TypeValidationError):
        HasSet1({"a", 3.3})  # type: ignore


def test_hasset1_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet1:
        x1: set[float]

    with raises(TypeValidationError):
        HasSet1({3.3, "x"})  # type: ignore


def test_hasset1_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet1:
        x1: set[float]

    with raises(TypeValidationError):
        HasSet1("xxx")  # type: ignore


def test_hasset1_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet1:
        x1: set[float]

    with raises(TypeValidationError):
        HasSet1([3.5, 7.8])  # type: ignore


def test_hasset1_7() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet1:
        x1: set[float]

    with raises(TypeValidationError):
        HasSet1(frozenset([3.5, 7.8]))  # type: ignore


def test_hasset2_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet2:
        x1: Set[float]

    t1: HasSet2 = HasSet2({3.5, 7.8})
    assert t1.x1 == {3.5, 7.8}


def test_hasset2_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet2:
        x1: Set[float]

    t1: HasSet2 = HasSet2(set())
    assert t1.x1 == set()


def test_hasset2_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet2:
        x1: Set[float]

    with raises(TypeValidationError):
        HasSet2({"a", 3.3})  # type: ignore


def test_hasset2_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet2:
        x1: Set[float]

    with raises(TypeValidationError):
        HasSet2({3.3, "x"})  # type: ignore


def test_hasset2_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet2:
        x1: Set[float]

    with raises(TypeValidationError):
        HasSet2("xxx")  # type: ignore


def test_hasset2_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet2:
        x1: Set[float]

    with raises(TypeValidationError):
        HasSet2([3.5, 7.8])  # type: ignore


def test_hasset2_7() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSet2:
        x1: Set[float]

    with raises(TypeValidationError):
        HasSet2(frozenset([3.5, 7.8]))  # type: ignore


def test_hasfrozenset1_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet1:
        x1: frozenset[float]

    t1: HasFrozenSet1 = HasFrozenSet1(frozenset([3.5, 7.8]))
    assert t1.x1 == frozenset([3.5, 7.8])


def test_hasfrozenset1_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet1:
        x1: frozenset[float]

    t1: HasFrozenSet1 = HasFrozenSet1(frozenset())
    assert t1.x1 == frozenset([])


def test_hasfrozenset1_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet1:
        x1: frozenset[float]

    with raises(TypeValidationError):
        HasFrozenSet1(frozenset(["a", 3.3]))  # type: ignore


def test_hasfrozenset1_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet1:
        x1: frozenset[float]

    with raises(TypeValidationError):
        HasFrozenSet1(frozenset([3.3, "x"]))  # type: ignore


def test_hasfrozenset1_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet1:
        x1: frozenset[float]

    with raises(TypeValidationError):
        HasFrozenSet1("xxx")  # type: ignore


def test_hasfrozenset1_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet1:
        x1: frozenset[float]

    with raises(TypeValidationError):
        HasFrozenSet1([3.5, 7.8])  # type: ignore


def test_hasfrozenset1_7() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet1:
        x1: frozenset[float]

    with raises(TypeValidationError):
        HasFrozenSet1({3.5, 7.8})  # type: ignore


def test_hasfrozenset2_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet2:
        x1: FrozenSet[float]

    t1: HasFrozenSet2 = HasFrozenSet2(frozenset([3.5, 7.8]))
    assert t1.x1 == frozenset([3.5, 7.8])


def test_hasfrozenset2_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet2:
        x1: FrozenSet[float]

    t1: HasFrozenSet2 = HasFrozenSet2(frozenset())
    assert t1.x1 == frozenset([])


def test_hasfrozenset2_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet2:
        x1: FrozenSet[float]

    with raises(TypeValidationError):
        HasFrozenSet2(frozenset(["a", 3.3]))  # type: ignore


def test_hasfrozenset2_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet2:
        x1: FrozenSet[float]

    with raises(TypeValidationError):
        HasFrozenSet2(frozenset([3.3, "x"]))  # type: ignore


def test_hasfrozenset2_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet2:
        x1: FrozenSet[float]

    with raises(TypeValidationError):
        HasFrozenSet2("xxx")  # type: ignore


def test_hasfrozenset2_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet2:
        x1: FrozenSet[float]

    with raises(TypeValidationError):
        HasFrozenSet2([3.5, 7.8])  # type: ignore


def test_hasfrozenset2_7() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasFrozenSet2:
        x1: FrozenSet[float]

    with raises(TypeValidationError):
        HasFrozenSet2({3.5, 7.8})  # type: ignore


def test_hasiterable_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasIterable:
        x1: Iterable[float]

    t1: HasIterable = HasIterable([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]


def test_hasiterable_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasIterable:
        x1: Iterable[float]

    t1: HasIterable = HasIterable({3.5, 7.8})
    assert t1.x1 == {3.5, 7.8}


def test_hasiterable_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasIterable:
        x1: Iterable[float]

    t1: HasIterable = HasIterable(frozenset([3.5, 7.8]))
    assert t1.x1 == frozenset([3.5, 7.8])


def test_hasiterable_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasIterable:
        x1: Iterable[float]

    with raises(TypeValidationError):
        HasIterable(["a", 3.3])  # type: ignore


def test_hasiterable_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasIterable:
        x1: Iterable[float]

    with raises(TypeValidationError):
        HasIterable([3.3, "a"])  # type: ignore


def test_hasiterable_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasIterable:
        x1: Iterable[float]

    with raises(TypeValidationError):
        HasIterable("xxx")  # type: ignore


def test_hassequence_1() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSequence:
        x1: Sequence[float]

    t1: HasSequence = HasSequence([3.5, 7.8])
    assert t1.x1 == [3.5, 7.8]


def test_hassequence_2() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSequence:
        x1: Sequence[float]

    with raises(TypeValidationError):
        HasSequence({3.5, 7.8})  # type: ignore


def test_hassequence_3() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSequence:
        x1: Sequence[float]

    with raises(TypeValidationError):
        HasSequence(frozenset([3.5, 7.8]))  # type: ignore


def test_hassequence_4() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSequence:
        x1: Sequence[float]

    with raises(TypeValidationError):
        HasSequence(["a", 3.3])  # type: ignore


def test_hassequence_5() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSequence:
        x1: Sequence[float]

    with raises(TypeValidationError):
        HasSequence([3.3, "a"])  # type: ignore


def test_hassequence_6() -> None:
    @dataclass_validate
    @dataclass(frozen = True)
    class HasSequence:
        x1: Sequence[float]

    with raises(TypeValidationError):
        HasSequence("xxx")  # type: ignore


def test_bad_list_1() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadList1:
            # Invalid type! Should always fail!
            x1: list["compile error", "bad type"]  # type: ignore  # noqa: F722


def test_bad_list_2() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadList2:
            # Invalid type! Should always fail!
            x1: list[str, int]  # type: ignore


def test_bad_list_3() -> None:
    with raises(TypeValidationError):
        @dataclass_validate
        @dataclass(frozen = True)
        class BadList3:
            # Invalid type! Should always fail!
            x1: list[...]  # type: ignore
