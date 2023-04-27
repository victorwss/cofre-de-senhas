from typing import Any, Self, Sequence, TypeVar
from .conn import ColumnDescriptor, Descriptor, SimpleConnection, Tribool, TypeCode
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from dataclasses import dataclass
from validator import dataclass_validate

__all__ = ["MySQLConnectionWrapper"]

@dataclass_validate
@dataclass(frozen = True)
class InternalCode:
    name: str
    value: int
    type: TypeCode

# See https://dev.mysql.com/doc/dev/connector-net/6.10/html/T_MySql_Data_MySqlClient_MySqlDbType.htm
# See https://mariadb-corporation.github.io/mariadb-connector-python/constants.html#module-mariadb.constants.FIELD_TYPE
__codes: list[InternalCode] = [
    InternalCode("Decimal"   ,   0, TypeCode.INTEGER ),
    InternalCode("Byte"      ,   1, TypeCode.INTEGER ), #FIELD_TYPE.TINY
    InternalCode("Int16"     ,   2, TypeCode.INTEGER ), #FIELD_TYPE.SHORT
    InternalCode("Int32"     ,   3, TypeCode.INTEGER ), #FIELD_TYPE.LONG
    InternalCode("Float"     ,   4, TypeCode.FLOAT   ), #FIELD_TYPE.FLOAT
    InternalCode("Double"    ,   5, TypeCode.FLOAT   ), #FIELD_TYPE.DOUBLE
    InternalCode("Null"      ,   6, TypeCode.NULL    ), #FIELD_TYPE.NULL
    InternalCode("Timestamp" ,   7, TypeCode.DATETIME), #FIELD_TYPE.TIMESTAMP
    InternalCode("Int64"     ,   8, TypeCode.INTEGER ), #FIELD_TYPE.LONGLONG
    InternalCode("Int24"     ,   9, TypeCode.INTEGER ), #FIELD_TYPE.INT24
    InternalCode("Date"      ,  10, TypeCode.DATE    ), #FIELD_TYPE.DATE
    InternalCode("Time"      ,  11, TypeCode.TIME    ), #FIELD_TYPE.TIME
    InternalCode("Datetime"  ,  12, TypeCode.DATETIME), #FIELD_TYPE.DATETIME
    InternalCode("Year"      ,  13, TypeCode.INTEGER ), #FIELD_TYPE.YEAR
    InternalCode("NewDate"   ,  14, TypeCode.DATETIME),
    InternalCode("VarString" ,  15, TypeCode.STRING  ), #FIELD_TYPE.VARCHAR
    InternalCode("Bit"       ,  16, TypeCode.INTEGER ), #FIELD_TYPE.BIT
    InternalCode("Json"      , 245, TypeCode.STRING  ), #FIELD_TYPE.JSON
    InternalCode("NewDecimal", 246, TypeCode.INTEGER ), #FIELD_TYPE.NEWDECIMAL
    InternalCode("Enum"      , 247, TypeCode.STRING  ), #FIELD_TYPE.ENUM
    InternalCode("Set"       , 248, TypeCode.STRING  ), #FIELD_TYPE.SET
    InternalCode("TinyBlob"  , 249, TypeCode.BINARY  ), #FIELD_TYPE.TINY_BLOB
    InternalCode("MediumBlob", 250, TypeCode.BINARY  ), #FIELD_TYPE.MEDIUM_BLOB
    InternalCode("LongBlob"  , 251, TypeCode.BINARY  ), #FIELD_TYPE.LONG_BLOB
    InternalCode("Blob"      , 252, TypeCode.BINARY  ), #FIELD_TYPE.BLOB
    InternalCode("Varchar"   , 253, TypeCode.STRING  ), #FIELD_TYPE.VAR_STRING
    InternalCode("String"    , 254, TypeCode.STRING  ), #FIELD_TYPE.STRING
    InternalCode("Geometry"  , 255, TypeCode.OTHER   ), #FIELD_TYPE.GEOMETRY
    InternalCode("UByte"     , 501, TypeCode.INTEGER ),
    InternalCode("UInt16"    , 502, TypeCode.INTEGER ),
    InternalCode("UInt32"    , 503, TypeCode.INTEGER ),
    InternalCode("UInt64"    , 508, TypeCode.INTEGER ),
    InternalCode("UInt24"    , 509, TypeCode.INTEGER ),
    InternalCode("Varbinary" , 753, TypeCode.BINARY  ),
    InternalCode("Binary"    , 754, TypeCode.BINARY  ),
    InternalCode("TinyText"  , 749, TypeCode.BINARY  ),
    InternalCode("MediumText", 750, TypeCode.BINARY  ),
    InternalCode("LongText"  , 751, TypeCode.BINARY  ),
    InternalCode("Text"      , 752, TypeCode.BINARY  ),
    InternalCode("Guid"      , 854, TypeCode.STRING  )
]

__codemap: dict[int, InternalCode] = {code.value: code for code in __codes}

def __find_code(code: int) -> InternalCode:
    return __codemap.get(code, InternalCode("Unknown", code, TypeCode.OTHER))

class MySQLConnectionWrapper(SimpleConnection):

    def __init__(self, conn: MySQLConnection) -> None:
        self.__conn: MySQLConnection = conn
        self.__curr: MySQLCursor = conn.cursor()

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()

    def close(self) -> None:
        self.__curr.close()
        self.__conn.close()

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.__curr.fetchone()

    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchall()

    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchmany(size)

    def callproc(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.callproc(sql, parameters)
        return self

    def execute(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.execute(sql, parameters)
        return self

    def executemany(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.executemany(sql, parameters)
        return self

    def executescript(self, sql: str, parameters: Sequence[Any] = ()) -> Self:
        self.__curr.execute(sql, parameters, multi = True)
        return self

    @property
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @property
    def rowcount(self) -> int:
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, int, None, None, None, None, bool | int, int, int]) -> ColumnDescriptor:
        return ColumnDescriptor.create( \
                name = k[0], \
                type_code = __find_code(k[1]).type, \
                column_type_name = __find_code(k[1]).name, \
                null_ok = Tribool.YES if k[6] not in [False, 0] else Tribool.NO, \
        )

    @property
    def description(self) -> Descriptor:
        if self.__curr.description is None: return []
        return [self.__make_descriptor(k) for k in self.__curr.description]

    @property
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    def raw_connection(self) -> MySQLConnection:
        return self.__conn

    @property
    def raw_cursor(self) -> MySQLCursor:
        return self.__curr