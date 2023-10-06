import sqlite3
from connection.trans import TransactedConnection
from connection.sqlite3conn import ConnectionData
from functools import wraps
from decorators.single import Single
from typing import Any, Callable, cast, TypeVar

_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

class Raiz:

    def __init__(self, file: str) -> None:
        self.__con: TransactedConnection = ConnectionData.create(file_name = file).connect()

    @property
    def instance(self) -> TransactedConnection:
        return self.__con