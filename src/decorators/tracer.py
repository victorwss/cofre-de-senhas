from typing import Any, Callable, cast
from typing import TypeVar # Delete when PEP 695 is ready.
from functools import wraps
from dataclasses import dataclass
from validator import dataclass_validate

__all__ = ["Call", "Logger"]

_FuncT = TypeVar("_FuncT", bound = Callable[..., Any]) # Delete when PEP 695 is ready.


@dataclass_validate
@dataclass(frozen = True)
class Call:
    callee: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


@dataclass_validate
@dataclass(frozen = True)
class Logger:
    on_enter : Callable[[Call               ], None]
    on_return: Callable[[Call, Any          ], None]
    on_raise : Callable[[Call, BaseException], None]

    #def trace[F: Callable[..., Any]](self, func: _FuncT) -> _FuncT: # PEP 695
    def trace(self, func: _FuncT) -> _FuncT:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            call: Call = Call(func, args, kwargs)
            self.on_enter(call)
            try:
                r = func(*args, **kwargs)
                self.on_return(call, r)
                return r
            except BaseException as x:
                self.on_raise(call, x)
                raise x
        return cast(_FuncT, wrapped)

    @staticmethod
    def for_print_fn(printer: Callable[[str], None] = print) -> "Logger":
        def on_enter(call: Call) -> None:
            printer(f"Calling {call.callee.__qualname__} - Args: {call.args} - Kwargs: {call.kwargs}.")
        def on_return(call: Call, ret: Any) -> None:
            printer(f"Call on {call.callee.__qualname__} - returned {ret}.")
        def on_raise(call: Call, exc: BaseException) -> None:
            printer(f"Call on {call.callee.__qualname__} - raised {exc}.")
        return Logger(on_enter, on_return, on_raise)