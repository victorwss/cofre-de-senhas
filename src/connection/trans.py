from typing import Any, Callable, Literal, override, ParamSpec, Self, Sequence
from typing import TypeVar  # Delete when PEP 695 is ready.
from abc import ABC, abstractmethod
from .conn import ColumnNames, Descriptor, RAW_DATA, SimpleConnection, TransactionNotActiveException
from types import TracebackType
from functools import wraps
from threadlocal import ThreadLocal

_T = TypeVar("_T")  # Delete when PEP 695 is ready.
_TRANS = TypeVar("_TRANS", bound = Callable[..., Any])  # Delete when PEP 695 is ready.
_P = ParamSpec("_P")
_R = TypeVar("_R")


class TransactedConnection(SimpleConnection):

    def __init__(self, activate: Callable[[], SimpleConnection], placeholder: str, database_type: str, database_name: str) -> None:
        self.__activate: Callable[[], SimpleConnection] = activate
        self.__conn: ThreadLocal[SimpleConnection | None] = ThreadLocal(None)
        self.__count: ThreadLocal[int] = ThreadLocal(0)
        self.__placeholder: str = placeholder
        self.__database_type: str = database_type
        self.__database_name: str = database_name

    @property
    def reenter_count(self) -> int:
        return self.__count.value

    @property
    def is_active(self) -> bool:
        return self.reenter_count > 0

    @property
    def __wrapped_or_none(self) -> SimpleConnection | None:
        return self.__conn.value

    @property
    def __wrapped(self) -> SimpleConnection:
        x: SimpleConnection | None = self.__wrapped_or_none
        if x is None:
            raise TransactionNotActiveException()
        return x

    def __enter__(self) -> Self:
        if self.__count.value == 0:
            self.__conn.value = self.__activate()
        self.__count.value += 1
        return self

    @override
    def close(self) -> None:
        if self.__count.value > 0:
            self.__count.value -= 1
            if self.__count.value == 0:
                self.__wrapped.close()
                self.__conn.value = None

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val : BaseException       | None,
            exc_tb  : TracebackType       | None
    ) -> Literal[False]:
        if self.__count.value == 1:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        self.close()
        return False

    #def transact[T: Callable[..., Any]](self, operation: T) -> T: # PEP 695
    def transact(self, operation: Callable[_P, _R]) -> Callable[_P, _R]:
        @wraps(operation)
        def transacted_operation(*args: _P.args, **kwargs: _P.kwargs) -> Any:
            with self as xxx:
                return operation(*args, **kwargs)
        return transacted_operation

    def force_close(self) -> None:
        self.__wrapped.close()

    @override
    def commit(self) -> None:
        self.__wrapped.commit()

    @override
    def rollback(self) -> None:
        self.__wrapped.rollback()

    @override
    def fetchone(self) -> tuple[Any, ...] | None:
        return self.__wrapped.fetchone()

    @override
    def fetchall(self) -> Sequence[tuple[Any, ...]]:
        return self.__wrapped.fetchall()

    @override
    def fetchmany(self, size: int = 0) -> Sequence[tuple[Any, ...]]:
        return self.__wrapped.fetchmany(size)

    @override
    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__wrapped.callproc(sql, parameters)
        return self

    @override
    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        self.__wrapped.execute(sql, parameters)
        return self

    @override
    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ()) -> Self:
        self.__wrapped.executemany(sql, parameters)
        return self

    @override
    def executescript(self, sql: str) -> Self:
        self.__wrapped.executescript(sql)
        return self

    @override
    def fetchone_dict(self) -> dict[str, Any] | None:
        return self.__wrapped.fetchone_dict()

    @override
    def fetchall_dict(self) -> list[dict[str, Any]]:
        return self.__wrapped.fetchall_dict()

    @override
    def fetchmany_dict(self, size: int = 0) -> list[dict[str, Any]]:
        return self.__wrapped.fetchmany_dict(size)

    @override
    #def fetchone_class[T](self, klass: type[T]) -> T | None: # PEP 695
    def fetchone_class(self, klass: type[_T]) -> _T | None:
        return self.__wrapped.fetchone_class(klass)

    @override
    #def fetchall_class[T](self, klass: type[T]) -> list[T]: # PEP 695
    def fetchall_class(self, klass: type[_T]) -> list[_T]:
        return self.__wrapped.fetchall_class(klass)

    @override
    #def fetchmany_class[T](self, klass: type[T], size: int = 0) -> list[T]: # PEP 695
    def fetchmany_class(self, klass: type[_T], size: int = 0) -> list[_T]:
        return self.__wrapped.fetchmany_class(klass, size)

    @override
    #def fetchone_class_lambda[T](self, ctor: Callable[[dict[str, RAW_DATA]], T]) -> T | None: # PEP 695
    def fetchone_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> _T | None:
        return self.__wrapped.fetchone_class_lambda(ctor)

    @override
    #def fetchall_class_lambda[T](self, ctor: Callable[[dict[str, RAW_DATA]], T]) -> list[T]: # PEP 695
    def fetchall_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T]) -> list[_T]:
        return self.__wrapped.fetchall_class_lambda(ctor)

    @override
    #def fetchmany_class_lambda[T](self, ctor: Callable[[dict[str, RAW_DATA]], T], size: int = 0) -> list[T]: # PEP 695
    def fetchmany_class_lambda(self, ctor: Callable[[dict[str, RAW_DATA]], _T], size: int = 0) -> list[_T]:
        return self.__wrapped.fetchmany_class_lambda(ctor, size)

    @property
    @override
    def rowcount(self) -> int:
        return self.__wrapped.rowcount

    @property
    @override
    def description(self) -> Descriptor:
        return self.__wrapped.description

    @property
    @override
    def column_names(self) -> ColumnNames:
        return self.__wrapped.column_names

    @property
    @override
    def lastrowid(self) -> int | None:
        return self.__wrapped.lastrowid

    @property
    @override
    def asserted_lastrowid(self) -> int:
        return self.__wrapped.asserted_lastrowid

    @property
    @override
    def raw_connection(self) -> object:
        return self.__wrapped.raw_connection

    @property
    @override
    def raw_cursor(self) -> object:
        return self.__wrapped.raw_cursor

    @property
    def wrapped(self) -> SimpleConnection:
        return self.__wrapped

    @property
    @override
    def placeholder(self) -> str:
        c: SimpleConnection | None = self.__wrapped_or_none
        if c is None: return self.__placeholder
        return c.placeholder

    @property
    @override
    def database_type(self) -> str:
        c: SimpleConnection | None = self.__wrapped_or_none
        if c is None: return self.__database_type
        return c.database_type

    @property
    @override
    def database_name(self) -> str:
        c: SimpleConnection | None = self.__wrapped_or_none
        if c is None: return self.__database_name
        return c.database_name


class ConnectionData(ABC):
    @abstractmethod
    def connect(self) -> TransactedConnection:
        pass