from typing import Any, Callable, cast, override, Self, Sequence, TypeVar
from decorators.for_all import for_all_methods
from functools import wraps
from .conn import ColumnDescriptor, Descriptor, IntegrityViolationException, NotImplementedError, NullStatus, RAW_DATA, SimpleConnection, TypeCode
from .trans import TransactedConnection
from sqlite3 import Connection, connect as db_connect, Cursor, IntegrityError
from dataclasses import dataclass
from validator import dataclass_validate

@dataclass_validate
@dataclass(frozen = True)
class ConnectionData:
    file_name: str

    @staticmethod
    def create( \
            *, \
            file_name: str, \
    ) -> "ConnectionData":
        return ConnectionData(file_name)

    def connect(self) -> TransactedConnection:
        def make_connection() -> _Sqlite3ConnectionWrapper:
            return _Sqlite3ConnectionWrapper(db_connect(self.file_name))
        return TransactedConnection(make_connection)

_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

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

    def __init__(self, conn: Connection) -> None:
        self.__conn: Connection = conn
        self.__curr: Cursor = conn.cursor()
        self.execute("PRAGMA foreign_keys = ON;")

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

    @override
    def fetchone(self) -> tuple[Any, ...] | None:
        return cast(tuple[Any, ...], self.__curr.fetchone())

    @override
    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchall()

    @override
    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchmany(size)

    @override
    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        raise NotImplementedError("Sorry. The callproc method was not implemented yet.")

    @override
    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__curr.execute(sql, parameters)
        return self

    @override
    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ()) -> Self:
        self.__curr.executemany(sql, parameters)
        return self

    @override
    def executescript(self, sql: str) -> Self:
        self.__curr.executescript(sql)
        return self

    @property
    @override
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @arraysize.setter
    @override
    def arraysize(self, size: int) -> None:
        self.__curr.arraysize = size

    @property
    @override
    def rowcount(self) -> int:
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, None, None, None, None, None, None]) -> ColumnDescriptor:
        return ColumnDescriptor.create(name = k[0])

    @property
    @override
    def description(self) -> Descriptor:
        if self.__curr.description is None: return Descriptor([])
        return Descriptor([self.__make_descriptor(k) for k in self.__curr.description])

    @property
    @override
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    @override
    def raw_connection(self) -> Connection:
        return self.__conn

    @property
    @override
    def raw_cursor(self) -> Cursor:
        return self.__curr