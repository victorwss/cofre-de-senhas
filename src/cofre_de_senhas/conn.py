from typing import Protocol, Tuple, TypeVar

TypeCode = STRING | BINARY | NUMBER | DATETIME | ROWID | None

T = TypeVar("T")

Descriptor = Tuple[
    str,        # name
    TypeCode,   # type_code
    int | None, # display_size
    int | None, # internal_size
    int | None, # precision
    int | None, # scale
    bool | None # null_ok
]

class SupportsClose(Protocol):

    def close(self) -> None:
        ...

class Cursor(SupportsClose, Protocol):

    def fetchone(self) -> Tuple[...] | None:
        ...

    def fetchall(self) -> list[Tuple[...]]:
        ...

    def fetchmany(self, size: int = 0) -> list[Tuple[...]]:
        ...

    def callproc(self, name: str, *parameters: Any) -> Tuple[...] | None:
        ...

    def execute(self, name: str, *parameters: Any) -> Tuple[...] | None:
        ...

    def executemany(self, name: str, *parameters: Any) -> Tuple[...] | None:
        ...

    @property
    def arraysize(self) -> int:
        ...

    @property
    def rowcount(self) -> int:
        ...

    @property
    def description(self) -> Descriptor:
        ...

    @property
    def rownumber(self) -> int:
        ...

    @property
    def lastrowid(self) -> int:
        ...

    @property
    def autocommit(self) -> bool:
        ...

    @property
    def connection(self) -> 'Connection':
        ...

    @property
    def messages(self) -> list[str]:
        ...

    @messages.deleter
    def messages(self) -> None:
        ...

    def scroll(self, value: int, mode: str = "relative") -> None:
        ...

class Connection(SupportsClose, Protocol):

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    @property
    def cursor(self) -> Cursor:
        ...

# Converte uma linha em um dicionário.
def row_to_dict(description: Descriptor, row: Tuple[...]) -> dict[str, Any]:
    if row is None: return None
    d = {}
    for i in range(0, len(row)):
        d[description[i][0]] = row[i]
    return d

# Converte uma lista de linhas em um lista de dicionários.
def rows_to_dict(description: Descriptor, rows: list[Tuple[...]]) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        result.append(row_to_dict(description, row))
    return result

# Fonte: https://stackoverflow.com/a/54769644
def dict_to_class(klass: Callable[..., T], d: dict[str, Any]) -> T:
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})
    except:
        return d # Not a dataclass field

def row_to_class(klass: Callable[..., T], description: Descriptor, row: Tuple[...]):
    dict_to_class(klass, row_to_dict(description, row))

def rows_to_classes(klass: Callable[..., T], description: Descriptor, rows: list[Tuple[...]]):
    result = []
    for row in rows:
        result.append(row_to_class(klass, description, row))
    return result

class ConexaoSimples(Connection, Cursor):

    def __init__(self, conn: Connection) -> None:
        self.__conn: Connection = conn
        self.__curr: Cursor = conn.cursor

    def close(self) -> None:
        self.__conn.close()
        self.__curr.close()

    def commit(self) -> None:
        self.__curr.commit()

    def rollback(self) -> None:
        self.__curr.rollback()

    def fetchone(self) -> Tuple[...] | None:
        return self.__curr.fetchone()

    def fetchall(self) -> list[Tuple[...]]:
        return self.__curr.fetchall()

    def fetchmany(self, size: int = 0) -> list[Tuple[...]]:
        return self.__curr.fetchmany(size)

    def callproc(self, name: str, *parameters: Any) -> Tuple[...] | None:
        return self.__curr.callproc(name, parameters)

    def execute(self, name: str, *parameters: Any) -> Tuple[...] | None:
        return self.__curr.execute(name, parameters)

    def executemany(self, name: str, *parameters: Any) -> Tuple[...] | None:
        return self.__curr.executemany(name, parameters)

    def scroll(self, value: int, mode: str = "relative") -> None:
        self.scroll(value, mode)

    @property
    def arraysize(self) -> int:
        return self.__curr.arraysize

    @property
    def rowcount(self) -> int:
        return self.__curr.rowcount

    @property
    def description(self) -> Descriptor:
        return self.__curr.description

    @property
    def rownumber(self) -> int:
        return self.__curr.rownumber

    @property
    def lastrowid(self) -> int:
        return self.__curr.lastrowid

    @property
    def autocommit(self) -> bool:
        return self.__curr.autocommit

    @property
    def connection(self) -> Connection:
        return self.__conn

    @property
    def cursor(self) -> Cursor:
        return self.__curr

    @property
    def messages(self) -> list[str]:
        return self.__conn.messages + self.__curr.messages

    @messages.deleter
    def messages(self) -> None:
        del self.__conn.messages
        del self.__curr.messages

    @property
    def connection_messages(self) -> list[str]:
        return self.__conn.messages

    @connection_messages.deleter
    def connection_messages(self) -> None:
        del self.__conn.messages

    @property
    def cursor_messages(self) -> list[str]:
        return self.__curr.messages

    @cursor_messages.deleter
    def cursor_messages(self) -> None:
        del self.__curr.messages

    def fetchone_dict(self) -> dict[str, Any]:
        row = self.fetchone()
        return row_to_dict(self.description, row)

    def fetchall_dict(self) -> list[dict[str, Any]]:
        rows = self.fetchall()
        return rows_to_dict(self.description, rows)

    def fetchmany_dict(self, size: int = 0) -> list[dict[str, Any]]:
        rows = self.fetchmany(size)
        return rows_to_dict(self.description, rows)

    def fetchone_class(self, klass: Callable[..., T]) -> T:
        row = self.fetchone()
        return row_to_class(klass, self.description, row)

    def fetchall_class(self, klass: Callable[..., T]) -> list[T]:
        rows = self.fetchall()
        return rows_to_classes(klass, self.description, rows)

    def fetchmany_class(self, klass: Callable[..., T], size: int = 0) -> list[T]:
        rows = self.fetchmany(size)
        return rows_to_classes(klass, self.description, rows)