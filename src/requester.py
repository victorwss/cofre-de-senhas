import requests
from validator import dataclass_validate
from dataclasses import asdict, dataclass
from requests.models import Response
from typing import Any, Callable, TypeVar, TYPE_CHECKING
from sucesso import Status


if TYPE_CHECKING:
    from _typeshed import DataclassInstance
    _D = TypeVar("_D", bound = DataclassInstance)
else:
    _D = TypeVar("_D")

_T = TypeVar("_T")  # Delete when PEP 695 is ready.
_X = TypeVar("_X")  # Delete when PEP 695 is ready.


class UnknownRemoteError(Exception):
    def __init__(self, data: Any):
        super(UnknownRemoteError, self).__init__(data)


@dataclass_validate
@dataclass(frozen = True)
class ErrorData:
    internal: bool
    error_type: str
    error_message: str

    def __eval(self, evaller: Callable[[str, str], Any]) -> Any:
        try:
            return evaller(self.error_type, self.error_message)
        except BaseException:
            raise UnknownRemoteError(f"[{self.error_type}] {self.error_message}")

    # def __raise_it[X](self, j: Any, x: type[X]) -> X:  # PEP 695
    def raise_it(self, x: type[_X], evaller: Callable[[str, str], Any]) -> _X:
        if self.internal:
            raise UnknownRemoteError(f"[{self.error_type}] {self.error_message}")
        z: Any = self.__eval(evaller)
        if isinstance(z, x):
            return z
        if isinstance(z, Status) and isinstance(z, BaseException):
            raise z
        raise UnknownRemoteError(f"[{self.error_type}] {self.error_message}")


def _islist(e: Any) -> bool:
    return isinstance(e, set) or isinstance(e, frozenset) or isinstance(e, tuple)


def _is_inside(x: Any, recurse_guard: list[Any]) -> bool:
    for k in recurse_guard:
        if x is k:
            return True
    return False


def _dictfix_in(x: dict[Any, Any], recurse_guard: list[Any]) -> dict[Any, Any]:
    if _is_inside(x, recurse_guard):
        return x
    for i in list(x.keys()):
        e: Any = x[i]
        if _islist(e):
            x[i] = list(e)
        elif isinstance(e, dict):
            recurse_guard.append(x)
            x[i] = _dictfix_in(e, recurse_guard)
            recurse_guard.pop()
    return x


def _dictfix(x: dict[Any, Any]) -> dict[Any, Any]:
    return _dictfix_in(x, [])


# @dataclass_validate
@dataclass(frozen = True)
class RequesterStrategy:
    success: Callable[[Any], bool]
    error_maker: Callable[[Any], ErrorData]
    none_replacer: type[Any]
    result_maker: Callable[[Any, type[_T]], _T]
    evaller: Callable[[str, str], Any]


class Requester:

    def __init__(self, url: str, strategy: RequesterStrategy) -> None:
        self.__strategy: RequesterStrategy = strategy
        self.__base_url: str = url
        self.__session: requests.Session = requests.Session()
        self.__cookies: dict[str, str] = {}
        self.__session.trust_env = False

    # def get[T, X](self, path: str, t: type[T], x: type[X]) -> T | X: # PEP 695
    def get(self, path: str, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.get(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def post[T, X](self, path: str, data: _D, t: type[T], x: type[X]) -> T | X: # PEP 695
    def post(self, path: str, data: _D, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.post(self.__base_url + path, json = _dictfix(asdict(data)), cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def put[T, X](self, path: str, data: _D, t: type[T], x: type[X]) -> T | X: # PEP 695
    def put(self, path: str, data: _D, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.put(self.__base_url + path, json = _dictfix(asdict(data)), cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def delete[T, X](self, path: str, t: type[T], x: type[X]) -> T | X: # PEP 695
    def delete(self, path: str, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.delete(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def move[T, X](self, path: str, to: str, overwrite: bool, t: type[T], x: type[X]) -> T | X: # PEP 695
    def move(self, path: str, to: str, overwrite: bool, t: type[_T], x: type[_X]) -> _T | _X:
        h: dict[str, str] = {
            "Destination": to,
            "Overwrite": "T" if overwrite else "F"
        }
        r: Response = self.__session.request("MOVE", self.__base_url + path, cookies = self.__cookies, headers = h)
        return self.__unwrap(r, t, x)

    def __json_validate(self, j: Any, rt: str) -> ErrorData | None:
        if self.__strategy.success(j):
            return None
        try:
            return self.__strategy.error_maker(j)  # from_dict(data_class = _ErroRemoto, data = j, config = Config(cast = [Enum, IntEnum]))
        except BaseException:
            raise UnknownRemoteError(rt)

    def __json_it(self, r: Response) -> Any:
        try:
            return r.json()
        except BaseException:
            raise UnknownRemoteError(r.text)

    # def __unwrap[T, X](self, r: Response, t: type[T] | None, x: type[X]]) -> T | X: # PEP 695
    def __unwrap(self, r: Response, t: type[_T], x: type[_X]) -> _T | _X:
        self.__cookies = dict(r.cookies)
        j: Any = self.__json_it(r)
        erro: ErrorData | None = self.__json_validate(j, r.text)
        if erro is not None:
            return erro.raise_it(x, self.__strategy.evaller)
        if t is type(None):
            self.__strategy.result_maker(j, self.__strategy.none_replacer)
            return None  # type: ignore
        return self.__strategy.result_maker(j, t)
