import sqlite3
from functools import wraps
from typing import Callable
from connection.sqlite3conn import Sqlite3ConnectionWrapper
from connection.conn import TransactedConnection
from cofre_de_senhas.bd.raiz import Raiz

class DbTestConfig:

    def __init__(self, pristine: str, sandbox: str) -> None:
        self.__pristine: str = pristine
        self.__sandbox: str = sandbox

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
                @Raiz.transact
                def innermost() -> None:
                    call_this()

                Raiz.register_sqlite(self.__sandbox)
                innermost()

            return inner
        return middle

    def new_connection(self) -> TransactedConnection:
        return TransactedConnection(lambda: Sqlite3ConnectionWrapper(sqlite3.connect(self.__sandbox)))
