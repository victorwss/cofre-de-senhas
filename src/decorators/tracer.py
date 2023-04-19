from typing import Any, Callable, cast, TypeVar
from functools import wraps
from dataclasses import dataclass
from validator import dataclass_validate

__all__ = ["Call", "Logger"]

FuncT = TypeVar("FuncT", bound = Callable[..., Any])

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

    def trace(self, func: FuncT) -> FuncT:
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
        return cast(FuncT, wrapped)

    @staticmethod
    def for_print_fn(printer: Callable[[str], None] = print) -> "Logger":
        on_enter : Callable[[Call               ], None] = \
                lambda call     : printer(f"Calling {call.callee.__qualname__} - Args: {call.args} - Kwargs: {call.kwargs}.")
        on_return: Callable[[Call, Any          ], None] = \
                lambda call, ret: printer(f"Call on {call.callee.__qualname__} returned {ret}.")
        on_raise : Callable[[Call, BaseException], None] = \
                lambda call, exc: printer(f"Call on {call.callee.__qualname__} raised {exc}.")
        return Logger(on_enter, on_return, on_raise)