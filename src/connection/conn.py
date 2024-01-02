from typing import Any, Callable, Iterator, Literal, override, Self, Sequence
from typing import TypeVar  # Delete when PEP 695 is ready.
from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from enum import Enum
from .inflater import ColumnNames
from datetime import date, time, datetime

_T = TypeVar("_T")  # Delete when PEP 695 is ready.

RAW_DATA = str | int | float | bool | None | date | time | datetime


class UnsupportedOperationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MisplacedOperationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class IntegrityViolationException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


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


class NullStatus(Enum):
    YES = "Yes"
    NO = "No"
    DONT_KNOW = "Don't know"


@dataclass_validate
@dataclass(frozen = True)
class FieldFlags:
    raw_value: int
    meanings: frozenset[str]


EMPTY_FLAGS = FieldFlags(0, frozenset())


@dataclass_validate
@dataclass(frozen = True)
class ColumnDescriptor:
    name                : str         # noqa: E203
    type_code           : TypeCode    # noqa: E203
    column_type_name    : str         # noqa: E203
    display_size        : int | None  # noqa: E203
    internal_size       : int | None  # noqa: E203
    precision           : int | None  # noqa: E203
    scale               : int | None  # noqa: E203
    null_ok             : NullStatus  # noqa: E203
    field_flags         : FieldFlags  # noqa: E203
    table_name          : str | None  # noqa: E203
    original_column_name: str | None  # noqa: E203
    original_table_name : str | None  # noqa: E203

    @staticmethod
    def create(
            *,
            name                : str,                                # noqa: E203
            type_code           : TypeCode = TypeCode.UNSPECIFIED,    # noqa: E203
            column_type_name    : str = "Unspecified",                # noqa: E203
            display_size        : int | None = None,                  # noqa: E203
            internal_size       : int | None = None,                  # noqa: E203
            precision           : int | None = None,                  # noqa: E203
            scale               : int | None = None,                  # noqa: E203
            null_ok             : NullStatus = NullStatus.DONT_KNOW,  # noqa: E203
            field_flags         : FieldFlags = EMPTY_FLAGS,           # noqa: E203
            table_name          : str | None = None,                  # noqa: E203
            original_column_name: str | None = None,                  # noqa: E203
            original_table_name : str | None = None                   # noqa: E203
    ) -> "ColumnDescriptor":
        return ColumnDescriptor(
            name,
            type_code,
            column_type_name,
            display_size,
            internal_size,
            precision,
            scale,
            null_ok,
            field_flags,
            table_name,
            original_column_name,
            original_table_name
        )


class ColumnSet:
    def __init__(self, items: list[ColumnDescriptor]) -> None:
        self.__items: list[ColumnDescriptor] = items[:]

        x: list[str] = []
        for c in items:
            if c.name in x:
                raise ValueError(f"Repeated column name {c.name}.")
            x.append(c.name)

    def __len__(self) -> int:
        return len(self.__items)

    def __getitem__(self, key: int) -> ColumnDescriptor:
        return self.__items[key]


class Descriptor:

    def __init__(self, columns: list[ColumnDescriptor]) -> None:
        self.__columns: ColumnSet = ColumnSet(columns)
        self.__column_names: ColumnNames = ColumnNames([c.name for c in columns])

    @property
    def columns(self) -> ColumnSet:
        return self.__columns

    @property
    def column_names(self) -> ColumnNames:
        return self.__column_names


class SimpleConnection(ABC, Iterator[tuple[RAW_DATA, ...]]):

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def fetchone(self) -> tuple[RAW_DATA, ...] | None:
        pass

    @abstractmethod
    def fetchall(self) -> Sequence[tuple[RAW_DATA, ...]]:
        pass

    @abstractmethod
    def fetchmany(self, size: int = 0) -> Sequence[tuple[RAW_DATA, ...]]:
        pass

    def fetchone_dict(self) -> dict[str, RAW_DATA] | None:
        t: tuple[RAW_DATA, ...] | None = self.fetchone()
        return self.column_names.row_to_dict_opt(t)

    def fetchall_dict(self) -> list[dict[str, RAW_DATA]]:
        t: Sequence[tuple[RAW_DATA, ...]] = self.fetchall()
        return self.column_names.rows_to_dicts(t)

    def fetchmany_dict(self, size: int = 0) -> list[dict[str, RAW_DATA]]:
        t: Sequence[tuple[RAW_DATA, ...]] = self.fetchmany(size)
        return self.column_names.rows_to_dicts(t)

    # def fetchone_class[T](self, klass: type[T]) -> T | None: # PEP 695
    def fetchone_class(self, klass: type[_T]) -> _T | None:
        t: tuple[RAW_DATA, ...] | None = self.fetchone()
        return self.column_names.row_to_class_opt(klass, t)

    # def fetchall_class[T](self, klass: type[T]) -> list[T]: # PEP 695
    def fetchall_class(self, klass: type[_T]) -> list[_T]:
        t: Sequence[tuple[RAW_DATA, ...]] = self.fetchall()
        return self.column_names.rows_to_classes(klass, t)

    # def fetchmany_class[T](self, klass: type[T], size: int = 0) -> list[T]: # PEP 695
    def fetchmany_class(self, klass: type[_T], size: int = 0) -> list[_T]:
        t: Sequence[tuple[RAW_DATA, ...]] = self.fetchmany(size)
        return self.column_names.rows_to_classes(klass, t)

    # def fetchone_class_lambda[T](self, ctor: Callable[[dict[str, RAW_DATA]], T]) -> T | None: # PEP 695
    def fetchone_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> _T | None:
        t: tuple[RAW_DATA, ...] | None = self.fetchone()
        return self.column_names.row_to_class_lambda_opt(ctor, t)

    # def fetchall_class_lambda[T](self, ctor: Callable[[dict[str, RAW_DATA]], T]) -> list[T]: # PEP 695
    def fetchall_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> list[_T]:
        t: Sequence[tuple[RAW_DATA, ...]] = self.fetchall()
        return self.column_names.rows_to_classes_lambda(ctor, t)

    # def fetchmany_class_lambda[T](self, ctor: Callable[[dict[str, RAW_DATA]], T], size: int = 0) -> list[T]: # PEP 695
    def fetchmany_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T], size: int = 0) -> list[_T]:
        t: Sequence[tuple[RAW_DATA, ...]] = self.fetchmany(size)
        return self.column_names.rows_to_classes_lambda(ctor, t)

    @abstractmethod
    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ...) -> Self:
        pass

    @abstractmethod
    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ...) -> Self:
        pass

    @abstractmethod
    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ...) -> Self:
        pass

    @abstractmethod
    def executescript(self, sql: str) -> Self:
        pass

    @property
    @abstractmethod
    def rowcount(self) -> int:
        pass

    @property
    @abstractmethod
    def description(self) -> Descriptor:
        pass

    @property
    def column_names(self) -> ColumnNames:
        return self.description.column_names

    @property
    @abstractmethod
    def lastrowid(self) -> int | None:
        pass

    @property
    def asserted_lastrowid(self) -> int:
        last: int | None = self.lastrowid
        assert last is not None
        return last

    def next(self) -> tuple[RAW_DATA, ...]:
        x: tuple[RAW_DATA, ...] | None = self.fetchone()
        if x is None:
            raise StopIteration
        return x

    @override
    def __next__(self) -> tuple[RAW_DATA, ...]:
        return self.next()

    @override
    def __iter__(self) -> Iterator[tuple[RAW_DATA, ...]]:
        return self

    @property
    @abstractmethod
    def raw_connection(self) -> object:
        pass

    @property
    @abstractmethod
    def raw_cursor(self) -> object:
        pass

    @property
    @abstractmethod
    def placeholder(self) -> str:
        pass

    @property
    def autocommit(self) -> Literal[False]:
        return False

    @property
    @abstractmethod
    def database_type(self) -> str:
        pass

    @property
    @abstractmethod
    def database_name(self) -> str:
        pass


class TransactionNotActiveException(Exception):
    pass


class BadDatabaseConfigException(Exception):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
