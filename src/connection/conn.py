from typing import Any, Callable, cast, Iterator, Literal, Self, Sequence, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from enum import Enum
from .inflater import *
from datetime import date, time, datetime

_T = TypeVar("_T")
_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

RAW_DATA = str | int | float | bool | None | date | time | datetime

class UnsupportedOperationError(Exception):
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
    meanings : frozenset[str]

EMPTY_FLAGS = FieldFlags(0, frozenset())

@dataclass_validate
@dataclass(frozen = True)
class ColumnDescriptor:
    name                : str
    type_code           : TypeCode
    column_type_name    : str
    display_size        : int | None
    internal_size       : int | None
    precision           : int | None
    scale               : int | None
    null_ok             : NullStatus
    field_flags         : FieldFlags
    table_name          : str | None
    original_column_name: str | None
    original_table_name : str | None

    @staticmethod
    def create( \
            *, \
            name                : str, \
            type_code           : TypeCode = TypeCode.UNSPECIFIED, \
            column_type_name    : str = "Unspecified", \
            display_size        : int | None = None, \
            internal_size       : int | None = None, \
            precision           : int | None = None, \
            scale               : int | None = None, \
            null_ok             : NullStatus = NullStatus.DONT_KNOW, \
            field_flags         : FieldFlags = EMPTY_FLAGS, \
            table_name          : str | None = None, \
            original_column_name: str | None = None, \
            original_table_name : str | None = None  \
    ) -> "ColumnDescriptor":
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
                original_table_name \
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

class SimpleConnection(ABC):

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

    def fetchone_dict(self) -> dict[str, Any] | None:
        return row_to_dict_opt(self.column_names, self.fetchone())

    def fetchall_dict(self) -> list[dict[str, Any]]:
        return rows_to_dicts(self.column_names, self.fetchall())

    def fetchmany_dict(self, size: int = 0) -> list[dict[str, Any]]:
        return rows_to_dicts(self.column_names, self.fetchmany(size))

    def fetchone_class(self, klass: type[_T]) -> _T | None:
        return row_to_class_opt(klass, self.column_names, self.fetchone())

    def fetchall_class(self, klass: type[_T]) -> list[_T]:
        return rows_to_classes(klass, self.column_names, self.fetchall())

    def fetchmany_class(self, klass: type[_T], size: int = 0) -> list[_T]:
        return rows_to_classes(klass, self.column_names, self.fetchmany(size))

    def fetchone_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> _T | None:
        return row_to_class_lambda_opt(ctor, self.column_names, self.fetchone())

    def fetchall_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> list[_T]:
        return rows_to_classes_lambda(ctor, self.column_names, self.fetchall())

    def fetchmany_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T], size: int = 0) -> list[_T]:
        return rows_to_classes_lambda(ctor, self.column_names, self.fetchmany(size))

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

    def next(self) -> tuple[RAW_DATA, ...] | None:
        return self.fetchone()

    def __next__(self) -> tuple[RAW_DATA, ...] | None:
        return self.fetchone()

    def __iter__(self) -> Iterator[tuple[RAW_DATA, ...] | None]:
        yield self.fetchone()

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

class TransactionNotActiveException(Exception):
    pass