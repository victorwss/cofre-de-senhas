from pytest import raises
from connection.conn import *

def make_column_descriptor(name: str) -> ColumnDescriptor:
    return ColumnDescriptor.create( \
            name = name, \
            type_code = TypeCode.UNSPECIFIED,
            column_type_name = "Unspecified",
            null_ok = NullStatus.DONT_KNOW
    )

def make_descriptor(columns: list[str]) -> Descriptor:
    return Descriptor([make_column_descriptor(x) for x in columns])

def test_empty_descriptor() -> None:
    assert Descriptor([]).columns == []

def test_descriptor() -> None:
    names: list[str] = ["uni", "duni", "te", "salame", "mingue"]
    d: Descriptor = Descriptor([make_column_descriptor(x) for x in names])
    assert [c.name for c in d.columns] == names

def test_bad_descriptor() -> None:
    with raises(ValueError, match = "^Repeated column name bad_field.$"):
        Descriptor([make_column_descriptor(x) for x in ["bad_field", "bad_field"]])

# ---------------

def test_row_to_dict() -> None:
    descriptor: list[str] = make_descriptor(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: dict[str, Any] = row_to_dict(descriptor, row)
    assert result == {"lemon": 1, "strawberry": "xyz", "grape": 27}

def test_row_to_dict_empty() -> None:
    descriptor: list[str] = make_descriptor([])
    row: tuple[Any, ...] = ()
    result: dict[str, Any] = row_to_dict(descriptor, row)
    assert result == {}

def test_row_to_dict_mismatch() -> None:
    descriptor: list[str] = make_descriptor(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, 2)
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_dict(descriptor, row)

# ---------------

def test_row_to_dict_opt() -> None:
    descriptor: list[str] = make_descriptor(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = (1, "xyz", 27)
    result: dict[str, Any] = row_to_dict_opt(descriptor, row)
    assert result == {"lemon": 1, "strawberry": "xyz", "grape": 27}

def test_row_to_dict_opt_empty() -> None:
    descriptor: list[str] = make_descriptor([])
    row: tuple[Any, ...] = ()
    result: dict[str, Any] = row_to_dict_opt(descriptor, row)
    assert result == {}

def test_row_to_dict_opt_mismatch() -> None:
    descriptor: list[str] = make_descriptor(["lemon", "strawberry", "grape"])
    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_dict_opt(descriptor, row)

# ---------------

def test_rows_to_dicts() -> None:
    descriptor: list[str] = make_descriptor(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, "xyz", 27), (5, "uvw", 55)]
    results: list[dict[str, Any]] = rows_to_dicts(descriptor, rows)
    assert results == [{"lemon": 1, "strawberry": "xyz", "grape": 27}, {"lemon": 5, "strawberry": "uvw", "grape": 55}]

def test_rows_to_dict_opt_empty() -> None:
    descriptor: list[str] = make_descriptor([])
    rows: list[tuple[Any, ...]] = []
    results: dict[str, Any] = rows_to_dicts(descriptor, rows)
    assert results == []

def test_rows_to_dict_mismatch() -> None:
    descriptor: list[str] = make_descriptor(["lemon", "strawberry", "grape"])
    rows: list[tuple[Any, ...]] = [(1, 2)]
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_dict(descriptor, rows)