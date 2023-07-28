from decorators.single import Single
import threading

def test_single():
    z0 = 0
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
        nonlocal z0
        z0 += 1
        return z0

    Single.register("test1", c)
    t1 = threading.Thread(target = a, args = [])
    t2 = threading.Thread(target = b, args = [])
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert [z0, z1, z2, z3, z4] in [[2, 1, 1, 2, 2], [2, 2, 2, 1, 1]]