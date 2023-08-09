from typing import Any, Callable, cast, Iterator, Literal, Self, Sequence, TypeVar
from enum import Enum
from dacite import Config, from_dict

_T = TypeVar("_T")

class ColumnNames:
    def __init__(self, items: list[str]) -> None:
        self.__items: list[str] = items[:]

        x: list[str] = []
        for c in items:
            if c in x:
                raise ValueError(f"Repeated column name {c}.")
            x.append(c)

    def __len__(self) -> int:
        return len(self.__items)

    def __getitem__(self, key: int) -> str:
        return self.__items[key]

def row_to_dict(columns: ColumnNames, row: tuple[Any, ...]) -> dict[str, Any]:
    if len(columns) != len(row):
        raise ValueError("Column descriptions and rows do not have the same length.")
    d = {}
    for i in range(0, len(row)):
        d[columns[i]] = row[i]
    return d

def row_to_dict_opt(columns: ColumnNames, row: tuple[Any, ...] | None) -> dict[str, Any] | None:
    if row is None: return None
    return row_to_dict(columns, row)

def rows_to_dicts(columns: ColumnNames, rows: Sequence[tuple[Any, ...]]) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        result.append(row_to_dict(columns, row))
    return result

def row_to_class_lambda(ctor: Callable[[dict[str, Any]], _T], columns: ColumnNames, row: tuple[Any, ...]) -> _T:
    return ctor(row_to_dict(columns, row))

def row_to_class(klass: type[_T], columns: ColumnNames, row: tuple[Any, ...]) -> _T:
    return row_to_class_lambda(lambda d: from_dict(data_class = klass, data = d, config = Config(cast = [Enum], strict = True)), columns, row)

def row_to_class_lambda_opt(ctor: Callable[[dict[str, Any]], _T], columns: ColumnNames, row: tuple[Any, ...] | None) -> _T | None:
    if row is None: return None
    return row_to_class_lambda(ctor, columns, row)

def row_to_class_opt(klass: type[_T], columns: ColumnNames, row: tuple[Any, ...] | None) -> _T | None:
    if row is None: return None
    return row_to_class(klass, columns, row)

def rows_to_classes_lambda(ctor: Callable[[dict[str, Any]], _T], columns: ColumnNames, rows: Sequence[tuple[Any, ...]]) -> list[_T]:
    result = []
    for row in rows:
        result.append(row_to_class_lambda(ctor, columns, row))
    return result

def rows_to_classes(klass: type[_T], columns: ColumnNames, rows: Sequence[tuple[Any, ...]]) -> list[_T]:
    result = []
    for row in rows:
        result.append(row_to_class(klass, columns, row))
    return result