from typing import Any, Callable, cast, override, Self, Sequence
from typing import TypeVar  # Delete when PEP 695 is ready.
from decorators.for_all import for_all_methods
from functools import wraps
from .conn import (
    BadDatabaseConfigException, ColumnDescriptor, Descriptor, FieldFlags, IntegrityViolationException,
    MisplacedOperationError, NullStatus, RAW_DATA, SimpleConnection, TypeCode, UnsupportedOperationError
)
from .trans import ConnectionData, TransactedConnection
from mariadb import connect as db_connect
from mariadb import IntegrityError, DataError
from mariadb.connections import Connection as MariaDBConnection
from mariadb.cursors import Cursor as MariaDBCursor
from mariadb.constants import FIELD_FLAG
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
    _InternalCode("Decimal"   ,   0, TypeCode.INTEGER ),                            # noqa: E202,E203,E241
    _InternalCode("Byte"      ,   1, TypeCode.INTEGER ),  # FIELD_TYPE.TINY         # noqa: E202,E203,E241
    _InternalCode("Int16"     ,   2, TypeCode.INTEGER ),  # FIELD_TYPE.SHORT        # noqa: E202,E203,E241
    _InternalCode("Int32"     ,   3, TypeCode.INTEGER ),  # FIELD_TYPE.LONG         # noqa: E202,E203,E241
    _InternalCode("Float"     ,   4, TypeCode.FLOAT   ),  # FIELD_TYPE.FLOAT        # noqa: E202,E203,E241
    _InternalCode("Double"    ,   5, TypeCode.FLOAT   ),  # FIELD_TYPE.DOUBLE       # noqa: E202,E203,E241
    _InternalCode("Null"      ,   6, TypeCode.NULL    ),  # FIELD_TYPE.NULL         # noqa: E202,E203,E241
    _InternalCode("Timestamp" ,   7, TypeCode.DATETIME),  # FIELD_TYPE.TIMESTAMP    # noqa: E202,E203,E241
    _InternalCode("Int64"     ,   8, TypeCode.INTEGER ),  # FIELD_TYPE.LONGLONG     # noqa: E202,E203,E241
    _InternalCode("Int24"     ,   9, TypeCode.INTEGER ),  # FIELD_TYPE.INT24        # noqa: E202,E203,E241
    _InternalCode("Date"      ,  10, TypeCode.DATE    ),  # FIELD_TYPE.DATE         # noqa: E202,E203,E241
    _InternalCode("Time"      ,  11, TypeCode.TIME    ),  # FIELD_TYPE.TIME         # noqa: E202,E203,E241
    _InternalCode("Datetime"  ,  12, TypeCode.DATETIME),  # FIELD_TYPE.DATETIME     # noqa: E202,E203,E241
    _InternalCode("Year"      ,  13, TypeCode.INTEGER ),  # FIELD_TYPE.YEAR         # noqa: E202,E203,E241
    _InternalCode("NewDate"   ,  14, TypeCode.DATETIME),                            # noqa: E202,E203,E241
    _InternalCode("VarString" ,  15, TypeCode.STRING  ),  # FIELD_TYPE.VARCHAR      # noqa: E202,E203,E241
    _InternalCode("Bit"       ,  16, TypeCode.INTEGER ),  # FIELD_TYPE.BIT          # noqa: E202,E203,E241
    _InternalCode("Json"      , 245, TypeCode.STRING  ),  # FIELD_TYPE.JSON         # noqa: E202,E203,E241
    _InternalCode("NewDecimal", 246, TypeCode.INTEGER ),  # FIELD_TYPE.NEWDECIMAL   # noqa: E202,E203,E241
    _InternalCode("Enum"      , 247, TypeCode.STRING  ),  # FIELD_TYPE.ENUM         # noqa: E202,E203,E241
    _InternalCode("Set"       , 248, TypeCode.STRING  ),  # FIELD_TYPE.SET          # noqa: E202,E203,E241
    _InternalCode("TinyBlob"  , 249, TypeCode.BINARY  ),  # FIELD_TYPE.TINY_BLOB    # noqa: E202,E203,E241
    _InternalCode("MediumBlob", 250, TypeCode.BINARY  ),  # FIELD_TYPE.MEDIUM_BLOB  # noqa: E202,E203,E241
    _InternalCode("LongBlob"  , 251, TypeCode.BINARY  ),  # FIELD_TYPE.LONG_BLOB    # noqa: E202,E203,E241
    _InternalCode("Blob"      , 252, TypeCode.BINARY  ),  # FIELD_TYPE.BLOB         # noqa: E202,E203,E241
    _InternalCode("Varchar"   , 253, TypeCode.STRING  ),  # FIELD_TYPE.VAR_STRING   # noqa: E202,E203,E241
    _InternalCode("String"    , 254, TypeCode.STRING  ),  # FIELD_TYPE.STRING       # noqa: E202,E203,E241
    _InternalCode("Geometry"  , 255, TypeCode.OTHER   ),  # FIELD_TYPE.GEOMETRY     # noqa: E202,E203,E241
    _InternalCode("UByte"     , 501, TypeCode.INTEGER ),                            # noqa: E202,E203,E241
    _InternalCode("UInt16"    , 502, TypeCode.INTEGER ),                            # noqa: E202,E203,E241
    _InternalCode("UInt32"    , 503, TypeCode.INTEGER ),                            # noqa: E202,E203,E241
    _InternalCode("UInt64"    , 508, TypeCode.INTEGER ),                            # noqa: E202,E203,E241
    _InternalCode("UInt24"    , 509, TypeCode.INTEGER ),                            # noqa: E202,E203,E241
    _InternalCode("Varbinary" , 753, TypeCode.BINARY  ),                            # noqa: E202,E203,E241
    _InternalCode("Binary"    , 754, TypeCode.BINARY  ),                            # noqa: E202,E203,E241
    _InternalCode("TinyText"  , 749, TypeCode.BINARY  ),                            # noqa: E202,E203,E241
    _InternalCode("MediumText", 750, TypeCode.BINARY  ),                            # noqa: E202,E203,E241
    _InternalCode("LongText"  , 751, TypeCode.BINARY  ),                            # noqa: E202,E203,E241
    _InternalCode("Text"      , 752, TypeCode.BINARY  ),                            # noqa: E202,E203,E241
    _InternalCode("Guid"      , 854, TypeCode.STRING  )                             # noqa: E202,E203,E241
]                                                                                   # noqa: E202,E203,E241


__codemap: dict[int, _InternalCode] = {code.value: code for code in __codes}


@dataclass_validate
@dataclass(frozen = True)
class MariadbConnectionData(ConnectionData):
    user: str
    password: str
    host: str
    port: int
    database: str
    connect_timeout: int

    @staticmethod
    def create(
            *,
            user: str,
            password: str,
            host: str,
            port: int = 3306,
            database: str,
            connect_timeout: int = 30
    ) -> "MariadbConnectionData":
        return MariadbConnectionData(user, password, host, port, database, connect_timeout)

    def connect(self) -> TransactedConnection:
        def make_connection() -> _MariaDBConnectionWrapper:
            try:
                return _MariaDBConnectionWrapper(db_connect(
                    user = self.user,
                    password = self.password,
                    host = self.host,
                    port = self.port,
                    database = self.database,
                    connect_timeout = self.connect_timeout
                ), self.database)
            except BaseException as x:
                raise BadDatabaseConfigException(x)
        return TransactedConnection(make_connection, "%s", "MariaDB", self.database)


def _find_code(code: int) -> _InternalCode:
    return __codemap.get(code, _InternalCode("Unknown", code, TypeCode.OTHER))


def connect(
        *,
        user: str,
        password: str,
        host: str,
        port: int = 3306,
        database: str,
        connect_timeout: int = 30
) -> TransactedConnection:
    return MariadbConnectionData.create(
        user = user,
        password = password,
        host = host,
        port = port,
        database = database,
        connect_timeout = connect_timeout
    ).connect()


@dataclass_validate
@dataclass(frozen = True)
class _Flag:
    name: str
    test: Callable[[int], bool]


def _flag_notnull      (x: int) -> bool: return (x & FIELD_FLAG.NOT_NULL      ) != 0                                           # noqa: E202,E211,E704
def _flag_nullable     (x: int) -> bool: return (x & FIELD_FLAG.NOT_NULL      ) == 0                                           # noqa: E202,E211,E704
def _flag_primary_key  (x: int) -> bool: return (x & FIELD_FLAG.PRIMARY_KEY   ) != 0                                           # noqa: E202,E211,E704
def _flag_unique_key   (x: int) -> bool: return (x & FIELD_FLAG.UNIQUE_KEY    ) != 0                                           # noqa: E202,E211,E704
def _flag_multiple_key (x: int) -> bool: return (x & FIELD_FLAG.MULTIPLE_KEY  ) != 0                                           # noqa: E202,E211,E704
def _flag_blob         (x: int) -> bool: return (x & FIELD_FLAG.BLOB          ) != 0                                           # noqa: E202,E211,E704
def _flag_unsigned     (x: int) -> bool: return (x & FIELD_FLAG.UNSIGNED      ) != 0                                           # noqa: E202,E211,E704
def _flag_zerofill     (x: int) -> bool: return (x & FIELD_FLAG.ZEROFILL      ) != 0                                           # noqa: E202,E211,E704
def _flag_binary       (x: int) -> bool: return (x & FIELD_FLAG.BINARY        ) != 0                                           # noqa: E202,E211,E704
def _flag_enum         (x: int) -> bool: return (x & FIELD_FLAG.ENUM          ) != 0                                           # noqa: E202,E211,E704
def _flag_autoincrement(x: int) -> bool: return (x & FIELD_FLAG.AUTO_INCREMENT) != 0                                           # noqa: E202,E211,E704
def _flag_timestamp    (x: int) -> bool: return (x & FIELD_FLAG.TIMESTAMP     ) != 0                                           # noqa: E202,E211,E704
def _flag_set          (x: int) -> bool: return (x & FIELD_FLAG.SET           ) != 0                                           # noqa: E202,E211,E704
def _flag_no_default   (x: int) -> bool: return (x & FIELD_FLAG.NO_DEFAULT    ) != 0                                           # noqa: E202,E211,E704
def _flag_has_default  (x: int) -> bool: return (x & FIELD_FLAG.NO_DEFAULT    ) == 0                                           # noqa: E202,E211,E704
def _flag_on_update_now(x: int) -> bool: return (x & FIELD_FLAG.ON_UPDATE_NOW ) != 0                                           # noqa: E202,E211,E704
def _flag_numeric      (x: int) -> bool: return (x & FIELD_FLAG.NUMERIC       ) != 0                                           # noqa: E202,E211,E704
# def _flag_unique     (x: int) -> bool: return (x & FIELD_FLAG.UNIQUE        ) != 0                                           # noqa: E202,E211,E704
def _flag_part_of_key  (x: int) -> bool: return (x & FIELD_FLAG.PART_OF_KEY   ) != 0                                           # noqa: E202,E211,E704
def _flag_signed       (x: int) -> bool: return (x & FIELD_FLAG.UNSIGNED      ) == 0 and (x & FIELD_FLAG.NUMERIC       ) != 0  # noqa: E202,E211,E704


__flags: list[_Flag] = [
    _Flag("Not Null"     , _flag_notnull      ),  # noqa: E202,E203
    _Flag("Nullable"     , _flag_nullable     ),  # noqa: E202,E203
    _Flag("Primary Key"  , _flag_primary_key  ),  # noqa: E202,E203
    _Flag("Unique Key"   , _flag_unique_key   ),  # noqa: E202,E203
    _Flag("Multiple Key" , _flag_multiple_key ),  # noqa: E202,E203
    _Flag("Blob"         , _flag_blob         ),  # noqa: E202,E203
    _Flag("Unsigned"     , _flag_unsigned     ),  # noqa: E202,E203
    _Flag("Zero fill"    , _flag_zerofill     ),  # noqa: E202,E203
    _Flag("Binary"       , _flag_binary       ),  # noqa: E202,E203
    _Flag("Enum"         , _flag_enum         ),  # noqa: E202,E203
    _Flag("Autoincrement", _flag_autoincrement),  # noqa: E202,E203
    _Flag("Timestamp"    , _flag_timestamp    ),  # noqa: E202,E203
    _Flag("Set"          , _flag_set          ),  # noqa: E202,E203
    _Flag("No default"   , _flag_no_default   ),  # noqa: E202,E203
    _Flag("Has default"  , _flag_has_default  ),  # noqa: E202,E203
    _Flag("On update now", _flag_on_update_now),  # noqa: E202,E203
    _Flag("Numeric"      , _flag_numeric      ),  # noqa: E202,E203
    # _Flag("Unique"     , _flag_unique       ),  # noqa: E202,E203
    _Flag("Part of key"  , _flag_part_of_key  ),  # noqa: E202,E203
    _Flag("Signed"       , _flag_signed       )   # noqa: E202,E203
]


def _find_flags(code: int) -> FieldFlags:
    result: list[str] = []
    for f in __flags:
        if f.test(code):
            result.append(f.name)
    return FieldFlags(code, frozenset(result))


_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])  # Delete when PEP 695 is ready.


# def _wrap_exceptions[T: Callable[..., Any]](operation: T) -> T: # PEP 695
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


@for_all_methods(_wrap_exceptions, even_privates = False)
class _MariaDBConnectionWrapper(SimpleConnection):

    def __init__(self, conn: MariaDBConnection, database_name: str) -> None:
        self.__conn: MariaDBConnection = conn
        self.__curr: MariaDBCursor = conn.cursor()
        self.__database_name: str = database_name
        self.__fetched: bool = False
        self.__executed: bool = False

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
        self.__fetched = False
        self.__executed = False

    @override
    def fetchone(self) -> tuple[Any, ...] | None:
        self.__fetched = True
        return self.__curr.fetchone()

    @override
    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        self.__fetched = True
        return self.__curr.fetchall()

    @override
    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        self.__fetched = True
        return self.__curr.fetchmany(size)

    @override
    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__fetched = False
        self.__executed = True
        self.__curr.callproc(sql, parameters)
        return self

    @override
    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__fetched = False
        self.__executed = True
        self.__curr.execute(sql, parameters)
        return self

    @override
    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ()) -> Self:
        self.__fetched = False
        self.__executed = True
        self.__curr.executemany(sql, parameters)
        return self

    @override
    def executescript(self, sql: str) -> Self:
        self.__fetched = False
        self.__executed = False
        raise UnsupportedOperationError("Sorry. The executescript method was not implemented yet.")
        # x: Generator[MySQLCursor, None, None] | None = self.__curr.execute(sql, multi = True)
        # if x is not None:
        #     for i in x:
        #         pass
        # return self

    @property
    @override
    def rowcount(self) -> int:
        if not self.__executed:
            raise MisplacedOperationError("rowcount shouldn't be used before execute, executemany, executescript or callproc")
        return self.__curr.rowcount

    def __make_descriptor(self, k: tuple[str, int, int, int, int, int, int, int, str, str, str]) -> ColumnDescriptor:
        code: _InternalCode = _find_code(k[1])
        return ColumnDescriptor.create(
            name                 = k[0],                                            # noqa: E221
            type_code            = code.type,                                       # noqa: E221
            column_type_name     = code.name,                                       # noqa: E221
            display_size         = k[2],                                            # noqa: E221
            internal_size        = k[3],                                            # noqa: E221
            precision            = k[4],                                            # noqa: E221
            scale                = k[5],                                            # noqa: E221
            null_ok              = NullStatus.YES if k[6] != 0 else NullStatus.NO,  # noqa: E221
            field_flags          = _find_flags(k[7]),                               # noqa: E221
            table_name           = k[8],                                            # noqa: E221
            original_column_name = k[9],                                            # noqa: E221
            original_table_name  = k[10]                                            # noqa: E221
        )

    @property
    @override
    def description(self) -> Descriptor:
        if not self.__fetched:
            raise MisplacedOperationError("description shouldn't be used before a fetcher method")
        if self.__curr.description is None:
            return Descriptor([])
        return Descriptor([self.__make_descriptor(k) for k in self.__curr.description])

    @property
    @override
    def lastrowid(self) -> int | None:
        if not self.__executed:
            raise MisplacedOperationError("lastrowid shouldn't be used before execute, executemany, executescript or callproc")
        return self.__curr.lastrowid

    @property
    @override
    def raw_connection(self) -> MariaDBConnection:
        return self.__conn

    @property
    @override
    def raw_cursor(self) -> MariaDBCursor:
        return self.__curr

    @property
    @override
    def placeholder(self) -> str:
        return "%s"

    @property
    @override
    def database_type(self) -> str:
        return "MariaDB"

    @property
    @override
    def database_name(self) -> str:
        return self.__database_name
