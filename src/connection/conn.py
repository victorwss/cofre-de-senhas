from typing import Any, Callable, cast, Iterator, Literal, Self, Sequence, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from dacite import from_dict
from types import TracebackType
from functools import wraps
from enum import Enum
import threading

__all__ = [
    "row_to_dict", "row_to_dict_opt", "rows_to_dicts", "row_to_class", "row_to_class_opt", "rows_to_classes",
    "TypeCode", "ColumnDescriptor", "Descriptor",
    "SimpleConnection", "TransactedConnection", "TransactionNotActiveException",
]

T = TypeVar("T")
TRANS = TypeVar("TRANS", bound = Callable[..., Any])

class TypeCode(Enum):
    STRING = "STRING"
    BINARY = "BINARY"
    BOOL = "BOOL"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    ROWID = "ROWID"
    NULL = "NULL"
    OTHER = "OTHER"
    UNSPECIFIED = "UNSPECIFIED"

class Tribool(Enum):
    YES = "Yes"
    NO = "No"
    DONT_KNOW = "Don't know"

@dataclass_validate
@dataclass(frozen = True)
class ColumnDescriptor:
    name                : str
    type_code           : TypeCode
    column_type_name    : str
    display_size        : int  | None
    internal_size       : int  | None
    precision           : int  | None
    scale               : int  | None
    null_ok             : Tribool
    field_flags         : int  | None
    table_name          : str  | None
    original_column_name: str  | None
    original_table_name : str  | None

    @staticmethod
    def create( \
            *, \
            name                : str, \
            type_code           : TypeCode, \
            column_type_name    : str, \
            display_size        : int  | None = None, \
            internal_size       : int  | None = None, \
            precision           : int  | None = None, \
            scale               : int  | None = None, \
            null_ok             : Tribool, \
            field_flags         : int  | None = None, \
            table_name          : str  | None = None, \
            original_column_name: str  | None = None, \
            original_table_name : str  | None = None, \
    ) -> ColumnDescriptor:
        return ColumnDescriptor( \
                name, \
                type_code, \
                column_type_name, \
                display_size, \
                internal_size, \
                precision, \
                scale, \
                null_ok, \
                field_flags, \
                table_name, \
                original_column_name, \
                original_table_name
        )

Descriptor = list[ColumnDescriptor]

def row_to_dict(description: Descriptor, row: tuple[Any, ...]) -> dict[str, Any]:
    d = {}
    for i in range(0, len(row)):
        d[description[i].name] = row[i]
    return d

def row_to_dict_opt(description: Descriptor, row: tuple[Any, ...] | None) -> dict[str, Any] | None:
    if row is None: return None
    return row_to_dict(description, row)

def rows_to_dicts(description: Descriptor, rows: Sequence[tuple[Any, ...]]) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        result.append(row_to_dict(description, row))
    return result

def row_to_class_lambda(ctor: Callable[[dict[str, Any]], T], description: Descriptor, row: tuple[Any, ...]) -> T:
    return ctor(row_to_dict(description, row))

def row_to_class(klass: type[T], description: Descriptor, row: tuple[Any, ...]) -> T:
    return row_to_class_lambda(lambda d: from_dict(data_class = klass, data = d), description, row)

def row_to_class_lambda_opt(ctor: Callable[[dict[str, Any]], T], description: Descriptor, row: tuple[Any, ...] | None) -> T | None:
    if row is None: return None
    return row_to_class_lambda(ctor, description, row)

def row_to_class_opt(klass: type[T], description: Descriptor, row: tuple[Any, ...] | None) -> T | None:
    if row is None: return None
    return row_to_class(klass, description, row)

def rows_to_classes_lambda(ctor: Callable[[dict[str, Any]], T], description: Descriptor, rows: Sequence[tuple[Any, ...]]) -> list[T]:
    result = []
    for row in rows:
        result.append(row_to_class_lambda(ctor, description, row))
    return result

def rows_to_classes(klass: type[T], description: Descriptor, rows: Sequence[tuple[Any, ...]]) -> list[T]:
    result = []
    for row in rows:
        result.append(row_to_class(klass, description, row))
    return result

class SimpleConnection(ABC):

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def fetchone(self) -> tuple[Any, ...] | None:
        ...

    @abstractmethod
    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        ...

    @abstractmethod
    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        ...

    def fetchone_dict(self) -> dict[str, Any] | None:
        return row_to_dict_opt(self.description, self.fetchone())

    def fetchall_dict(self) -> list[dict[str, Any]]:
        return rows_to_dicts(self.description, self.fetchall())

    def fetchmany_dict(self, size: int = 0) -> list[dict[str, Any]]:
        return rows_to_dicts(self.description, self.fetchmany(size))

    def fetchone_class(self, klass: type[T]) -> T | None:
        return row_to_class_opt(klass, self.description, self.fetchone())

    def fetchall_class(self, klass: type[T]) -> list[T]:
        return rows_to_classes(klass, self.description, self.fetchall())

    def fetchmany_class(self, klass: type[T], size: int = 0) -> list[T]:
        return rows_to_classes(klass, self.description, self.fetchmany(size))

    def fetchone_class_lambda(self, ctor: Callable[[dict[str, Any]], T]) -> T | None:
        return row_to_class_lambda_opt(ctor, self.description, self.fetchone())

    def fetchall_class_lambda(self, ctor: Callable[[dict[str, Any]], T]) -> list[T]:
        return rows_to_classes_lambda(ctor, self.description, self.fetchall())

    def fetchmany_class_lambda(self, ctor: Callable[[dict[str, Any]], T], size: int = 0) -> list[T]:
        return rows_to_classes_lambda(ctor, self.description, self.fetchmany(size))

    @abstractmethod
    def callproc(self, sql: str, parameters: Sequence[Any] = ...) -> Self:
        ...

    @abstractmethod
    def execute(self, sql: str, parameters: Sequence[Any] = ...) -> Self:
        ...

    @abstractmethod
    def executemany(self, sql: str, parameters: Sequence[Any] = ...) -> Self:
        ...

    @abstractmethod
    def executescript(self, sql: str) -> Self:
        ...

    @property
    @abstractmethod
    def arraysize(self) -> int:
        ...

    @property
    @abstractmethod
    def rowcount(self) -> int:
        ...

    @property
    @abstractmethod
    def description(self) -> Descriptor:
        ...

    @property
    @abstractmethod
    def lastrowid(self) -> int | None:
        ...

    def next(self) -> tuple[Any, ...] | None:
        return self.fetchone()

    def __next__(self) -> tuple[Any, ...] | None:
        return self.fetchone()

    def __iter__(self) -> Iterator[tuple[Any, ...] | None]:
        yield self.fetchone()

    @property
    @abstractmethod
    def raw_connection(self) -> object:
        ...

    @property
    @abstractmethod
    def raw_cursor(self) -> object:
        ...

class TransactionNotActiveException(Exception):
    pass

class TransactedConnection(SimpleConnection):
    def __init__(self, activate: Callable[[], SimpleConnection]) -> None:
        self.__activate: Callable[[], SimpleConnection] = activate
        self.__local = threading.local()
        self.__count: int = 0

    def __enter__(self) -> Self:
        if self.__count == 0:
            self.__local.con = self.__activate()
        self.__count += 1
        return self

    def close(self) -> None:
        self.__count -= 1
        if self.__count == 0:
            self.__wrapped.close()
            del self.__local.con

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> Literal[False]:
        self.close()
        return False

    @property
    def reenter_count(self) -> int:
        return self.__count

    @property
    def is_active(self) -> bool:
        return self.__count > 0

    def transact(self, operation: TRANS) -> TRANS:
        @wraps(operation)
        def transacted_operation(*args: Any, **kwargs: Any) -> Any:
            with self as xxx:
                try:
                    return operation(*args, **kwargs)
                except BaseException as x:
                    self.rollback()
                    raise x
                else:
                    self.commit()
        return cast(TRANS, transacted_operation)

    @property
    def __wrapped(self) -> SimpleConnection:
        try:
            return cast(SimpleConnection, self.__local.con)
        except AttributeError as x:
            raise TransactionNotActiveException()

    def force_close(self) -> None:
        self.__wrapped.close()

    def commit(self) -> None:
        self.__wrapped.commit()

    def rollback(self) -> None:
        self.__wrapped.rollback()

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.__wrapped.fetchone()

    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        return self.__wrapped.fetchall()

    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        return self.__wrapped.fetchmany(size)

    def callproc(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__wrapped.callproc(sql, parameters)
        return self

    def execute(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__wrapped.execute(sql, parameters)
        return self

    def executemany(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__wrapped.executemany(sql, parameters)
        return self

    def executescript(self, sql: str) -> Self:
        self.__wrapped.executescript(sql)
        return self

    def fetchone_dict(self) -> dict[str, Any] | None:
        return self.__wrapped.fetchone_dict()

    def fetchall_dict(self) -> list[dict[str, Any]]:
        return self.__wrapped.fetchall_dict()

    def fetchmany_dict(self, size: int = 0) -> list[dict[str, Any]]:
        return self.__wrapped.fetchmany_dict(size)

    def fetchone_class(self, klass: type[T]) -> T | None:
        return self.__wrapped.fetchone_class(klass)

    def fetchall_class(self, klass: type[T]) -> list[T]:
        return self.__wrapped.fetchall_class(klass)

    def fetchmany_class(self, klass: type[T], size: int = 0) -> list[T]:
        return self.__wrapped.fetchmany_class(klass, size)

    def fetchone_class_lambda(self, ctor: Callable[[dict[str, Any]], T]) -> T | None:
        return self.__wrapped.fetchone_class_lambda(ctor)

    def fetchall_class_lambda(self, ctor: Callable[[dict[str, Any]], T]) -> list[T]:
        return self.__wrapped.fetchall_class_lambda(ctor)

    def fetchmany_class_lambda(self, ctor: Callable[[dict[str, Any]], T], size: int = 0) -> list[T]:
        return self.__wrapped.fetchmany_class_lambda(ctor, size)

    @property
    def arraysize(self) -> int:
        return self.__wrapped.arraysize

    @property
    def rowcount(self) -> int:
        return self.__wrapped.rowcount

    @property
    def description(self) -> Descriptor:
        return self.__wrapped.description

    @property
    def lastrowid(self) -> int | None:
        return self.__wrapped.lastrowid

    @property
    def raw_connection(self) -> object:
        return self.__wrapped.raw_connection

    @property
    def raw_cursor(self) -> object:
        return self.__wrapped.raw_cursor

del TRANS
del T