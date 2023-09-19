from typing import Any
from pytest import raises
from connection.conn import ColumnDescriptor, Descriptor, NullStatus, TypeCode
from dataclasses import dataclass
from validator import dataclass_validate
from connection.inflater import *
from dacite.exceptions import MissingValueError, WrongTypeError, UnexpectedDataError

def make_column_descriptor(name: str) -> ColumnDescriptor:
    return ColumnDescriptor.create( \
            name = name, \
            type_code = TypeCode.UNSPECIFIED, \
            column_type_name = "Unspecified", \
            null_ok = NullStatus.DONT_KNOW \
    )

def make_columns(columns: list[str]) -> ColumnNames:
    return Descriptor([make_column_descriptor(x) for x in columns]).column_names

def test_empty_descriptor() -> None:
    d: Descriptor = Descriptor([])
    assert len(d.columns) == 0
    assert len(d.column_names) == 0

def test_descriptor() -> None:
    names: list[str] = ["uni", "duni", "te", "salame", "mingue"]
    cd: list[ColumnDescriptor] = [make_column_descriptor(x) for x in names]
    d: Descriptor = Descriptor(cd)
    assert len(d.columns) == 5
    assert len(d.column_names) == 5
    for i in range(0, 5):
        assert d.columns[i] == cd[i]
        assert d.column_names[i] == names[i]

def test_bad_descriptor() -> None:
    with raises(ValueError, match = "^Repeated column name bad_field.$"):
        Descriptor([make_column_descriptor(x) for x in ["bad_field", "bad_field"]])

# ---------------

def test_row_to_dict() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: dict[str, Any] = row_to_dict(columns, row)
    assert result == {"lemon": 1, "strawberry": "xyz", "grape": 27}

def test_row_to_dict_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    result: dict[str, Any] = row_to_dict(columns, row)
    assert result == {}

def test_row_to_dict_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_dict(columns, row)

# ---------------

def test_row_to_dict_opt() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: dict[str, Any] | None = row_to_dict_opt(columns, row)
    assert result == {"lemon": 1, "strawberry": "xyz", "grape": 27}

def test_row_to_dict_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    result: dict[str, Any] | None = row_to_dict_opt(columns, row)
    assert result == {}

def test_row_to_dict_opt_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_dict_opt(columns, row)

def test_row_to_dict_opt_none() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    assert None == row_to_dict_opt(columns, None)

# ---------------

def test_rows_to_dicts() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "xyz", 27), (5, "uvw", 55)]
    results: list[dict[str, Any]] = rows_to_dicts(columns, rows)
    assert results == [{"lemon": 1, "strawberry": "xyz", "grape": 27}, {"lemon": 5, "strawberry": "uvw", "grape": 55}]

def test_rows_to_dict_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    rows: list[tuple[Any, ...]] = []
    results: list[dict[str, Any]] = rows_to_dicts(columns, rows)
    assert results == []

def test_rows_to_dict_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_dict(columns, row)

# ---------------

@dataclass_validate
@dataclass(frozen = True)
class FruitSalad:
    lemon: int
    strawberry: str
    grape: int

def test_row_to_class() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: FruitSalad = row_to_class(FruitSalad, columns, row)
    assert result.lemon == 1
    assert result.strawberry == "xyz"
    assert result.grape == 27

def test_row_to_class_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    with raises(MissingValueError):
        row_to_class(FruitSalad, columns, row)

def test_row_to_class_row_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_class(FruitSalad, columns, row)

def test_row_to_class_columns_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "orange", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    with raises(UnexpectedDataError):
        row_to_class(FruitSalad, columns, row)

def test_row_to_class_type_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 6, 27)
    with raises(WrongTypeError):
        row_to_class(FruitSalad, columns, row)

def test_row_to_class_columns_extra() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape", "orange"])
    row: tuple[Any, ...] = (1, "xyz", 27, 55)
    with raises(UnexpectedDataError):
        row_to_class(FruitSalad, columns, row)

def test_row_to_class_columns_missing() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry"])
    row: tuple[Any, ...] = (1, "xyz")
    with raises(MissingValueError):
        row_to_class(FruitSalad, columns, row)

# ---------------

def test_row_to_class_opt() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: FruitSalad | None = row_to_class_opt(FruitSalad, columns, row)
    assert result == FruitSalad(1, "xyz", 27)

def test_row_to_class_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    with raises(MissingValueError):
        row_to_class_opt(FruitSalad, columns, row)

def test_row_to_class_opt_row_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_class_opt(FruitSalad, columns, row)

def test_row_to_class_opt_columns_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "orange", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    with raises(UnexpectedDataError):
        row_to_class_opt(FruitSalad, columns, row)

def test_row_to_class_opt_type_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 6, 27)
    with raises(WrongTypeError):
        row_to_class_opt(FruitSalad, columns, row)

def test_row_to_class_opt_columns_extra() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape", "orange"])
    row: tuple[Any, ...] = (1, "xyz", 27, 55)
    with raises(UnexpectedDataError):
        row_to_class_opt(FruitSalad, columns, row)

def test_row_to_class_opt_columns_missing() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry"])
    row: tuple[Any, ...] = (1, "xyz")
    with raises(MissingValueError):
        row_to_class_opt(FruitSalad, columns, row)

def test_row_to_class_opt_none() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    assert None == row_to_class_opt(FruitSalad, columns, None)

# ---------------

def test_row_to_class_lambda() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "abc", 27)
    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {"lemon": 1, "strawberry": "abc", "grape": 27}
        return FruitSalad(5, "xyz", 9)
    result: FruitSalad = row_to_class_lambda(make, columns, row)
    assert result == FruitSalad(5, "xyz", 9)

def test_row_to_class_lambda_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {}
        return FruitSalad(5, "xyz", 9)
    result: FruitSalad = row_to_class_lambda(make, columns, row)
    assert result == FruitSalad(5, "xyz", 9)

def test_row_to_class_lambda_row_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    def make(t: dict[str, Any]) -> FruitSalad:
        assert False
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_class_lambda(make, columns, row)

# ---------------

def test_row_to_class_lambda_opt() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "abc", 27)
    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {"lemon": 1, "strawberry": "abc", "grape": 27}
        return FruitSalad(5, "xyz", 9)
    result: FruitSalad | None = row_to_class_lambda_opt(make, columns, row)
    assert result == FruitSalad(5, "xyz", 9)

def test_row_to_class_lambda_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {}
        return FruitSalad(5, "xyz", 9)
    result: FruitSalad | None = row_to_class_lambda_opt(make, columns, row)
    assert result == FruitSalad(5, "xyz", 9)

def test_row_to_class_lambda_opt_row_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    def make(t: dict[str, Any]) -> FruitSalad:
        assert False
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_class_lambda_opt(make, columns, row)

def test_row_to_class_lambda_opt_none() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    def make(t: dict[str, Any]) -> FruitSalad:
        assert False
    assert None == row_to_class_lambda_opt(make, columns, None)