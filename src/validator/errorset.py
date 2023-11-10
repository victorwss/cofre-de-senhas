import dataclasses
from abc import ABC, abstractmethod
from typing import override
from typing import Generic, TypeVar # Delete when PEP 695 is ready.


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

    def __as_list(self) -> list[str]:
        return self._list_all(_FieldChain([]))

    @override
    def __str__(self) -> str:
        return ",".join(self.__as_list())

    @abstractmethod
    def _list_all(self, fields: _FieldChain) -> list[str]:
        ...

    @property
    @abstractmethod
    def empty(self) -> bool:
        ...


class SignalingErrorSet(ErrorSet):

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
    #errors: dict[SI, ErrorSet]
    errors: dict[_SI, ErrorSet]

    @override
    def _list_all(self, fields: _FieldChain) -> list[str]:
        return _flatten([self.errors[k]._list_all(fields.append(k)) for k in self.errors])


@dataclasses.dataclass
class _ErrorSetEmpty(ErrorSet):
    pass

    @override
    def _list_all(self, fields: _FieldChain) -> list[str]:
        return []

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


#def _thou_shalt_not_pass[X](pair: tuple[X, ErrorSet]) -> bool: # PEP 695
def _thou_shalt_not_pass(pair: tuple[_X, ErrorSet]) -> bool:
    return not pair[1].empty


#def _make_dict_errors[SI: str | int](what: dict[SI, ErrorSet]) -> ErrorSet: # PEP 695
def _make_dict_errors(what: dict[_SI, ErrorSet]) -> ErrorSet:
    d2: dict[_SI, ErrorSet] = dict(filter(_thou_shalt_not_pass, what.items()))

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