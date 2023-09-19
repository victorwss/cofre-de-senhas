from typing import Any, TypeVar
from mariadb.connections import Connection

_T = TypeVar("_T", bound = type[Connection])

def connect(*args: Any, connectionclass: _T = ..., **kwargs: Any) -> _T:
    ...