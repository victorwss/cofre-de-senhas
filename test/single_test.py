from decorators.single import Single
import threading

def test_single() -> None:
    a1: int = 0
    z1: int | None = None
    z2: int | None = None
    z3: int | None = None
    z4: int | None = None

    def a() -> None:
        nonlocal z1, z2
        z1 = Single.instance("test1")
        z2 = Single.instance("test1")

    def b() -> None:
        nonlocal z3, z4
        z3 = Single.instance("test1")
        z4 = Single.instance("test1")

    def c() -> int:
        nonlocal a1
        a1 += 1
        return a1

    Single.register("test1", c)
    t1 = threading.Thread(target = a, args = [])
    t2 = threading.Thread(target = b, args = [])
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert [a1, z1, z2, z3, z4] in [[2, 1, 1, 2, 2], [2, 2, 2, 1, 1]]

def test_single_two_values() -> None:
    a1: int = 0
    a2: int = 0
    z1: int | None = None
    z2: int | None = None
    z3: int | None = None
    z4: int | None = None
    z5: int | None = None
    z6: int | None = None

    def a() -> None:
        nonlocal z1, z2, z3
        z1 = Single.instance("test3")
        z2 = Single.instance("test4")
        z3 = Single.instance("test3")

    def b() -> None:
        nonlocal z4, z5, z6
        z4 = Single.instance("test3")
        z5 = Single.instance("test4")
        z6 = Single.instance("test3")

    def c() -> int:
        nonlocal a1
        a1 += 1
        return a1

    def d() -> int:
        nonlocal a2
        a2 += 1
        return a2

    Single.register("test3", c)
    Single.register("test4", d)
    t1 = threading.Thread(target = a, args = [])
    t2 = threading.Thread(target = b, args = [])
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert [a1, a2] == [2, 2]
    assert [z1, z3, z4, z6] in [[1, 1, 2, 2], [2, 2, 1, 1]]
    assert [z2, z5] in [[1, 2], [2, 1]]
