from typing import Any, cast, Self, Sequence
from .conn import ColumnDescriptor, Descriptor, SimpleConnection, Tribool, TypeCode
from sqlite3 import Cursor, Connection, NotSupportedError

__all__ = ["Sqlite3ConnectionWrapper"]

class Sqlite3ConnectionWrapper(SimpleConnection):

    def __init__(self, conn: Connection) -> None:
        self.__conn: Connection = conn
        self.__curr: Cursor = conn.cursor()

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()

    def close(self) -> None:
        self.__conn.close()
        self.__curr.close()

    def fetchone(self) -> tuple[Any, ...] | None:
        return cast(tuple[Any, ...], self.__curr.fetchone())

    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchall()

    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchmany(size)

    def callproc(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        raise NotSupportedError()

    def execute(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.execute(sql, parameters)
        return self

    def executemany(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.executemany(sql, parameters)
        return self

    def executescript(self, sql: str) -> Self:
        self.__curr.executescript(sql)
        return self

    @property
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @property
    def rowcount(self) -> int:
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, None, None, None, None, None, None]) -> ColumnDescriptor:
        return ColumnDescriptor.create( \
                name = k[0], \
                type_code = TypeCode.UNSPECIFIED,
                column_type_name = "Unspecified",
                null_ok = Tribool.DONT_KNOW
        )

    @property
    def description(self) -> Descriptor:
        if self.__curr.description is None: return []
        return [self.__make_descriptor(k) for k in self.__curr.description]

    @property
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    def raw_connection(self) -> Connection:
        return self.__conn

    @property
    def raw_cursor(self) -> Cursor:
        return self.__curr