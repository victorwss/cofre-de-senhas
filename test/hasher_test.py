from hasher import *
from .fixtures import *

def test_random_string() -> None:
    a: str = string_random(20)
    b: str = string_random(20)
    c: str = string_random(20)
    d: str = string_random(10)
    assert len({a, b, c}) == 3
    assert len(a) == 20
    assert len(b) == 20
    assert len(c) == 20
    assert len(d) == 10

def test_hash() -> None:
    a = criar_hash("alohomora")
    assert len(a) == 144 # 16 do sal + 128 do hash
    assert comparar_hash(a, "alohomora")
    assert not comparar_hash(a, "avada kedavra")
    assert not comparar_hash(a, "Alohomora")

def test_passwords() -> None:
    assert comparar_hash(avada_kedavra, "avada kedavra")
    assert comparar_hash(expelliarmus, "expelliarmus")
    assert comparar_hash(alohomora, "alohomora")
    assert comparar_hash(expecto_patronum, "expecto patronum")
    assert comparar_hash(sectumsempra, "sectumsempra")