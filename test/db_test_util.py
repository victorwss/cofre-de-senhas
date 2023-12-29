from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, ParamSpec, TypeVar
from connection.trans import TransactedConnection
import pytest

_P = ParamSpec("_P")
_R = TypeVar("_R")


class DbTestConfig(ABC):

    def __init__(self, placeholder: str, database_type: str, database_name: str, maker: Callable[[], TransactedConnection]) -> None:
        self.__maker: Callable[[], TransactedConnection] = maker
        self.__conn: TransactedConnection | None = None
        self.__placeholder: str = placeholder
        self.__database_name: str = database_name
        self.__database_type: str = database_type

    def _poor_execute_script(self, script: str) -> None:
        with self._maker() as conn:
            for part in script.split(";"):
                if part.strip() != "":
                    conn.execute(part)
            conn.commit()

    @property
    @abstractmethod
    def decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        pass

    @property
    def transacted(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            @self.decorator
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                @self.conn.transact
                def innermost() -> _R:
                    return call_this(*args, **kwargs)
                return innermost()
            return inner
        return middle

    @property
    def _maker(self) -> Callable[[], TransactedConnection]:
        return self.__maker

    def _set_conn(self, conn: TransactedConnection) -> TransactedConnection:
        self.__conn = conn
        return conn

    def _del_conn(self) -> None:
        if self.__conn is not None:
            self.__conn.close()
        self.__conn = None

    @property
    def conn(self) -> TransactedConnection:
        assert self.__conn is not None
        return self.__conn

    @property
    def placeholder(self) -> str:
        return self.__placeholder

    @property
    def database_type(self) -> str:
        return self.__database_type

    @property
    def database_name(self) -> str:
        return self.__database_name


class SqliteTestConfig(DbTestConfig):

    def __init__(self, pristine: str, sandbox: str) -> None:
        def inner() -> TransactedConnection:
            from connection.sqlite3conn import connect
            return connect(sandbox)

        super().__init__("?", "Sqlite", "test/fruits.db", inner)
        self.__pristine: str = pristine
        self.__sandbox: str = sandbox

    @property
    def decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                import os
                import shutil

                try:
                    os.remove(self.__sandbox)
                except FileNotFoundError as x:  # noqa: F841
                    pass

                shutil.copy2(self.__pristine, self.__sandbox)

                self._set_conn(self._maker())
                try:
                    return call_this(*args, **kwargs)
                finally:
                    self._del_conn()
                    os.remove(self.__sandbox)

            return inner
        return middle


class MariaDbTestConfig(DbTestConfig):

    def __init__(self, reset_script: str, user: str, password: str, host: str, port: int, database: str, connect_timeout: int) -> None:
        def inner() -> TransactedConnection:
            from connection.mariadbconn import connect
            return connect(user = user, password = password, host = host, port = port, database = database, connect_timeout = connect_timeout)

        super().__init__("%s", "MariaDB", "test_fruits", inner)
        self.__reset_script: str = reset_script

    @property
    def decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                self._poor_execute_script(self.__reset_script)

                self._set_conn(self._maker())
                try:
                    return call_this(*args, **kwargs)
                finally:
                    self._del_conn()
                    self._poor_execute_script(self.__reset_script)

            return inner
        return middle


class MysqlTestConfig(DbTestConfig):

    def __init__(self, reset_script: str, user: str, password: str, host: str, port: int, database: str) -> None:
        def inner() -> TransactedConnection:
            from connection.mysqlconn import connect
            return connect(user = user, password = password, host = host, port = port, database = database)

        super().__init__("%s", "MySQL", "test_fruits", inner)
        self.__reset_script: str = reset_script

    @property
    def decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                self._poor_execute_script(self.__reset_script)

                self._set_conn(self._maker())
                try:
                    return call_this(*args, **kwargs)
                finally:
                    self._del_conn()
                    self._poor_execute_script(self.__reset_script)

            return inner
        return middle


def _do_nothing(which: DbTestConfig) -> None:
    pass


_A = Callable[[DbTestConfig], None]
_B = Callable[[TransactedConnection], None]
_C = Callable[[TransactedConnection, DbTestConfig], None]
_D = Callable[[str], None]
_E = dict[str, DbTestConfig]
_F = Callable[[str], None]


def applier(appliances: _E, pretest: _A = _do_nothing) -> Callable[[_A], _D]:
    def outer(applied: _A) -> _F:
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


def applier_trans(appliances: _E, pretest: _A = _do_nothing) -> Callable[[_B], _D]:
    def outer(applied: _B) -> _F:
        @applier(appliances, pretest)
        def inner(db: DbTestConfig) -> None:
            conn: TransactedConnection = db.conn
            with conn as c:
                applied(c)

        return inner
    return outer


def applier_trans2(appliances: _E, pretest: _A = _do_nothing) -> Callable[[_C], _D]:
    def outer(applied: _C) -> _F:
        @applier(appliances, pretest)
        def inner(db: DbTestConfig) -> None:
            conn: TransactedConnection = db.conn
            with conn as c:
                applied(c, db)

        return inner
    return outer
