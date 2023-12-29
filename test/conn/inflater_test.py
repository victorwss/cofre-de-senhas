from typing import Any
from pytest import raises
from connection.conn import ColumnDescriptor, Descriptor, NullStatus, TypeCode
from dataclasses import dataclass
from validator import dataclass_validate
from connection.inflater import ColumnNames
from dacite.exceptions import MissingValueError, WrongTypeError, UnexpectedDataError


def make_column_descriptor(name: str) -> ColumnDescriptor:
    return ColumnDescriptor.create(
        name = name,
        type_code = TypeCode.UNSPECIFIED,
        column_type_name = "Unspecified",
        null_ok = NullStatus.DONT_KNOW
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


def test_bad_column_names() -> None:
    with raises(ValueError, match = "^Repeated column name bad_field.$"):
        ColumnNames(["bad_field", "bad_field"])


# Tests of row_to_dict


def test_row_to_dict() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: dict[str, Any] = columns.row_to_dict(row)
    assert result == {"lemon": 1, "strawberry": "xyz", "grape": 27}


def test_row_to_dict_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    result: dict[str, Any] = columns.row_to_dict(row)
    assert result == {}


def test_row_to_dict_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict(row)


def test_row_to_dict_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict(row)


def test_row_to_dict_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2, 3, 4)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict(row)


# Tests of row_to_dict_opt


def test_row_to_dict_opt() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: dict[str, Any] | None = columns.row_to_dict_opt(row)
    assert result == {"lemon": 1, "strawberry": "xyz", "grape": 27}


def test_row_to_dict_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    result: dict[str, Any] | None = columns.row_to_dict_opt(row)
    assert result == {}


def test_row_to_dict_opt_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict_opt(row)


def test_row_to_dict_opt_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict_opt(row)


def test_row_to_dict_opt_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2, 3, 4)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict_opt(row)


def test_row_to_dict_opt_none() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    assert None is columns.row_to_dict_opt(None)


# Tests of rows_to_dicts


def test_rows_to_dicts() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "xyz", 27), (5, "uvw", 55)]
    results: list[dict[str, Any]] = columns.rows_to_dicts(rows)
    assert results == [{"lemon": 1, "strawberry": "xyz", "grape": 27}, {"lemon": 5, "strawberry": "uvw", "grape": 55}]


def test_rows_to_dict_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    rows: list[tuple[Any, ...]] = []
    results: list[dict[str, Any]] = columns.rows_to_dicts(rows)
    assert results == []


def test_rows_to_dict_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict(row)


def test_rows_to_dict_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict(row)


def test_rows_to_dict_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2, 3, 4)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_dict(row)


# Tests of row_to_class


@dataclass_validate
@dataclass(frozen = True)
class FruitSalad:
    lemon: int
    strawberry: str
    grape: int


def test_row_to_class() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: FruitSalad = columns.row_to_class(FruitSalad, row)
    assert result.lemon == 1
    assert result.strawberry == "xyz"
    assert result.grape == 27


def test_row_to_class_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    with raises(MissingValueError):
        columns.row_to_class(FruitSalad, row)


def test_row_to_class_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class(FruitSalad, row)


def test_row_to_class_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz")
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class(FruitSalad, row)


def test_row_to_class_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27, 6)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class(FruitSalad, row)


def test_row_to_class_name_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "orange", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    with raises(UnexpectedDataError):
        columns.row_to_class(FruitSalad, row)


def test_row_to_class_type_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 6, 27)
    with raises(WrongTypeError):
        columns.row_to_class(FruitSalad, row)


def test_row_to_class_extra_name() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape", "orange"])
    row: tuple[Any, ...] = (1, "xyz", 27, 55)
    with raises(UnexpectedDataError):
        columns.row_to_class(FruitSalad, row)


def test_row_to_class_missing_name() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry"])
    row: tuple[Any, ...] = (1, "xyz")
    with raises(MissingValueError):
        columns.row_to_class(FruitSalad, row)


# Tests of row_to_class_opt


def test_row_to_class_opt() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: FruitSalad | None = columns.row_to_class_opt(FruitSalad, row)
    assert result == FruitSalad(1, "xyz", 27)


def test_row_to_class_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()
    with raises(MissingValueError):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2, 3, 4)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_name_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "orange", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    with raises(UnexpectedDataError):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_type_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 6, 27)
    with raises(WrongTypeError):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_extra_name() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape", "orange"])
    row: tuple[Any, ...] = (1, "xyz", 27, 55)
    with raises(UnexpectedDataError):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_missing_name() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry"])
    row: tuple[Any, ...] = (1, "xyz")
    with raises(MissingValueError):
        columns.row_to_class_opt(FruitSalad, row)


def test_row_to_class_opt_none() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    assert None is columns.row_to_class_opt(FruitSalad, None)


# Tests of row_to_class_lambda


def test_row_to_class_lambda() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "abc", 27)

    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {"lemon": 1, "strawberry": "abc", "grape": 27}
        return FruitSalad(5, "xyz", 9)

    result: FruitSalad = columns.row_to_class_lambda(make, row)
    assert result == FruitSalad(5, "xyz", 9)


def test_row_to_class_lambda_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()

    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {}
        return FruitSalad(5, "xyz", 9)

    result: FruitSalad = columns.row_to_class_lambda(make, row)
    assert result == FruitSalad(5, "xyz", 9)


def test_row_to_class_lambda_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_lambda(make, row)


def test_row_to_class_lambda_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_lambda(make, row)


def test_row_to_class_lambda_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    row: tuple[Any, ...] = (1, 2, 3, 4)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_lambda(make, row)


# Tests of row_to_class_lambda_opt


def test_row_to_class_lambda_opt() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "abc", 27)

    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {"lemon": 1, "strawberry": "abc", "grape": 27}
        return FruitSalad(5, "xyz", 9)

    result: FruitSalad | None = columns.row_to_class_lambda_opt(make, row)
    assert result == FruitSalad(5, "xyz", 9)


def test_row_to_class_lambda_opt_empty() -> None:
    columns: ColumnNames = make_columns([])
    row: tuple[Any, ...] = ()

    def make(t: dict[str, Any]) -> FruitSalad:
        assert t == {}
        return FruitSalad(5, "xyz", 9)

    result: FruitSalad | None = columns.row_to_class_lambda_opt(make, row)
    assert result == FruitSalad(5, "xyz", 9)


def test_row_to_class_lambda_opt_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = ()

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_lambda_opt(make, row)


def test_row_to_class_lambda_opt_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_lambda_opt(make, row)


def test_row_to_class_lambda_opt_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2, 3, 4)

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.row_to_class_lambda_opt(make, row)


def test_row_to_class_lambda_opt_none() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    assert None is columns.row_to_class_lambda_opt(make, None)


# Tests of rows_to_classes


def test_rows_to_classes() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27), (3, "xyz", 18), (7, "pqr", 3)]
    result: list[FruitSalad] = columns.rows_to_classes(FruitSalad, rows)
    assert result == [FruitSalad(1, "abc", 27), FruitSalad(3, "xyz", 18), FruitSalad(7, "pqr", 3)]


def test_rows_to_classes_empty() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = []
    result: list[FruitSalad] = columns.rows_to_classes(FruitSalad, rows)
    assert result == []


def test_rows_to_classes_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape", "orange"])
    rows: list[tuple[Any, ...]] = [(), (), ()]
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes(FruitSalad, rows)


def test_rows_to_classes_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "abc"), (3, "xyz"), (7, "pqr")]
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes(FruitSalad, rows)


def test_rows_to_classes_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27, "x"), (3, "xyz", 18, "y"), (7, "pqr", 3, "z")]
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes(FruitSalad, rows)


def test_rows_to_classes_name_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "orange", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27), (3, "xyz", 18), (7, "pqr", 3)]
    with raises(UnexpectedDataError):
        columns.rows_to_classes(FruitSalad, rows)


def test_rows_to_classes_type_mismatch() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, 7, 27), (3, 7, 18), (7, 56, 3)]
    with raises(WrongTypeError):
        columns.rows_to_classes(FruitSalad, rows)


def test_rows_to_classes_extra_name() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape", "orange"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27, "x"), (3, "xyz", 18, "y"), (7, "pqr", 3, "z")]
    with raises(UnexpectedDataError):
        columns.rows_to_classes(FruitSalad, rows)


def test_rows_to_classes_missing_name() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry"])
    rows: list[tuple[Any, ...]] = [(1, "abc"), (3, "xyz"), (7, "pqr")]
    with raises(MissingValueError):
        columns.rows_to_classes(FruitSalad, rows)


def test_rows_to_classes_mixed_data() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27), (3, "xyz"), (7, "pqr", 3, 10)]
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes(FruitSalad, rows)


# Tests of rows_to_classes_lambda


def test_rows_to_classes_lambda() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27), (3, "xyz", 18), (7, "pqr", 33)]

    v: int = 0
    r: list[dict[str, Any]] = [
        {"lemon": 1, "strawberry": "abc", "grape": 27},
        {"lemon": 3, "strawberry": "xyz", "grape": 18},
        {"lemon": 7, "strawberry": "pqr", "grape": 33},
    ]
    s: list[FruitSalad] = [FruitSalad(1, "abc", 27), FruitSalad(3, "xyz", 18), FruitSalad(7, "pqr", 33)]

    def make(t: dict[str, Any]) -> FruitSalad:
        nonlocal v
        assert t == r[v]
        try:
            return s[v]
        finally:
            v += 1

    result: list[FruitSalad] = columns.rows_to_classes_lambda(make, rows)
    assert result == s
    assert result is not s


def test_rows_to_classes_lambda_empty() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = []

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    result: list[FruitSalad] = columns.rows_to_classes_lambda(make, rows)
    assert result == []


def test_rows_to_classes_lambda_no_columns() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape", "orange"])
    rows: list[tuple[Any, ...]] = [(), (), ()]

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes_lambda(make, rows)


def test_rows_to_classes_lambda_missing_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "abc"), (3, "xyz"), (7, "pqr")]

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes_lambda(make, rows)


def test_rows_to_classes_lambda_extra_column() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27, "x"), (3, "xyz", 18, "y"), (7, "pqr", 3, "z")]

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes_lambda(make, rows)


def test_rows_to_classes_lambda_mixed_data() -> None:
    columns: ColumnNames = make_columns(["lemon", "strawberry"])
    rows: list[tuple[Any, ...]] = [(1, "abc", 27), (3, "xyz"), (7, "pqr", 3, 10)]

    def make(t: dict[str, Any]) -> FruitSalad:
        assert False

    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        columns.rows_to_classes_lambda(make, rows)
