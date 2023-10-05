from typing import Any, Callable, cast
from threading import local

def _create_it() -> local:
    x: local = local()
    x.d = {}
    return x

class Single:

    __field: local = _create_it()
    __main: dict[str, Callable[[], Any]] = {}

    def __init__(self) -> None:
        raise Exception()

    @staticmethod
    def __maked() -> dict[str, Any]:
        try:
            Single.__field.d
        except AttributeError:
            Single.__field.d = {}
        return cast(dict[str, Any], Single.__field.d)

    @staticmethod
    def register(what: str, factory: Callable[[], Any]) -> None:
        Single.__main[what] = factory

    @staticmethod
    def instance(what: str) -> Any:
        if what in Single.__maked(): return Single.__maked()[what]
        if what not in Single.__main: raise Exception(f"Not registered {what}")

        x: Any = Single.__main[what]()
        Single.__maked()[what] = x
        return x