from typing import Any, Callable, cast, override, Self, Sequence
from typing import TypeVar  # Delete when PEP 695 is ready.
from decorators.for_all import for_all_methods
from functools import wraps
from .conn import (
    BadDatabaseConfigException, ColumnDescriptor, Descriptor,
    IntegrityViolationException, RAW_DATA, SimpleConnection, MisplacedOperationError
)
from .trans import ConnectionData, TransactedConnection
from sqlite3 import Connection, connect as db_connect, Cursor, IntegrityError
from dataclasses import dataclass
from validator import dataclass_validate


@dataclass_validate
@dataclass(frozen = True)
class SqliteConnectionData(ConnectionData):
    file_name: str

    @staticmethod
    def create(
            *,
            file_name: str,
    ) -> "SqliteConnectionData":
        return SqliteConnectionData(file_name)

    def connect(self) -> TransactedConnection:
        def make_connection() -> _Sqlite3ConnectionWrapper:
            try:
                return _Sqlite3ConnectionWrapper(db_connect(self.file_name), self.file_name)
            except BaseException as x:
                raise BadDatabaseConfigException(x)
        return TransactedConnection(make_connection, "?", "Sqlite", self.file_name)


def connect(file: str) -> TransactedConnection:
    return SqliteConnectionData.create(file_name = file).connect()


_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])  # Delete when PEP 695 is ready.


# def _wrap_exceptions[T: Callable[..., Any]](operation: T) -> T: # PEP 695
def _wrap_exceptions(operation: _TRANS) -> _TRANS:

    @wraps(operation)
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            return operation(*args, **kwargs)
        except IntegrityError as x:
            raise IntegrityViolationException(str(x))

    return cast(_TRANS, inner)


@for_all_methods(_wrap_exceptions, even_privates = False)
class _Sqlite3ConnectionWrapper(SimpleConnection):

    def __init__(self, conn: Connection, file_name: str) -> None:
        self.__conn: Connection = conn
        self.__curr: Cursor = conn.cursor()
        self.__file_name: str = file_name
        self.execute("PRAGMA foreign_keys = ON;")
        self.__fetched: bool = False
        self.__executed: bool = False

    @override
    def commit(self) -> None:
        self.__conn.commit()

    @override
    def rollback(self) -> None:
        self.__conn.rollback()

    @override
    def close(self) -> None:
        self.__curr.close()
        self.__conn.close()
        self.__fetched = False
        self.__executed = False

    @override
    def fetchone(self) -> tuple[Any, ...] | None:
        self.__fetched = True
        return cast(tuple[Any, ...], self.__curr.fetchone())

    @override
    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        self.__fetched = True
        return self.__curr.fetchall()

    @override
    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        self.__fetched = True
        return self.__curr.fetchmany(size)

    @override
    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        raise NotImplementedError("Sorry. The callproc method was not implemented yet.")

    @override
    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__fetched = False
        self.__executed = True
        self.__curr.execute(sql, parameters)
        return self

    @override
    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ()) -> Self:
        self.__fetched = False
        self.__executed = True
        self.__curr.executemany(sql, parameters)
        return self

    @override
    def executescript(self, sql: str) -> Self:
        self.__fetched = False
        self.__executed = True
        self.__curr.executescript(sql)
        return self

    @property
    @override
    def rowcount(self) -> int:
        if not self.__executed:
            raise MisplacedOperationError("rowcount shouldn't be used before execute, executemany, executescript or callproc")
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, None, None, None, None, None, None]) -> ColumnDescriptor:
        return ColumnDescriptor.create(name = k[0])

    @property
    @override
    def description(self) -> Descriptor:
        if not self.__fetched:
            raise MisplacedOperationError("description shouldn't be used before a fetcher method")
        if self.__curr.description is None:
            return Descriptor([])
        return Descriptor([self.__make_descriptor(k) for k in self.__curr.description])

    @property
    @override
    def lastrowid(self) -> int | None:
        if not self.__executed:
            raise MisplacedOperationError("lastrowid shouldn't be used before execute, executemany, executescript or callproc")
        return self.__curr.lastrowid

    @property
    @override
    def raw_connection(self) -> Connection:
        return self.__conn

    @property
    @override
    def raw_cursor(self) -> Cursor:
        return self.__curr

    @property
    @override
    def placeholder(self) -> str:
        return "?"

    @property
    @override
    def database_type(self) -> str:
        return "Sqlite"

    @property
    @override
    def database_name(self) -> str:
        return self.__file_name
