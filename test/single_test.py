from decorators.single import Single
import threading

def test_single():
    a1 = 0
    z1 = None
    z2 = None
    z3 = None
    z4 = None

    def a():
        nonlocal z1, z2
        z1 = Single.instance("test1")
        z2 = Single.instance("test1")

    def b():
        nonlocal z3, z4
        z3 = Single.instance("test1")
        z4 = Single.instance("test1")

    def c():
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

def test_single_two_values():
    a1 = 0
    a2 = 0
    z1 = None
    z2 = None
    z3 = None
    z4 = None
    z5 = None
    z6 = None

    def a():
        nonlocal z1, z2, z3
        z1 = Single.instance("test3")
        z2 = Single.instance("test4")
        z3 = Single.instance("test3")

    def b():
        nonlocal z4, z5, z6
        z4 = Single.instance("test3")
        z5 = Single.instance("test4")
        z6 = Single.instance("test3")

    def c():
        nonlocal a1
        a1 += 1
        return a1

    def d():
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
