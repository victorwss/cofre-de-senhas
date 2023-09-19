import sqlite3
from connection.trans import TransactedConnection
from connection.sqlite3conn import ConnectionData
from functools import wraps
from decorators.tracer import Logger
from decorators.single import Single
from typing import Any, Callable, cast, TypeVar

_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

class Raiz:

    def __init__(self) -> None:
        raise Exception()

    @staticmethod
    def register_sqlite(file: str) -> None:
        Raiz.register(ConnectionData.create(file_name = file).connect())

    @staticmethod
    def register(instance: TransactedConnection) -> None:
        Single.register("Raiz", lambda: instance)

    @staticmethod
    def instance() -> TransactedConnection:
        return cast(TransactedConnection, Single.instance("Raiz"))

    @staticmethod
    def transact(operation: _TRANS) -> _TRANS:
        @wraps(operation)
        def transacted_operation(*args: Any, **kwargs: Any) -> Any:
            return Raiz.instance().transact(operation)(*args, **kwargs)
        return cast(_TRANS, transacted_operation)

log = Logger.for_print_fn()