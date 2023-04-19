from typing import Any, Iterator, Self, Sequence
from types import TracebackType
from mariadb.connections import Connection as MariaDBConnection

PARAMSTYLE_QMARK = 1
PARAMSTYLE_FORMAT = 2
PARAMSTYLE_PYFORMAT = 3

ROWS_ALL = -1

RESULT_TUPLE = 0
RESULT_NAMEDTUPLE = 1
RESULT_DICTIONARY = 2

# Command types
SQL_NONE = 0,
SQL_INSERT = 1
SQL_UPDATE = 2
SQL_REPLACE = 3
SQL_DELETE = 4
SQL_CALL = 5
SQL_DO = 6
SQL_SELECT = 7
SQL_OTHER = 255

ROWS_EOF = -1


class Cursor:

    def check_closed(self) -> None:
        ...

    def __init__(self, connection: MariaDBConnection, **kwargs: Any) -> None:
        ...

    def callproc(self, sp: str, data: Sequence[Any] = ...) -> None:
        ...

    def nextset(self) -> bool | None:
        ...

    def execute(self, statement: str, data: Sequence[Any] = ..., buffered: bool | None = ...) -> None:
        ...

    def executemany(self, statement: str, parameters: Sequence[Any] = ...) -> None:
        ...

    def close(self) -> None:
        ...

    def fetchone(self) -> tuple[Any, ...] | None:
        ...

    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        ...

    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        ...

    def __iter__(self) -> Iterator[tuple[Any, ...] | None]:
        ...

    def scroll(self, value: int, mode: str = ...) -> None:
        ...

    def setinputsizes(self, size: int) -> None:
        ...

    def setoutputsize(self, size: int) -> None:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        ...

    @property
    def rowcount(self) -> int:
        ...

    @property
    def sp_outparams(self) -> bool:
        ...

    @property
    def lastrowid(self) -> int:
        ...

    @property
    def connection(self) -> MariaDBConnection:
        ...

    #Defined in C:

    @property
    def rownumber(self) -> int:
        ...

    @property
    def closed(self) -> bool:
        ...

    @property
    def description(self) -> Sequence[tuple[str, int, int, int, int, int, int, int, str, str, str]]:
        ...

    @property
    def warnings(self) -> int:
        ...

    # Alias for fetchone
    def next(self) -> tuple[Any, ...] | None:
        ...

    @property
    def statement(self) -> str:
        ...

    @property
    def paramcount(self) -> int:
        ...

    @property
    def buffered(self) -> bool:
        ...

    @property
    def arraysize(self) -> int:
        ...

    @property
    def field_count(self) -> int:
        ...

    @property
    def affected_rows(self) -> int:
        ...

    @property
    def insert_id(self) -> int:
        ...