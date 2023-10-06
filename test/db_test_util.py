import sqlite3
from functools import wraps
from typing import Callable
from connection.sqlite3conn import ConnectionData
from connection.trans import TransactedConnection
from cofre_de_senhas.bd.raiz import Raiz
from decorators.single import Single

class DbTestConfig:

    def __init__(self, pristine: str, sandbox: str) -> None:
        self.__pristine: str = pristine
        self.__sandbox: str = sandbox
        self.__raiz: TransactedConnection = Raiz(sandbox).instance

    @property
    def decorator(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def middle(call_this: Callable[[], None]) -> Callable[[], None]:
            @wraps(call_this)
            def inner() -> None:
                import os
                import shutil

                def clear() -> None:
                    try:
                        os.remove(self.__sandbox)
                    except FileNotFoundError as x:
                        pass

                clear()
                shutil.copy2(self.__pristine, self.__sandbox)

                try:
                    call_this()
                finally:
                    os.remove(self.__sandbox)

            return inner
        return middle

    @property
    def transacted(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def middle(call_this: Callable[[], None]) -> Callable[[], None]:
            @wraps(call_this)
            @self.decorator
            def inner() -> None:
                @self.conn.transact
                def innermost() -> None:
                    call_this()
                innermost()

            return inner
        return middle

    def new_connection(self) -> TransactedConnection:
        return ConnectionData.create(file_name = self.__sandbox).connect()

    @property
    def conn(self) -> TransactedConnection:
        return self.__raiz