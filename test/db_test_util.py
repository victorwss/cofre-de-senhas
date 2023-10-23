import sqlite3
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable
from connection.trans import TransactedConnection
import pytest

class DbTestConfig(ABC):

    def __init__(self, maker: Callable[[], TransactedConnection]) -> None:
        self.__maker: Callable[[], TransactedConnection] = maker
        self.__conn: TransactedConnection | None = None

    def _poor_execute_script(self, script: str) -> None:
        with self._maker() as conn:
            for part in script.split(";"):
                if part.strip() != "":
                    conn.execute(part)
            conn.commit()

    @property
    @abstractmethod
    def decorator(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        pass

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

    @property
    def _maker(self) -> Callable[[], TransactedConnection]:
        return self.__maker

    def _set_conn(self, conn: TransactedConnection) -> TransactedConnection:
        self.__conn = conn
        return conn

    def _del_conn(self) -> None:
        if self.__conn is not None: self.__conn.close()
        self.__conn = None

    @property
    def conn(self) -> TransactedConnection:
        assert self.__conn is not None
        return self.__conn

class SqliteTestConfig(DbTestConfig):

    def __init__(self, pristine: str, sandbox: str) -> None:
        def inner() -> TransactedConnection:
            from connection.sqlite3conn import connect
            return connect(sandbox)
        super().__init__(inner)
        self.__pristine: str = pristine
        self.__sandbox: str = sandbox

    @property
    def decorator(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def middle(call_this: Callable[[], None]) -> Callable[[], None]:
            @wraps(call_this)
            def inner() -> None:
                import os
                import shutil

                try:
                    os.remove(self.__sandbox)
                except FileNotFoundError as x:
                    pass

                shutil.copy2(self.__pristine, self.__sandbox)

                self._set_conn(self._maker())
                try:
                    call_this()
                finally:
                    self._del_conn()
                    os.remove(self.__sandbox)

            return inner
        return middle

class MariaDbTestConfig(DbTestConfig):

    def __init__(self, create_script: str, clear_script: str, user: str, password: str, host: str, port: int, database: str, connect_timeout: int) -> None:
        def inner() -> TransactedConnection:
            from connection.mariadbconn import connect
            return connect(user = user, password = password, host = host, port = port, database = database, connect_timeout = connect_timeout)
        super().__init__(inner)
        self.__create_script: str = create_script
        self.__clear_script: str = clear_script

    @property
    def decorator(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def middle(call_this: Callable[[], None]) -> Callable[[], None]:
            @wraps(call_this)
            def inner() -> None:
                self._poor_execute_script(self.__create_script)

                self._set_conn(self._maker())
                try:
                    call_this()
                finally:
                    self._del_conn()
                    self._poor_execute_script(self.__clear_script)

            return inner
        return middle

class MysqlTestConfig(DbTestConfig):

    def __init__(self, create_script: str, clear_script: str, user: str, password: str, host: str, port: int, database: str) -> None:
        def inner() -> TransactedConnection:
            from connection.mysqlconn import connect
            return connect(user = user, password = password, host = host, port = port, database = database)
        super().__init__(inner)
        self.__create_script: str = create_script
        self.__clear_script: str = clear_script

    @property
    def decorator(self) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def middle(call_this: Callable[[], None]) -> Callable[[], None]:
            @wraps(call_this)
            def inner() -> None:
                self._poor_execute_script(self.__create_script)

                self._set_conn(self._maker())
                try:
                    call_this()
                finally:
                    self._del_conn()
                    self._poor_execute_script(self.__clear_script)

            return inner
        return middle

def _do_nothing(which: DbTestConfig) -> None:
    pass

def applier(appliances: dict[str, DbTestConfig], pretest: Callable[[DbTestConfig], None] = _do_nothing) -> Callable[[Callable[[DbTestConfig], None]], Callable[[str], None]]:

    def outer(applied: Callable[[DbTestConfig], None]) -> Callable[[str], None]:
        @pytest.mark.parametrize("db", appliances.keys())
        def middle(db: str) -> None:
            dbc: DbTestConfig = appliances[db]
            pretest(dbc)
            @wraps(applied)
            @dbc.decorator
            def call() -> None:
                applied(dbc)
            call()
        return middle
    return outer