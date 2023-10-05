import sqlite3
from connection.trans import TransactedConnection
from connection.sqlite3conn import ConnectionData
from functools import wraps
from decorators.tracer import Logger
from decorators.single import Single
from typing import Any, Callable, cast, TypeVar

_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

class Raiz:

    def __init__(self, name: str, file: str) -> None:
        self.__name: str = name
        self.__file: str = file

    def register_sqlite(self) -> None:
        self.register(ConnectionData.create(file_name = self.__file).connect())

    def register(self, instance: TransactedConnection) -> None:
        Single.register(self.__name, lambda: instance)

    @property
    def instance(self) -> TransactedConnection:
        return cast(TransactedConnection, Single.instance(self.__name))

    def transact(self, operation: _TRANS) -> _TRANS:
        @wraps(operation)
        def transacted_operation(*args: Any, **kwargs: Any) -> Any:
            return self.instance.transact(operation)(*args, **kwargs)
        return cast(_TRANS, transacted_operation)

log: Logger = Logger.for_print_fn()

cofre: Raiz = Raiz("Raiz", "cofre.bd")