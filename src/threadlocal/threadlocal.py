from typing import cast
from typing import Generic, TypeVar  # Delete when PEP 695 is ready.
from threading import local


_T = TypeVar("_T")  # Delete when PEP 695 is ready.


# class ThreadLocal[T]: # PEP 695
class ThreadLocal(Generic[_T]):

    # def __init__(self, starting_value: T) -> None: # PEP 695
    def __init__(self, starting_value: _T) -> None:
        self.__empty: _T = starting_value
        self.__local: local = local()

    @property
    # def value(self) -> T: # PEP 695
    def value(self) -> _T:
        try:
            return cast(_T, self.__local.v)
        except AttributeError:
            return self.__empty

    @value.setter
    # def value(self, new_value: T | None) -> None: # PEP 695
    def value(self, new_value: _T | None) -> None:
        self.__local.v = new_value
