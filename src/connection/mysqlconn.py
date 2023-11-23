from typing import Any, Callable, cast, Generator, override, Self, Sequence
from typing import TypeVar # Delete when PEP 695 is ready.
from decorators.for_all import for_all_methods
from functools import wraps
from .conn import \
    BadDatabaseConfigException, ColumnDescriptor, Descriptor, \
    IntegrityViolationException, NullStatus, RAW_DATA, SimpleConnection, TypeCode, UnsupportedOperationError
from .trans import ConnectionData, TransactedConnection
from mysql.connector import connect as db_connect, IntegrityError
from mysql.connector.connection import MySQLConnection
from mysql.connector.connection_cext import CMySQLConnection
from mysql.connector.cursor import MySQLCursor
from mysql.connector.cursor_cext import CMySQLCursor
from mysql.connector.errors import DataError
from mysql.connector.types import CextEofPacketType, CextResultType
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
class MysqlConnectionData(ConnectionData):
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
    ) -> "MysqlConnectionData":
        return MysqlConnectionData(user, password, host, port, database)

    def connect(self) -> TransactedConnection:
        def make_connection() -> _MySQLConnectionWrapper:
            try:
                return _MySQLConnectionWrapper(cast(CMySQLConnection, db_connect( \
                    user = self.user, \
                    password = self.password, \
                    host = self.host, \
                    port = self.port, \
                    database = self.database \
                )), self.database)
            except BaseException as x:
                raise BadDatabaseConfigException(x)
        return TransactedConnection(make_connection, "%s", "MySQL", self.database)

def _find_code(code: int) -> _InternalCode:
    return __codemap.get(code, _InternalCode("Unknown", code, TypeCode.OTHER))

def connect( \
        *, \
        user: str, \
        password: str, \
        host: str, \
        port: int = 3306, \
        database: str, \
) -> TransactedConnection:
    return MysqlConnectionData.create(user = user, password = password, host = host, port = port, database = database).connect()

_TRANS = TypeVar("_TRANS", bound = Callable[..., Any]) # Delete when PEP 695 is ready.

#def _wrap_exceptions[T: Callable[..., Any]](operation: T) -> T: # PEP 695
def _wrap_exceptions(operation: _TRANS) -> _TRANS:

    @wraps(operation)
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            return operation(*args, **kwargs)
        except DataError as x:
            raise IntegrityViolationException(str(x))
        except IntegrityError as x:
            raise IntegrityViolationException(str(x))

    return cast(_TRANS, inner)

class _PatchMySQLCursor(CMySQLCursor):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @override
    def _handle_result(self, result: CextEofPacketType | CextResultType) -> None:
        self._last_insert_id = None # type: ignore
        super()._handle_result(result)

    @override
    def reset(self, free: bool = True) -> None:
        super().reset(free)
        self._last_insert_id: int = None # type: ignore

@for_all_methods(_wrap_exceptions, even_privates = False)
class _MySQLConnectionWrapper(SimpleConnection):

    def __init__(self, conn: CMySQLConnection, database_name: str) -> None:
        self.__conn: CMySQLConnection = conn
        self.__curr: CMySQLCursor = conn.cursor(cursor_class = _PatchMySQLCursor)
        self.__database_name: str = database_name

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
    def executescript(self, sql: str) -> Self:
        x: Generator[CMySQLCursor, None, None] | None = self.__curr.execute(sql, multi = True)
        if x is not None:
            for i in x:
                pass
        return self

    @property
    @override
    def rowcount(self) -> int:
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, int, None, None, None, None, bool | int, int, int]) -> ColumnDescriptor:
        code: _InternalCode = _find_code(k[1])
        return ColumnDescriptor.create( \
                name = k[0], \
                type_code = code.type, \
                column_type_name = code.name, \
                null_ok = NullStatus.YES if k[6] not in [False, 0] else NullStatus.NO \
        )

    @property
    @override
    def description(self) -> Descriptor:
        if self.__curr.description is None: return Descriptor([])
        return Descriptor([self.__make_descriptor(k) for k in self.__curr.description])

    @property
    @override
    def lastrowid(self) -> int | None:
        return self.__curr.lastrowid

    @property
    @override
    def raw_connection(self) -> CMySQLConnection:
        return self.__conn

    @property
    @override
    def raw_cursor(self) -> CMySQLCursor:
        return self.__curr

    @property
    @override
    def placeholder(self) -> str:
        return "%s"

    @property
    @override
    def database_type(self) -> str:
        return "MySQL"

    @property
    @override
    def database_name(self) -> str:
        return self.__database_name