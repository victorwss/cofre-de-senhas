from typing import Any, Callable, cast, Iterator, Literal, Self, Sequence, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate # pip install dataclass_type_validator
from dacite import from_dict
from types import TracebackType
from functools import wraps
from enum import Enum
import threading

__all__ = [
    "row_to_dict", "row_to_dict_opt", "rows_to_dicts", "row_to_class", "row_to_class_opt", "rows_to_classes",
    "TypeCode", "ColumnDescriptor", "Descriptor", "ScrollMode",
    "SimpleConnection", "TransactedConnection", "TransactionNotActiveException",
]

T = TypeVar("T")
C = TypeVar("C", bound = Callable[..., Any])

class ScrollMode(Enum):
    Relative = "relative"
    Absolute = "absolute"

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

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class ColumnDescriptor:
    name         : str
    type_code    : TypeCode
    display_size : int | None
    internal_size: int | None
    precision    : int | None
    scale        : int | None
    null_ok      : bool | None

    @staticmethod
    def create( \
            name: str, \
            type_code: TypeCode, \
            display_size: int | None = None, \
            internal_size: int | None = None, \
            precision: int | None = None, \
            scale: int | None = None, \
            null_ok: bool | None = None, \
    ) -> ColumnDescriptor:
        return ColumnDescriptor(name, type_code, display_size, internal_size, precision, scale, null_ok)

Descriptor = list[ColumnDescriptor]

def row_to_dict(description: Descriptor, row: tuple[Any, ...]) -> dict[str, Any]:
    d = {}
    for i in range(0, len(row)):
        d[description[i].name] = row[i]
    return d

def row_to_dict_opt(description: Descriptor, row: tuple[Any, ...] | None) -> dict[str, Any] | None:
    if row is None: return None
    return row_to_dict(description, row)

def rows_to_dicts(description: Descriptor, rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        result.append(row_to_dict(description, row))
    return result

def row_to_class(klass: type[T], description: Descriptor, row: tuple[Any, ...]) -> T:
    return from_dict(data_class = klass, data = row_to_dict(description, row))

def row_to_class_opt(klass: type[T], description: Descriptor, row: tuple[Any, ...] | None) -> T | None:
    if row is None: return None
    return row_to_class(klass, description, row)

def rows_to_classes(klass: type[T], description: Descriptor, rows: list[tuple[Any, ...]]) -> list[T]:
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
    def fetchall(self) -> list[tuple[Any, ...]]:
        ...

    @abstractmethod
    def fetchmany(self, size: int = 0) -> list[tuple[Any, ...]]:
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
    def rownumber(self) -> int | None:
        ...

    @property
    @abstractmethod
    def lastrowid(self) -> int | None:
        ...

    @property
    @abstractmethod
    def autocommit(self) -> bool:
        ...

    @abstractmethod
    def scroll(self, value: int, mode: ScrollMode = ...) -> Self:
        ...

    @property
    def messages(self) -> Sequence[str]:
        return self._get_messages()

    @messages.deleter
    def messages(self) -> None:
        self._delete_messages()

    @abstractmethod
    def _get_messages(self) -> Sequence[str]:
        ...

    @abstractmethod
    def _delete_messages(self) -> None:
        ...

    def next(self) -> tuple[Any, ...] | None:
        return self.fetchone()

    def __next__(self) -> tuple[Any, ...] | None:
        return self.fetchone()

    def __iter__(self) -> Iterator[tuple[Any, ...] | None]:
        yield self.fetchone()

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

    def transact(self, operation: C) -> C:
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
        return cast(C, transacted_operation)

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

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self.__wrapped.fetchall()

    def fetchmany(self, size: int = 0) -> list[tuple[Any, ...]]:
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

    def scroll(self, value: int, mode: ScrollMode = ScrollMode.Relative) -> Self:
        self.__wrapped.scroll(value, mode)
        return self

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
    def rownumber(self) -> int | None:
        return self.__wrapped.rownumber

    @property
    def lastrowid(self) -> int | None:
        return self.__wrapped.lastrowid

    @property
    def autocommit(self) -> bool:
        return self.__wrapped.autocommit

    def _get_messages(self) -> Sequence[str]:
        return self.__wrapped.messages

    def _delete_messages(self) -> None:
        del self.__wrapped.messages

del C
del T