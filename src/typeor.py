from typing import Generic, TypeVar  # Delete when PEP 695 is ready.

_T = TypeVar("_T")  # Delete when PEP 695 is ready.
_X = TypeVar("_X")  # Delete when PEP 695 is ready.


class OngoingTyping(Generic[_X]):

    def __init__(self, x: type[_X]) -> None:
        self.__x: type[_X] = x

    def join(self, t: type[_T]) -> "OngoingTyping[_X | _T]":
        return OngoingTyping(self.__x | t)   # type: ignore

    @property
    def end(self) -> type[_X]:
        return self.__x


def typed(x: type[_X]) -> OngoingTyping[_X]:
    return OngoingTyping(x)
