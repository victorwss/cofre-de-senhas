from typing import Any, Callable, Self, Sequence, TypeVar
from .conn import ColumnDescriptor, Descriptor, SimpleConnection, Tribool, TypeCode
from mariadb.connections import Connection as MariaDBConnection
from mariadb.cursors import Cursor as MariaDBCursor
from mariadb.constants import FIELD_FLAG, FIELD_TYPE
from dataclasses import dataclass
from validator import dataclass_validate

__all__ = ["MariaDBConnectionWrapper"]

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

@dataclass_validate
@dataclass(frozen = True)
class Flag:
    name: str
    test: Callable[[int], bool]

__flags: list[Flag] = [
    Flag("Not Null"     , lambda x: (x & FIELD_FLAG.NOT_NULL      ) != 0),
    Flag("Nullable"     , lambda x: (x & FIELD_FLAG.NOT_NULL      ) == 0),
    Flag("Primary Key"  , lambda x: (x & FIELD_FLAG.PRIMARY_KEY   ) != 0),
    Flag("Unique Key"   , lambda x: (x & FIELD_FLAG.UNIQUE_KEY    ) != 0),
    Flag("Multiple Key" , lambda x: (x & FIELD_FLAG.MULTIPLE_KEY  ) != 0),
    Flag("Blob"         , lambda x: (x & FIELD_FLAG.BLOB          ) != 0),
    Flag("Unsigned"     , lambda x: (x & FIELD_FLAG.UNSIGNED      ) != 0),
    Flag("Zero fill"    , lambda x: (x & FIELD_FLAG.ZEROFILL      ) != 0),
    Flag("Binary"       , lambda x: (x & FIELD_FLAG.BINARY        ) != 0),
    Flag("Enum"         , lambda x: (x & FIELD_FLAG.ENUM          ) != 0),
    Flag("Autoincrement", lambda x: (x & FIELD_FLAG.AUTO_INCREMENT) != 0),
    Flag("Timestamp"    , lambda x: (x & FIELD_FLAG.TIMESTAMP     ) != 0),
    Flag("Set"          , lambda x: (x & FIELD_FLAG.SET           ) != 0),
    Flag("No default"   , lambda x: (x & FIELD_FLAG.NO_DEFAULT    ) != 0),
    Flag("Has default"  , lambda x: (x & FIELD_FLAG.NO_DEFAULT    ) == 0),
    Flag("On update now", lambda x: (x & FIELD_FLAG.ON_UPDATE_NOW ) != 0),
    Flag("Numeric"      , lambda x: (x & FIELD_FLAG.NUMERIC       ) != 0),
   #Flag("Unique"       , lambda x: (x & FIELD_FLAG.UNIQUE        ) != 0),
    Flag("Part of key"  , lambda x: (x & FIELD_FLAG.PART_OF_KEY   ) != 0),
    Flag("Signed"       , lambda x: (x & FIELD_FLAG.UNSIGNED      ) == 0 and (x & FIELD_FLAG.NUMERIC       ) != 0)
]

def __find_flags(code: int) -> set[Flag]:
    result: list[Flag] = []
    for f in __flags:
        if f.test(code):
            result.append(f)
    return set(result)

class MariaDBConnectionWrapper(SimpleConnection):

    def __init__(self, conn: MariaDBConnection) -> None:
        self.__conn: MariaDBConnection = conn
        self.__curr: MariaDBCursor = conn.cursor()

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()

    def close(self) -> None:
        self.__conn.close()
        self.__curr.close()

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
        raise TypeError("Sorry. Not implemented yet.")
        #self.__curr.execute(sql, parameters, multi = True)
        #return self

    @property
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @property
    def rowcount(self) -> int:
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, int, int, int, int, int, int, int, str, str, str]) -> ColumnDescriptor:
        return ColumnDescriptor.create( \
                name = k[0], \
                type_code = __find_code(k[1]).type, \
                column_type_name = __find_code(k[1]).name, \
                display_size = k[2], \
                internal_size = k[3], \
                precision = k[4], \
                scale = k[5], \
                null_ok = Tribool.YES if k[6] != 0 else Tribool.NO, \
                field_flags = k[7], \
                table_name = k[8], \
                original_column_name = k[9], \
                original_table_name = k[10] \
        )

    @property
    def description(self) -> Descriptor:
        if self.__curr.description is None: return []
        return [self.__make_descriptor(k) for k in self.__curr.description]

    @property
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    def raw_connection(self) -> MariaDBConnection:
        return self.__conn

    @property
    def raw_cursor(self) -> MariaDBCursor:
        return self.__curr