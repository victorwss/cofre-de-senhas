from typing import Any, cast, Self, Sequence, TypeVar
from conn import ColumnDescriptor, Descriptor, ScrollMode, SimpleConnection
from sqlite3 import Cursor, Connection, NotSupportedError

__all__ = ["Sqlite3Connection"]

T = TypeVar("T")

class Sqlite3Connection(SimpleConnection):

    def __init__(self, conn: Connection) -> None:
        self.__conn: Connection = conn
        self.__curr: Cursor = conn.cursor()
        self.__count: int = 0

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()

    def close(self) -> None:
        self.__conn.close()
        self.__curr.close()

    def fetchone(self) -> tuple[Any, ...] | None:
        return cast(tuple[Any, ...], self.__curr.fetchone())

    def fetchall(self) -> list[tuple[Any, ...]]:
        return cast(list[tuple[Any, ...]], self.__curr.fetchall())

    def fetchmany(self, size: int = 0) -> list[tuple[Any, ...]]:
        return cast(list[tuple[Any, ...]], self.__curr.fetchmany(size))

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

    def scroll(self, value: int, mode: ScrollMode = ScrollMode.Relative) -> None:
        raise NotSupportedError()

    @property
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @property
    def rowcount(self) -> int:
        return self.__curr.rowcount

    @property
    def description(self) -> Descriptor:
        return [ColumnDescriptor(*k) for k in self.__curr.description]

    @property
    def rownumber(self) -> int | None:
        return None

    @property
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    def autocommit(self) -> bool:
        return False

    def _get_messages(self) -> Sequence[str]:
        return ()

    def _delete_messages(self) -> None:
        pass

del T