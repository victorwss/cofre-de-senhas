import dataclasses
from abc import ABC, abstractmethod
from typing import Generic, override, TypeVar


_SI = TypeVar("_SI", bound = int | str)
_X = TypeVar("_X")


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
        pass

    @property
    def empty(self) -> bool:
        return False


@dataclasses.dataclass
class _ErrorSetLeaf(ErrorSet):
    error: str

    @override
    def _list_all(self, fields: _FieldChain) -> list[str]:
        return [f"{fields}: {self.error}"]


@dataclasses.dataclass
class _ErrorSetDict(ErrorSet, Generic[_SI]):
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


def _flatten(data: list[list[_X]]) -> list[_X]:
    d: list[_X] = []
    for p in data:
        d += p
    return d


def _as_dict(what: list[_X]) -> dict[int, _X]:
    return {i: what[i] for i in range(0, len(what))}


def _thou_shalt_not_pass(pair: tuple[_X, ErrorSet]) -> bool:
    return not pair[1].empty


def _make_dict_errors(what: dict[_SI, ErrorSet]) -> ErrorSet:
    d2: dict[_SI, ErrorSet] = dict(filter(_thou_shalt_not_pass, what.items()))

    if len(d2) == 0:
        return no_error

    return _ErrorSetDict(d2)


def make_errors(what: list[ErrorSet] | dict[str, ErrorSet] | str | None = None) -> ErrorSet:

    if what is None:
        return no_error

    if isinstance(what, str):
        return _ErrorSetLeaf(what)

    if isinstance(what, dict):
        return _make_dict_errors(what)

    return _make_dict_errors(_as_dict(what))


no_error: ErrorSet = _ErrorSetEmpty()
bad_ellipsis: ErrorSet = make_errors("Unexpected ... here")