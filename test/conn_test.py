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
    row: tuple[Any, ...] = ()
    with raises(ValueError, match = "^Column descriptions and rows do not have the same length.$"):
        row_to_dict(descriptor, row)