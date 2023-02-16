from typing import Any, cast, Self, Sequence, TypeVar
from .conn import ColumnDescriptor, Descriptor, ScrollMode, SimpleConnection, TypeCode
from mysql.connector import NotSupportedError
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate

__all__ = ["MySQLConnectionWrapper"]

T = TypeVar("T")

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class Code:
    name: str
    value: int
    type: TypeCode

# See https://dev.mysql.com/doc/dev/connector-net/6.10/html/T_MySql_Data_MySqlClient_MySqlDbType.htm
__codes: list[Code] = [
    Code("Decimal"   ,   0, TypeCode.INTEGER ),
    Code("Byte"      ,   1, TypeCode.INTEGER ),
    Code("Int16"     ,   2, TypeCode.INTEGER ),
    Code("Int32"     ,   3, TypeCode.INTEGER ),
    Code("Float"     ,   4, TypeCode.FLOAT   ),
    Code("Double"    ,   5, TypeCode.FLOAT   ),
    Code("Null"      ,   6, TypeCode.NULL    ),
    Code("Timestamp" ,   7, TypeCode.DATETIME),
    Code("Int64"     ,   8, TypeCode.INTEGER ),
    Code("Int24"     ,   9, TypeCode.INTEGER ),
    Code("Date"      ,  10, TypeCode.DATE    ),
    Code("Time"      ,  11, TypeCode.TIME    ),
    Code("Datetime"  ,  12, TypeCode.DATETIME),
    Code("Year"      ,  13, TypeCode.INTEGER ),
    Code("NewDate"   ,  14, TypeCode.DATETIME),
    Code("VarString" ,  15, TypeCode.STRING  ),
    Code("Bit"       ,  16, TypeCode.INTEGER ),
    Code("Json"      , 245, TypeCode.STRING  ),
    Code("NewDecimal", 246, TypeCode.INTEGER ),
    Code("MyEnum"    , 247, TypeCode.STRING  ),
    Code("MySet"     , 248, TypeCode.STRING  ),
    Code("TinyBlob"  , 249, TypeCode.BINARY  ),
    Code("MediumBlob", 250, TypeCode.BINARY  ),
    Code("LongBlob"  , 251, TypeCode.BINARY  ),
    Code("Blob"      , 252, TypeCode.BINARY  ),
    Code("Varchar"   , 253, TypeCode.STRING  ),
    Code("String"    , 254, TypeCode.STRING  ),
    Code("Geometry"  , 255, TypeCode.OTHER   ),
    Code("UByte"     , 501, TypeCode.INTEGER ),
    Code("UInt16"    , 502, TypeCode.INTEGER ),
    Code("UInt32"    , 503, TypeCode.INTEGER ),
    Code("UInt64"    , 508, TypeCode.INTEGER ),
    Code("UInt24"    , 509, TypeCode.INTEGER ),
    Code("Varbinary" , 753, TypeCode.BINARY  ),
    Code("Binary"    , 754, TypeCode.BINARY  ),
    Code("TinyText"  , 749, TypeCode.BINARY  ),
    Code("MediumText", 750, TypeCode.BINARY  ),
    Code("LongText"  , 751, TypeCode.BINARY  ),
    Code("Text"      , 752, TypeCode.BINARY  ),
    Code("Guid"      , 854, TypeCode.STRING  )
]

__codemap: dict[int, TypeCode] = {code.value: code.type for code in __codes}

def __find_code(code: int) -> TypeCode:
    return __codemap.get(code, TypeCode.OTHER)

class MySQLConnectionWrapper(SimpleConnection):

    def __init__(self, conn: MySQLConnection) -> None:
        self.__conn: MySQLConnection = conn
        self.__curr: MySQLCursor = conn.cursor()
        self.__count: int = 0

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()

    def close(self) -> None:
        self.__conn.close()
        self.__curr.close()

    def fetchone(self) -> tuple[Any, ...] | None:
        return cast(tuple[Any, ...], self.__curr.fetchone())

    def fetchall(self) -> list[tuple[Any, ...]]:
        return cast(list[tuple[Any, ...]], self.__curr.fetchall())

    def fetchmany(self, size: int = 0) -> list[tuple[Any, ...]]:
        return cast(list[tuple[Any, ...]], self.__curr.fetchmany(size))

    def callproc(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.callproc(sql, parameters)
        return self

    def execute(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.execute(sql, parameters)
        return self

    def executemany(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.executemany(sql, parameters)
        return self

    def executescript(self, sql: str) -> Self:
        raise NotSupportedError()

    def scroll(self, value: int, mode: ScrollMode = ScrollMode.Relative) -> Self:
        raise NotSupportedError()

    @property
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @property
    def rowcount(self) -> int:
        return self.__curr.rowcount

    @property
    def description(self) -> Descriptor:
        if self.__curr.description is None: return []
        return [ColumnDescriptor.create(name = k[0], type_code = __find_code(k[1]), null_ok = k[6] not in [False, 0]) for k in self.__curr.description]

    @property
    def rownumber(self) -> int | None:
        return None

    @property
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    def autocommit(self) -> bool:
        return False

    def _get_messages(self) -> Sequence[str]:
        return ()

    def _delete_messages(self) -> None:
        pass

del T