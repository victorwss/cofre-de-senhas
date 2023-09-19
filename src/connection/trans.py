from typing import Any, Callable, cast, Literal, Self, Sequence, TypeVar
from .conn import ColumnNames, Descriptor, RAW_DATA, SimpleConnection, TransactionNotActiveException
from types import TracebackType
from functools import wraps
import threading

_T = TypeVar("_T")
_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])

class TransactedConnection(SimpleConnection):

    def __init__(self, activate: Callable[[], SimpleConnection]) -> None:
        self.__activate: Callable[[], SimpleConnection] = activate
        self.__local: threading.local = threading.local()
        self.__count: int = 0

    def __enter__(self) -> Self:
        if self.__count == 0:
            self.__local.con = self.__activate()
        self.__count += 1
        return self

    def close(self) -> None:
        self.__count -= 1
        if self.__count == 0:
            self.__wrapped.close()
            del self.__local.con

    def __exit__( \
            self, \
            exc_type: type[BaseException] | None, \
            exc_val : BaseException       | None, \
            exc_tb  : TracebackType       | None  \
    ) -> Literal[False]:
        self.close()
        return False

    @property
    def reenter_count(self) -> int:
        return self.__count

    @property
    def is_active(self) -> bool:
        return self.__count > 0

    def transact(self, operation: _TRANS) -> _TRANS:
        @wraps(operation)
        def transacted_operation(*args: Any, **kwargs: Any) -> Any:
            with self as xxx:
                ok: bool = True
                try:
                    return operation(*args, **kwargs)
                except BaseException as x:
                    ok = False
                    raise x
                finally:
                    if ok:
                        self.commit()
                    else:
                        self.rollback()
        return cast(_TRANS, transacted_operation)

    @property
    def __wrapped(self) -> SimpleConnection:
        try:
            return cast(SimpleConnection, self.__local.con)
        except AttributeError as x:
            raise TransactionNotActiveException()

    def force_close(self) -> None:
        self.__wrapped.close()

    def commit(self) -> None:
        self.__wrapped.commit()

    def rollback(self) -> None:
        self.__wrapped.rollback()

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.__wrapped.fetchone()

    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        return self.__wrapped.fetchall()

    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        return self.__wrapped.fetchmany(size)

    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__wrapped.callproc(sql, parameters)
        return self

    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__wrapped.execute(sql, parameters)
        return self

    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ()) -> Self:
        self.__wrapped.executemany(sql, parameters)
        return self

    def executescript(self, sql: str) -> Self:
        self.__wrapped.executescript(sql)
        return self

    def fetchone_dict(self) -> dict[str, Any] | None:
        return self.__wrapped.fetchone_dict()

    def fetchall_dict(self) -> list[dict[str, Any]]:
        return self.__wrapped.fetchall_dict()

    def fetchmany_dict(self, size: int = 0) -> list[dict[str, Any]]:
        return self.__wrapped.fetchmany_dict(size)

    def fetchone_class(self, klass: type[_T]) -> _T | None:
        return self.__wrapped.fetchone_class(klass)

    def fetchall_class(self, klass: type[_T]) -> list[_T]:
        return self.__wrapped.fetchall_class(klass)

    def fetchmany_class(self, klass: type[_T], size: int = 0) -> list[_T]:
        return self.__wrapped.fetchmany_class(klass, size)

    def fetchone_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> _T | None:
        return self.__wrapped.fetchone_class_lambda(ctor)

    def fetchall_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> list[_T]:
        return self.__wrapped.fetchall_class_lambda(ctor)

    def fetchmany_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T], size: int = 0) -> list[_T]:
        return self.__wrapped.fetchmany_class_lambda(ctor, size)

    @property
    def arraysize(self) -> int:
        return self.__wrapped.arraysize

    @arraysize.setter
    def arraysize(self, size: int) -> None:
        self.__wrapped.arraysize = size

    @property
    def rowcount(self) -> int:
        return self.__wrapped.rowcount

    @property
    def description(self) -> Descriptor:
        return self.__wrapped.description

    @property
    def column_names(self) -> ColumnNames:
        return self.__wrapped.column_names

    @property
    def lastrowid(self) -> int | None:
        return self.__wrapped.lastrowid

    @property
    def asserted_lastrowid(self) -> int:
        return self.__wrapped.asserted_lastrowid

    @property
    def raw_connection(self) -> object:
        return self.__wrapped.raw_connection

    @property
    def raw_cursor(self) -> object:
        return self.__wrapped.raw_cursor