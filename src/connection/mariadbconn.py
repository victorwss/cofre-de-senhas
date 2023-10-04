from typing import Any, Callable, cast, override, Self, Sequence, TypeVar
from decorators.for_all import for_all_methods
from functools import wraps
from .conn import ColumnDescriptor, Descriptor, FieldFlags, IntegrityViolationException, NotImplementedError, NullStatus, RAW_DATA, SimpleConnection, TypeCode
from .trans import TransactedConnection
from mariadb import connect as db_connect
from mariadb.errors import IntegrityError
from mariadb.connections import Connection as MariaDBConnection
from mariadb.cursors import Cursor as MariaDBCursor
from mariadb.constants import FIELD_FLAG, FIELD_TYPE
from dataclasses import dataclass
from validator import dataclass_validate

@dataclass_validate
@dataclass(frozen = True)
class _InternalCode:
    name: str
    value: int
    type: TypeCode

# See https://dev.mysql.com/doc/dev/connector-net/6.10/html/T_MySql_Data_MySqlClient_MySqlDbType.htm
# See https://mariadb-corporation.github.io/mariadb-connector-python/constants.html#module-mariadb.constants.FIELD_TYPE
__codes: list[_InternalCode] = [
    _InternalCode("Decimal"   ,   0, TypeCode.INTEGER ),
    _InternalCode("Byte"      ,   1, TypeCode.INTEGER ), #FIELD_TYPE.TINY
    _InternalCode("Int16"     ,   2, TypeCode.INTEGER ), #FIELD_TYPE.SHORT
    _InternalCode("Int32"     ,   3, TypeCode.INTEGER ), #FIELD_TYPE.LONG
    _InternalCode("Float"     ,   4, TypeCode.FLOAT   ), #FIELD_TYPE.FLOAT
    _InternalCode("Double"    ,   5, TypeCode.FLOAT   ), #FIELD_TYPE.DOUBLE
    _InternalCode("Null"      ,   6, TypeCode.NULL    ), #FIELD_TYPE.NULL
    _InternalCode("Timestamp" ,   7, TypeCode.DATETIME), #FIELD_TYPE.TIMESTAMP
    _InternalCode("Int64"     ,   8, TypeCode.INTEGER ), #FIELD_TYPE.LONGLONG
    _InternalCode("Int24"     ,   9, TypeCode.INTEGER ), #FIELD_TYPE.INT24
    _InternalCode("Date"      ,  10, TypeCode.DATE    ), #FIELD_TYPE.DATE
    _InternalCode("Time"      ,  11, TypeCode.TIME    ), #FIELD_TYPE.TIME
    _InternalCode("Datetime"  ,  12, TypeCode.DATETIME), #FIELD_TYPE.DATETIME
    _InternalCode("Year"      ,  13, TypeCode.INTEGER ), #FIELD_TYPE.YEAR
    _InternalCode("NewDate"   ,  14, TypeCode.DATETIME),
    _InternalCode("VarString" ,  15, TypeCode.STRING  ), #FIELD_TYPE.VARCHAR
    _InternalCode("Bit"       ,  16, TypeCode.INTEGER ), #FIELD_TYPE.BIT
    _InternalCode("Json"      , 245, TypeCode.STRING  ), #FIELD_TYPE.JSON
    _InternalCode("NewDecimal", 246, TypeCode.INTEGER ), #FIELD_TYPE.NEWDECIMAL
    _InternalCode("Enum"      , 247, TypeCode.STRING  ), #FIELD_TYPE.ENUM
    _InternalCode("Set"       , 248, TypeCode.STRING  ), #FIELD_TYPE.SET
    _InternalCode("TinyBlob"  , 249, TypeCode.BINARY  ), #FIELD_TYPE.TINY_BLOB
    _InternalCode("MediumBlob", 250, TypeCode.BINARY  ), #FIELD_TYPE.MEDIUM_BLOB
    _InternalCode("LongBlob"  , 251, TypeCode.BINARY  ), #FIELD_TYPE.LONG_BLOB
    _InternalCode("Blob"      , 252, TypeCode.BINARY  ), #FIELD_TYPE.BLOB
    _InternalCode("Varchar"   , 253, TypeCode.STRING  ), #FIELD_TYPE.VAR_STRING
    _InternalCode("String"    , 254, TypeCode.STRING  ), #FIELD_TYPE.STRING
    _InternalCode("Geometry"  , 255, TypeCode.OTHER   ), #FIELD_TYPE.GEOMETRY
    _InternalCode("UByte"     , 501, TypeCode.INTEGER ),
    _InternalCode("UInt16"    , 502, TypeCode.INTEGER ),
    _InternalCode("UInt32"    , 503, TypeCode.INTEGER ),
    _InternalCode("UInt64"    , 508, TypeCode.INTEGER ),
    _InternalCode("UInt24"    , 509, TypeCode.INTEGER ),
    _InternalCode("Varbinary" , 753, TypeCode.BINARY  ),
    _InternalCode("Binary"    , 754, TypeCode.BINARY  ),
    _InternalCode("TinyText"  , 749, TypeCode.BINARY  ),
    _InternalCode("MediumText", 750, TypeCode.BINARY  ),
    _InternalCode("LongText"  , 751, TypeCode.BINARY  ),
    _InternalCode("Text"      , 752, TypeCode.BINARY  ),
    _InternalCode("Guid"      , 854, TypeCode.STRING  )
]

__codemap: dict[int, _InternalCode] = {code.value: code for code in __codes}

@dataclass_validate
@dataclass(frozen = True)
class ConnectionData:
    user: str
    password: str
    host: str
    port: int
    database: str

    @staticmethod
    def create( \
            *, \
            user: str, \
            password: str, \
            host: str, \
            port: int = 3306, \
            database: str, \
    ) -> "ConnectionData":
        return ConnectionData(user, password, host, port, database)

    def connect(self) -> TransactedConnection:
        def mangle(*, user: str, pasword: str, host: str, port: int, database: str) -> MariaDBConnection:
            assert False

        def make_connection() -> _MariaDBConnectionWrapper:
            return _MariaDBConnectionWrapper(db_connect( \
                user = self.user, \
                password = self.password, \
                host = self.host, \
                port = self.port, \
                database = self.database \
            ))
        return TransactedConnection(make_connection)

def _find_code(code: int) -> _InternalCode:
    return __codemap.get(code, _InternalCode("Unknown", code, TypeCode.OTHER))

@dataclass_validate
@dataclass(frozen = True)
class _Flag:
    name: str
    test: Callable[[int], bool]

__flags: list[_Flag] = [
    _Flag("Not Null"     , lambda x: (x & FIELD_FLAG.NOT_NULL      ) != 0),
    _Flag("Nullable"     , lambda x: (x & FIELD_FLAG.NOT_NULL      ) == 0),
    _Flag("Primary Key"  , lambda x: (x & FIELD_FLAG.PRIMARY_KEY   ) != 0),
    _Flag("Unique Key"   , lambda x: (x & FIELD_FLAG.UNIQUE_KEY    ) != 0),
    _Flag("Multiple Key" , lambda x: (x & FIELD_FLAG.MULTIPLE_KEY  ) != 0),
    _Flag("Blob"         , lambda x: (x & FIELD_FLAG.BLOB          ) != 0),
    _Flag("Unsigned"     , lambda x: (x & FIELD_FLAG.UNSIGNED      ) != 0),
    _Flag("Zero fill"    , lambda x: (x & FIELD_FLAG.ZEROFILL      ) != 0),
    _Flag("Binary"       , lambda x: (x & FIELD_FLAG.BINARY        ) != 0),
    _Flag("Enum"         , lambda x: (x & FIELD_FLAG.ENUM          ) != 0),
    _Flag("Autoincrement", lambda x: (x & FIELD_FLAG.AUTO_INCREMENT) != 0),
    _Flag("Timestamp"    , lambda x: (x & FIELD_FLAG.TIMESTAMP     ) != 0),
    _Flag("Set"          , lambda x: (x & FIELD_FLAG.SET           ) != 0),
    _Flag("No default"   , lambda x: (x & FIELD_FLAG.NO_DEFAULT    ) != 0),
    _Flag("Has default"  , lambda x: (x & FIELD_FLAG.NO_DEFAULT    ) == 0),
    _Flag("On update now", lambda x: (x & FIELD_FLAG.ON_UPDATE_NOW ) != 0),
    _Flag("Numeric"      , lambda x: (x & FIELD_FLAG.NUMERIC       ) != 0),
   #_Flag("Unique"       , lambda x: (x & FIELD_FLAG.UNIQUE        ) != 0),
    _Flag("Part of key"  , lambda x: (x & FIELD_FLAG.PART_OF_KEY   ) != 0),
    _Flag("Signed"       , lambda x: (x & FIELD_FLAG.UNSIGNED      ) == 0 and (x & FIELD_FLAG.NUMERIC       ) != 0)
]

def _find_flags(code: int) -> FieldFlags:
    result: list[str] = []
    for f in __flags:
        if f.test(code):
            result.append(f.name)
    return FieldFlags(code, frozenset(result))

_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

def _wrap_exceptions(operation: _TRANS) -> _TRANS:

    @wraps(operation)
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            return operation(*args, **kwargs)
        except IntegrityError as x:
            raise IntegrityViolationException(str(x))

    return cast(_TRANS, inner)

@for_all_methods(_wrap_exceptions, even_privates = False)
class _MariaDBConnectionWrapper(SimpleConnection):

    def __init__(self, conn: MariaDBConnection) -> None:
        self.__conn: MariaDBConnection = conn
        self.__curr: MariaDBCursor = conn.cursor()

    @override
    def commit(self) -> None:
        self.__conn.commit()

    @override
    def rollback(self) -> None:
        self.__conn.rollback()

    @override
    def close(self) -> None:
        self.__curr.close()
        self.__conn.close()

    @override
    def fetchone(self) -> tuple[Any, ...] | None:
        return self.__curr.fetchone()

    @override
    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchall()

    @override
    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        return self.__curr.fetchmany(size)

    @override
    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__curr.callproc(sql, parameters)
        return self

    @override
    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__curr.execute(sql, parameters)
        return self

    @override
    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ()) -> Self:
        self.__curr.executemany(sql, parameters)
        return self

    @override
    def executescript(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        raise NotImplementedError("Sorry. The executescript method was not implemented yet.")
        #self.__curr.execute(sql, parameters, multi = True)
        #return self

    @property
    @override
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @arraysize.setter
    @override
    def arraysize(self, size: int) -> None:
        raise NotImplementedError("Sorry. The arraysize setter was not implemented yet.")

    @property
    @override
    def rowcount(self) -> int:
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, int, int, int, int, int, int, int, str, str, str]) -> ColumnDescriptor:
        code: _InternalCode = _find_code(k[1])
        return ColumnDescriptor.create( \
                name = k[0], \
                type_code = code.type, \
                column_type_name = code.name, \
                display_size = k[2], \
                internal_size = k[3], \
                precision = k[4], \
                scale = k[5], \
                null_ok = NullStatus.YES if k[6] != 0 else NullStatus.NO, \
                field_flags = _find_flags(k[7]), \
                table_name = k[8], \
                original_column_name = k[9], \
                original_table_name = k[10] \
        )

    @property
    @override
    def description(self) -> Descriptor:
        return Descriptor([self.__make_descriptor(k) for k in self.__curr.description])

    @property
    @override
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    @override
    def raw_connection(self) -> MariaDBConnection:
        return self.__conn

    @property
    @override
    def raw_cursor(self) -> MariaDBCursor:
        return self.__curr