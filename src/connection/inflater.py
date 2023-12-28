from typing import Any, Callable, Sequence
from typing import TypeVar  # Delete when PEP 695 is ready.
from enum import Enum
from dacite import Config, from_dict

_T = TypeVar("_T")  # Delete when PEP 695 is ready.
_U = TypeVar("_U")  # Delete when PEP 695 is ready.


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


# def row_to_dict[U](columns: ColumnNames, row: tuple[U, ...]) -> dict[str, U]: # PEP 695
def row_to_dict(columns: ColumnNames, row: tuple[_U, ...]) -> dict[str, _U]:
    if len(columns) != len(row):
        raise ValueError("Column descriptions and rows do not have the same length.")
    d = {}
    for i in range(0, len(row)):
        d[columns[i]] = row[i]
    return d


# def row_to_dict_opt[U](columns: ColumnNames, row: tuple[U, ...] | None) -> dict[str, U] | None: # PEP 695
def row_to_dict_opt(columns: ColumnNames, row: tuple[_U, ...] | None) -> dict[str, _U] | None:
    if row is None:
        return None
    return row_to_dict(columns, row)


# def rows_to_dicts[U](columns: ColumnNames, rows: Sequence[tuple[U, ...]]) -> list[dict[str, U]]: # PEP 695
def rows_to_dicts(columns: ColumnNames, rows: Sequence[tuple[_U, ...]]) -> list[dict[str, _U]]:
    result = []
    for row in rows:
        result.append(row_to_dict(columns, row))
    return result


# def row_to_class_lambda[T, U](ctor: Callable[[dict[str, U]], T], columns: ColumnNames, row: tuple[U, ...]) -> T: # PEP 695
def row_to_class_lambda(ctor: Callable[[dict[str, _U]], _T], columns: ColumnNames, row: tuple[_U, ...]) -> _T:
    return ctor(row_to_dict(columns, row))


# def row_to_class[T](klass: type[T], columns: ColumnNames, row: tuple[Any, ...]) -> T: # PEP 695
def row_to_class(klass: type[_T], columns: ColumnNames, row: tuple[Any, ...]) -> _T:
    return row_to_class_lambda(lambda d: from_dict(data_class = klass, data = d, config = Config(cast = [Enum], strict = True)), columns, row)


# def row_to_class_lambda_opt[U, T](ctor: Callable[[dict[str, U]], T], columns: ColumnNames, row: tuple[U, ...] | None) -> T | None: # PEP 695
def row_to_class_lambda_opt(ctor: Callable[[dict[str, _U]], _T], columns: ColumnNames, row: tuple[_U, ...] | None) -> _T | None:
    if row is None:
        return None
    return row_to_class_lambda(ctor, columns, row)


# def row_to_class_opt[U, T](klass: type[T], columns: ColumnNames, row: tuple[U, ...] | None) -> T | None: # PEP 695
def row_to_class_opt(klass: type[_T], columns: ColumnNames, row: tuple[_U, ...] | None) -> _T | None:
    if row is None:
        return None
    return row_to_class(klass, columns, row)


# def rows_to_classes_lambda[U, T](ctor: Callable[[dict[str, U]], T], columns: ColumnNames, rows: Sequence[tuple[U, ...]]) -> list[T]: # PEP 695
def rows_to_classes_lambda(ctor: Callable[[dict[str, _U]], _T], columns: ColumnNames, rows: Sequence[tuple[_U, ...]]) -> list[_T]:
    result = []
    for row in rows:
        result.append(row_to_class_lambda(ctor, columns, row))
    return result


# def rows_to_classes[U, T](klass: type[T], columns: ColumnNames, rows: Sequence[tuple[U, ...]]) -> list[T]: # PEP 695
def rows_to_classes(klass: type[_T], columns: ColumnNames, rows: Sequence[tuple[_U, ...]]) -> list[_T]:
    result = []
    for row in rows:
        result.append(row_to_class(klass, columns, row))
    return result
