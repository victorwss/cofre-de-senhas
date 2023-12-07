from abc import ABC, abstractmethod
from dataclasses import dataclass
from flask import Flask, request, Response
from typing import Any, Callable, Generic, TypeVar
from inspect import signature, Signature
from validator import TypeValidationError, make_error
from werkzeug.datastructures.structures import MultiDict, ImmutableMultiDict
from werkzeug.datastructures.file_storage import FileStorage
from werkzeug.datastructures.headers import Headers
from sucesso import *
from httpwrap import *
from functools import wraps

_X = TypeVar("_X")

@dataclass(frozen = True)
class Converter(Generic[_X]):
    key: type[_X]
    func: Callable[[], _X]

def or_throw(data: _X | None) -> _X:
    if data is None:
        raise RequisicaoMalFormadaException()
    return data

def parse_int(data: str) -> int:
    try:
        return int(data)
    except:
        raise RequisicaoMalFormadaException()

def parse_float(data: str) -> float:
    try:
        return float(data)
    except:
        raise RequisicaoMalFormadaException()

@dataclass(frozen = True)
class WebParam(Generic[_X]):
    name: str
    converter: Converter[_X]

    @property
    def key(self) -> type[_X]:
        return self.converter.key

    def handle(self) -> _X:
        return self.converter.func()

def from_path(param_name: str) -> Callable[[], str]:
    def inner() -> str:
        return or_throw(or_throw(request.view_args).get(param_name))
    return inner

def from_query_string(param_name: str) -> Callable[[], str]:
    def inner() -> str:
        return or_throw(request.args.get(param_name))
    return inner

def from_query_string_multi(param_name: str) -> Callable[[], list[str]]:
    def inner() -> list[str]:
        return request.args.getlist(param_name)
    return inner

def from_file(param_name: str) -> Callable[[], FileStorage]:
    def inner() -> FileStorage:
        return or_throw(request.files.get(param_name))
    return inner

def from_file_multi(param_name: str) -> Callable[[], list[FileStorage]]:
    def inner() -> list[FileStorage]:
        return request.files.getlist(param_name)
    return inner

def from_header(param_name: str) -> Callable[[], str]:
    def inner() -> str:
        return or_throw(request.headers.get(param_name))
    return inner

def from_header_multi(param_name: str) -> Callable[[], list[str]]:
    def inner() -> list[str]:
        return request.headers.getlist(param_name)
    return inner

def from_form(param_name: str) -> Callable[[], str]:
    def inner() -> str:
        return or_throw(request.form.get(param_name))
    return inner

def from_form_multi(param_name: str) -> Callable[[], list[str]]:
    def inner() -> list[str]:
        return request.form.getlist(param_name)
    return inner

def from_cookie(param_name: str) -> Callable[[], str]:
    def inner() -> str:
        return or_throw(request.cookies.get(param_name))
    return inner

def from_cookie_multi(param_name: str) -> Callable[[], list[str]]:
    def inner() -> list[str]:
        return request.cookies.getlist(param_name)
    return inner

def from_body_bytes() -> Callable[[], bytes]:
    def inner() -> bytes:
        return request.get_data()
    return inner

def from_body() -> Callable[[], str]:
    def inner() -> str:
        return request.get_data(as_text = True)
    return inner

def from_body_json() -> Any:
    def inner() -> Any:
        return request.get_json()
    return inner

def from_body_typed(target: type[_X], *, json: bool = True, urlencoded: bool = True, multipart: bool = True) -> Converter[_X]:
    def inner() -> _X:
        return read_body(target, json = json, urlencoded = urlencoded, multipart = multipart)
    return Converter(target, inner)

def to_int(wrap: Callable[[], str]) -> Callable[[], int]:
    def inner() -> int:
        return parse_int(wrap())
    return inner

def to_ints(wrap: Callable[[], list[str]]) -> Callable[[], list[int]]:
    def inner() -> list[int]:
        return [parse_int(x) for x in wrap()]
    return inner

def to_float(wrap: Callable[[], str]) -> Callable[[], float]:
    def inner() -> float:
        return parse_float(wrap())
    return inner

def to_floats(wrap: Callable[[], list[str]]) -> Callable[[], list[float]]:
    def inner() -> list[float]:
        return [parse_float(x) for x in wrap()]
    return inner

_RS = Response | str
_T = TypeVar("_T", bound = Callable[..., _RS | tuple[_RS, int]])

@dataclass(frozen = True)
class WebMethod:
    http_method: str
    url_template: str
    params: list[WebParam[Any]]

    def handle(self) -> list[Any]:
        return [p.handle() for p in self.params]

class WebSuite:

    def __init__(self, app: Flask) -> None:
        self.__methods: list[WebMethod] = []
        self.__flask: Flask = app

    def __str__(self) -> str:
        r: str = ""
        for m in self.__methods:
            r += f"{m}"
        return r

    def flaskenify(self, wb: WebMethod) -> Callable[[_T], Callable[[], tuple[_RS, int]]]:
        def middle(what: _T) -> Callable[[], tuple[_RS, int]]:
            args_names: tuple[str, ...] = what.__code__.co_varnames[:what.__code__.co_argcount]

            s: Signature = signature(what)
            if len(s.parameters) != len(wb.params):
                raise TypeValidationError(target = self, errors = make_error("Function parameters and web parameters length mismatch."))

            response_template: str = "if (response.ok) { return response.body; } throw new Error();"
            template: str = "async function FUNC_NAME(PARAMS) { const url = URL; const options = { method: METHOD }; OPTIONS; const response = await fetch(url, options); RESPONSE }"

            @self.__flask.route(wb.url_template, methods = [wb.http_method])
            @wraps(what)
            def inner() -> tuple[_RS, int]:
                request.get_data() # Ensure caching
                params: list[Any] = wb.handle()
                f: _RS | tuple[_RS, int] = what(params)
                if isinstance(f, Response): return f, 200
                if isinstance(f, str): return f, 200
                return f

            return inner
        self.__methods.append(wb)
        return middle