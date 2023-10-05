from hasher import *

alohomora       : str = "SbhhiMEETzPiquOxabc178eb35f26c8f59981b01a11cbec48b16f6a8e2c204f4a9a1b633c9199e0b3b2a64b13e49226306bb451c57c851f3c6e872885115404cb74279db7f5372ea"
avada_kedavra   : str = "ZisNWkdEImMneIcX8ac8780d30e67df14c1afbaf256e1ee45afd1d3cf2654d154b2e9c63541a40d4132a9beed69c4a47b3f2e5612c2751cdfa3abfaed9797fe54777e2f3dfe6aaa0"
expecto_patronum: str = "sMIIsuQpzUZswvbW8bc81f083ae783d5dc4f4ae688b6d41d7c5d4b0da55bdb6f42d07453031c046ed4151d0cead5e647f307f96701e586dbb38e197222b645807f10f7b4c124d68c"
sectumsempra    : str = "VaVnCicwVrQUJaCR39f3afe61dd624f7c3fb3da1ca1249bcb938d35dce3af64910ac3341c5f15cd1bfa2f1312ed3f89ceee2b126c834176f8202f5aca0e43fd8c5eea6a036c7f9b5"
expelliarmus    : str = "VPJWqamYPZTUKxsxe79b2fdd41d88c308f2be7c92432d68c9d55ecc9fb9b277c1424d5626777b6e26067875b5a28f10d64db83e41a7537b21850d1bd8359b8e9bfe68e7acb02ff1d"

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