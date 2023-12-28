import hashlib


def string_random(size: int) -> str:
    import random
    import string
    letters: str = string.ascii_letters
    return "".join(random.choice(letters) for i in range(size))


def criar_hash(senha: str) -> str:
    sal: str = string_random(16)
    return sal + hashlib.sha3_512((sal + senha).encode("utf-8")).hexdigest()


def comparar_hash(hash_com_sal: str, senha: str) -> bool:
    sal: str = hash_com_sal[0:16]
    return sal + hashlib.sha3_512((sal + senha).encode("utf-8")).hexdigest() == hash_com_sal
