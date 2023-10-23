from typing import Any, TypeVar
from mariadb.connections import Connection

_T = TypeVar("_T", bound = type[Connection])

def connect(*args: Any, connectionclass: _T = ..., **kwargs: Any) -> _T:
    ...

class IntegrityError(Exception):
    def __init__(self, msg: str) -> None:
        ...

class ProgrammingError(Exception):
    def __init__(self, msg: str) -> None:
        ...

class InternalError(Exception):
    def __init__(self, msg: str) -> None:
        ...

class DataError(Exception):
    def __init__(self, msg: str) -> None:
        ...