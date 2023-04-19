from typing import Any, Literal, Self, Sequence
from types import TracebackType
from socket import socket
from mariadb.cursors import Cursor as MariaDBCursor

class Connection:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def cursor(self, \
            cursorclass: MariaDBCursor = ..., \
            *, \
            buffered: bool = ..., \
            dictionary: bool = ..., \
            named_tuple: bool = ..., \
            cursor_type: Literal[0] | Literal[1] = ..., \
            prepared: bool = ..., \
            binary: bool = ...
    ) -> MariaDBCursor:
        ...

    def close(self) -> None:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def kill(self, id: int) -> None:
        ...

    def begin(self) -> None:
        ...

    def select_db(self, new_db: str) -> None:
        ...

    def get_server_version(self) -> tuple[int, int, int]:
        ...

    def show_warnings(self) -> Sequence[tuple[Any, ...]]:
        ...

    class xid:
        def __new__(self, format_id: int, transaction_id: str, branch_qualifier: str) -> Self:
            ...

    def tpc_begin(self, xid: xid) -> None:
        ...

    def tpc_commit(self, xid: xid | None = ...) -> None:
        ...

    def tpc_prepare(self) -> None:
        ...

    def tpc_rollback(self, xid: xid | None = ...) -> None:
        ...

    def tpc_recover(self) -> Sequence[tuple[Any, ...]]:
        ...

    @property
    def database(self) -> str:
        ...

    @database.setter
    def database(self, schema: str) -> None:
        ...

    @property
    def user(self) -> str:
        ...

    @property
    def character_set(self) -> str:
        ...

    @property
    def client_capabilities(self) -> int:
        ...

    @property
    def server_capabilities(self) -> int:
        ...

    @property
    def extended_server_capabilities(self) -> int:
        ...

    @property
    def server_port(self) -> int:
        ...

    @property
    def unix_socket(self) -> str:
        ...

    @property
    def server_name(self) -> str:
        ...

    @property
    def collation(self) -> str:
        ...

    @property
    def server_info(self) -> str:
        ...

    @property
    def tls_cipher(self) -> str:
        ...

    @property
    def tls_version(self) -> str:
        ...

    @property
    def server_status(self) -> int:
        ...

    @property
    def server_version(self) -> int:
        ...

    @property
    def server_version_info(self) -> tuple[int, int, int]:
        ...

    @property
    def autocommit(self) -> bool:
        ...

    @autocommit.setter
    def autocommit(self, mode: bool) -> None:
        ...

    @property
    def socket(self) -> socket:
        ...

    @property
    def open(self) -> bool:
        ...

    # Aliases
    character_set_name = character_set

    @property
    def thread_id(self) -> int:
        ...

    #Defined in C:

    def connect(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def ping(self) -> None:
        ...

    def change_use(self, user: str, password: str, database: str) -> None:
        ...

    def dump_debug_info(self) -> None:
        ...

    def escape_string(self, to_escape: str) -> str:
        ...

    def reconnect(self) -> None:
        ...

    def reset(self) -> None:
        ...

    @property
    def auto_reconnect(self) -> bool:
        ...

    @property
    def auto_commit(self) -> bool:
        ...

    @property
    def connection_id(self) -> int:
        ...

    @property
    def warnings(self) -> int:
        ...