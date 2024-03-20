from typing import Any, Callable, Sequence
from typing import TypeVar  # Delete when PEP 695 is ready.
from enum import Enum, IntEnum
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

    # def row_to_dict[U](self, row: tuple[U, ...]) -> dict[str, U]: # PEP 695
    def row_to_dict(self, row: tuple[_U, ...]) -> dict[str, _U]:
        if len(self) != len(row):
            raise ValueError("Column descriptions and rows do not have the same length.")
        d: dict[str, _U] = {}
        for i in range(0, len(row)):
            d[self[i]] = row[i]
        return d

    # def row_to_dict_opt[U](self, row: tuple[U, ...] | None) -> dict[str, U] | None: # PEP 695
    def row_to_dict_opt(self, row: tuple[_U, ...] | None) -> dict[str, _U] | None:
        if row is None:
            return None
        return self.row_to_dict(row)

    # def rows_to_dicts[U](self, rows: Sequence[tuple[U, ...]]) -> list[dict[str, U]]: # PEP 695
    def rows_to_dicts(self, rows: Sequence[tuple[_U, ...]]) -> list[dict[str, _U]]:
        result = []
        for row in rows:
            result.append(self.row_to_dict(row))
        return result

    # def row_to_class_lambda[U, T](self, ctor: Callable[[dict[str, U]], T], row: tuple[U, ...]) -> T: # PEP 695
    def row_to_class_lambda(self, ctor: Callable[[dict[str, _U]], _T], row: tuple[_U, ...]) -> _T:
        return ctor(self.row_to_dict(row))

    # def row_to_class[T](self, klass: type[T], row: tuple[Any, ...]) -> T: # PEP 695
    def row_to_class(self, klass: type[_T], row: tuple[Any, ...]) -> _T:
        return self.row_to_class_lambda(lambda d: from_dict(data_class = klass, data = d, config = Config(cast = [Enum, IntEnum], strict = True)), row)

    # def row_to_class_lambda_opt[U, T](self, ctor: Callable[[dict[str, U]], T], row: tuple[U, ...] | None) -> T | None: # PEP 695
    def row_to_class_lambda_opt(self, ctor: Callable[[dict[str, _U]], _T], row: tuple[_U, ...] | None) -> _T | None:
        if row is None:
            return None
        return self.row_to_class_lambda(ctor, row)

    # def row_to_class_opt[U, T](self, klass: type[T], row: tuple[U, ...] | None) -> T | None: # PEP 695
    def row_to_class_opt(self, klass: type[_T], row: tuple[_U, ...] | None) -> _T | None:
        if row is None:
            return None
        return self.row_to_class(klass, row)

    # def rows_to_classes_lambda[U, T](self, ctor: Callable[[dict[str, U]], T], rows: Sequence[tuple[U, ...]]) -> list[T]: # PEP 695
    def rows_to_classes_lambda(self, ctor: Callable[[dict[str, _U]], _T], rows: Sequence[tuple[_U, ...]]) -> list[_T]:
        result = []
        for row in rows:
            result.append(self.row_to_class_lambda(ctor, row))
        return result

    # def rows_to_classes[U, T](self, klass: type[T], rows: Sequence[tuple[U, ...]]) -> list[T]: # PEP 695
    def rows_to_classes(self, klass: type[_T], rows: Sequence[tuple[_U, ...]]) -> list[_T]:
        result = []
        for row in rows:
            result.append(self.row_to_class(klass, row))
        return result
