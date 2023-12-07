import dataclasses
from abc import ABC, abstractmethod
from typing import Any, override, TypeGuard
from typing import Generic, TypeVar # Delete when PEP 695 is ready.
from .typezoo import EllipsisType, TT2


_SI = TypeVar("_SI", bound = str | int) # Delete when PEP 695 is ready.
_X = TypeVar("_X") # Delete when PEP 695 is ready.


@dataclasses.dataclass
class _FieldChain:
    fields: list[str | int]

    @override
    def __str__(self) -> str:
        x: str = ""
        for k in self.fields:
            x += f"[{k}]"
        return x

    def append(self, other: str | int) -> "_FieldChain":
        return _FieldChain(self.fields + [other])


class ErrorSet(ABC):

    @property
    @abstractmethod
    def empty(self) -> bool:
        ...


class SignalingErrorSet(ErrorSet):

    def __as_list(self) -> list[str]:
        return self._list_all(_FieldChain([]))

    @override
    def __str__(self) -> str:
        return ",".join(self.__as_list())

    @abstractmethod
    def _list_all(self, fields: _FieldChain) -> list[str]:
        ...

    @property
    @override
    def empty(self) -> bool:
        return False


@dataclasses.dataclass
class _ErrorSetLeaf(SignalingErrorSet):
    error: str

    @override
    def _list_all(self, fields: _FieldChain) -> list[str]:
        return [f"{fields}: {self.error}"]


@dataclasses.dataclass
#class _ErrorSetDict[SI: str | int](SignalingErrorSet, Generic[SI]): # PEP 695
class _ErrorSetDict(SignalingErrorSet, Generic[_SI]):
    #errors: dict[SI, SignalingErrorSet]
    errors: dict[_SI, SignalingErrorSet]

    @override
    def _list_all(self, fields: _FieldChain) -> list[str]:
        return _flatten([self.errors[k]._list_all(fields.append(k)) for k in self.errors])


@dataclasses.dataclass
class _ErrorSetEmpty(ErrorSet):
    pass

    @override
    def __str__(self) -> str:
        return ""

    @property
    @override
    def empty(self) -> bool:
        return True


#def _flatten[X](data: list[list[X]]) -> list[X]: # PEP 695
def _flatten(data: list[list[_X]]) -> list[_X]:
    d: list[_X] = []
    for p in data:
        d += p
    return d


#def _as_dict[X](what: list[X]) -> dict[int, X]: # PEP 695
def _as_dict(what: list[_X]) -> dict[int, _X]:
    return {i: what[i] for i in range(0, len(what))}


#def _thou_shalt_not_pass[X](pair: tuple[X, ErrorSet]) -> TypeGuard[tuple[_X, SignalingErrorSet]]: # PEP 695
def _thou_shalt_not_pass(pair: tuple[_X, ErrorSet]) -> TypeGuard[tuple[_X, SignalingErrorSet]]:
    return not pair[1].empty


#def _make_dict_errors[SI: str | int](what: dict[SI, ErrorSet]) -> ErrorSet: # PEP 695
def _make_dict_errors(what: dict[_SI, ErrorSet]) -> ErrorSet:
    d2: dict[_SI, SignalingErrorSet] = dict(filter(_thou_shalt_not_pass, what.items()))

    if len(d2) == 0:
        return no_error

    return _ErrorSetDict(d2)


def make_error(what: str) -> SignalingErrorSet:
    return _ErrorSetLeaf(what)


def make_errors(what: list[ErrorSet] | dict[str, ErrorSet]) -> ErrorSet:
    if isinstance(what, dict):
        return _make_dict_errors(what)
    return _make_dict_errors(_as_dict(what))


no_error: ErrorSet = _ErrorSetEmpty()
bad_ellipsis: SignalingErrorSet = make_error("Unexpected ... here")

def to_error(what: SignalingErrorSet | TT2) -> ErrorSet:
    if what is EllipsisType:
        return bad_ellipsis
    if isinstance(what, SignalingErrorSet):
        return what
    return no_error


def split_errors(entering: list[SignalingErrorSet | TT2]) -> ErrorSet:
    return make_errors([to_error(t) for t in entering])


def split_valids(entering: list[SignalingErrorSet | TT2]) -> list[TT2]:
    return [t for t in entering if not isinstance(t, SignalingErrorSet) and not isinstance(t, EllipsisType)]