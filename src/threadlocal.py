from typing import cast, Generic, TypeVar
from threading import local

_T = TypeVar("_T")

class ThreadLocal(Generic[_T]):

    def __init__(self, starting_value: _T) -> None:
        self.__empty: _T = starting_value
        self.__local: local = local()

    @property
    def value(self) -> _T:
        try:
            return cast(_T, self.__local.v)
        except AttributeError as x:
            return self.__empty

    @value.setter
    def value(self, new_value: _T | None) -> None:
        self.__local.v = new_value