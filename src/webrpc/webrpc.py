from dataclasses import dataclass
from flask import Flask, make_response, request
from typing import Any, Callable, Generic, ParamSpec, TypeVar
from inspect import signature, Signature, Parameter
from werkzeug.datastructures.file_storage import FileStorage
from werkzeug import Response
from sucesso import RequisicaoMalFormadaException
from httpwrap import handler, read_body
from functools import wraps
from types import MappingProxyType
import sys
import traceback


_P = ParamSpec("_P")
_X = TypeVar("_X")
_C = Callable[_P, tuple[Response, int]]
_D = Callable[[], tuple[Response, int]]


def or_default(default: str | None, data: str | None) -> str:
    if data is None:
        return or_throw(default)
    return data


def or_throw(data: _X | None) -> _X:
    if data is None:
        raise RequisicaoMalFormadaException()
    return data


def parse_int(data: str) -> int:
    try:
        return int(data)
    except BaseException:
        raise RequisicaoMalFormadaException()


def parse_float(data: str) -> float:
    try:
        return float(data)
    except BaseException:
        raise RequisicaoMalFormadaException()


def identity(data: str) -> str:
    return data


@dataclass(frozen = True)
class WebParam(Generic[_X]):
    name: str
    key: type[_X]
    func: Callable[[], _X]
    js_snippet: str
    on_path_to_flask: bool
    full_body: bool
    body_type: str

    def handle(self) -> _X:
        return self.func()


def from_path(param_name: str) -> WebParam[str]:
    def inner() -> str:
        return or_throw(or_throw(request.view_args).get(param_name))
    return WebParam(param_name, str, inner, "", True, False, "")


def from_path_int(param_name: str) -> WebParam[int]:
    def inner() -> int:
        return parse_int(or_throw(or_throw(request.view_args).get(param_name)))
    return WebParam(param_name, int, inner, "", True, False, "")


def from_path_float(param_name: str) -> WebParam[float]:
    def inner() -> float:
        return parse_float(or_throw(or_throw(request.view_args).get(param_name)))
    return WebParam(param_name, float, inner, "", True, False, "")


def from_query_string(param_name: str, default: str | None = None) -> WebParam[str]:
    def inner() -> str:
        return or_throw(or_default(default, request.args.get(param_name)))
    js: str = f'__qs.push(["${param_name}", [${param_name}]]);'
    return WebParam(param_name, str, inner, js, False, False, "")


def from_query_string_multi(param_name: str) -> WebParam[list[str]]:
    def inner() -> list[str]:
        return request.args.getlist(param_name)
    js: str = f'__qs.push(["${param_name}", ${param_name}]);'
    return WebParam(param_name, list[str], inner, js, False, False, "")


def from_file(param_name: str) -> WebParam[FileStorage]:
    def inner() -> FileStorage:
        return or_throw(request.files.get(param_name))
    return WebParam(param_name, FileStorage, inner, "", False, False, "multipart")


def from_file_multi(param_name: str) -> WebParam[list[FileStorage]]:
    def inner() -> list[FileStorage]:
        return request.files.getlist(param_name)
    return WebParam(param_name, list[FileStorage], inner, "", False, False, "multipart")


def from_header(param_name: str, default: str | None = None) -> WebParam[str]:
    def inner() -> str:
        return or_throw(or_default(default, request.headers.get(param_name)))
    js: str = f'__hs.push(["${param_name}", [${param_name}]]);'
    return WebParam(param_name, str, inner, js, False, False, "")


def from_header_multi(param_name: str) -> WebParam[list[str]]:
    def inner() -> list[str]:
        return request.headers.getlist(param_name)
    js: str = f'__hs.push(["${param_name}", ${param_name}]);'
    return WebParam(param_name, list[str], inner, js, False, False, "")


def from_form(param_name: str, default: str | None = None) -> WebParam[str]:
    def inner() -> str:
        return or_throw(or_default(default, request.form.get(param_name)))
    js: str = f'__body.body.push(["${param_name}", [${param_name}]]);'
    return WebParam(param_name, str, inner, js, False, False, "multipart")


def from_form_multi(param_name: str) -> WebParam[list[str]]:
    def inner() -> list[str]:
        return request.form.getlist(param_name)
    js: str = f'__body.body.push(["${param_name}", ${param_name}]);'
    return WebParam(param_name, list[str], inner, js, False, False, "multipart")


def from_cookie(param_name: str, default: str | None = None) -> WebParam[str]:
    def inner() -> str:
        return or_throw(or_default(default, request.cookies.get(param_name)))
    return WebParam(param_name, str, inner, "", False, False, "")


def from_cookie_multi(param_name: str) -> WebParam[list[str]]:
    def inner() -> list[str]:
        return request.cookies.getlist(param_name)
    return WebParam(param_name, list[str], inner, "", False, False, "")


def from_body_bytes(param_name: str) -> WebParam[bytes]:
    def inner() -> bytes:
        return request.get_data()
    js: str = f'__body.body = {param_name};'
    return WebParam(param_name, bytes, inner, js, False, True, "")


def from_body(param_name: str) -> WebParam[str]:
    def inner() -> str:
        return request.get_data(as_text = True)
    js: str = f'__body.body = {param_name};'
    return WebParam(param_name, str, inner, js, False, True, "")


def from_body_typed(param_name: str, target: type[_X], *, json: bool = True, urlencoded: bool = True, multipart: bool = True) -> WebParam[_X]:
    def inner() -> _X:
        return read_body(target, json = json, urlencoded = urlencoded, multipart = multipart)
    js: str = f'__body.body = {param_name};'
    return WebParam(param_name, target, inner, js, False, True, "json")


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


@dataclass(frozen = True)
class WebMethod:
    http_method: str
    url_template: str
    params: list[WebParam[Any]]

    def handle(self) -> list[Any]:
        return [p.handle() for p in self.params]


_first_skeleton: str = "\n".join([
    'const RPC = (() => {',
    '    const __NO_RESPONSE   = 0, __JSON_RESPONSE = 1, __BLOB_RESPONSE = 2;',
    '    const __EMPTY_REQUEST = 0, __JSON_REQUEST  = 1, __PLAIN_REQUEST = 2;',
    '',
    '    async function __call(url, method, data, queryString, headers, has_response_body) {',
    '        if (!("Content-Type" in headers)) {',
    '            headers["Content-Type"] = "application/json";',
    '        }',
    '',
    '        let options = {',
    '            method: method,',
    '            mode: "cors",',
    '            cache: "no-cache",',
    '            credentials: "same-origin",',
    '            headers,',
    '            redirect: "follow",',
    '            referrerPolicy: "no-referrer"',
    '        };',
    '',
    '        if (data.type === __EMPTY_REQUEST) {',
    '            // Do nothing.',
    '        } else if (data.type === __JSON_REQUEST) {',
    '            options["body"] = JSON.stringify(data.body);',
    '        } else if (data.type === __PLAIN_REQUEST) {',
    '            options["body"] = `${data.body}`;',
    '        } else {',
    '            throw new Error("Ops");',
    '        }',
    '',
    '        const response = await fetch(url, options);',
    '        if (!response.ok) {',
    '            throw new Error(`Ops, status was ${response.status}.`);',
    '        }',
    '',
    '        switch (has_response_body) {',
    '            case __NO_RESPONSE  : return;',
    '            case __JSON_RESPONSE: return response.json();',
    '            case __BLOB_RESPONSE: return response.blob();',
    '            default: throw new Error("Ops");',
    '        }',
    '    }',
    '',
    '    const _client = {',
    ''
])

_func_skeleton: str = "\n".join([
    '',
    '        =FUNC_NAME=: async function =FUNC_NAME=(=PARAMS=) {',
    '            const __qs = {};',
    '            const __hs = {};',
    '            const __body = =BODY=;=INJECT_JS=',
    '            return await __call(`=URL=`, "=METHOD=", __body, __qs, __hs, =HRB=);',
    '        },',
    '',
])


_last_skeleton: str = "\n".join([
    '',
    '    };',
    '',
    '    return Object.freeze(_client);',
    '})();'
])


def _fix_up_url(url: str) -> str:
    iters: int = 0
    while iters < 1000:
        p1: int = url.find("<")
        if p1 < 0:
            return url
        p2: int = url.find(">")
        if p2 < 0:
            raise ValueError(f"Malformed URL {url}")
        part: str = url[p1 + 1 : p2]
        colon: int = part.find(":")
        url = url[:p1] + "${" + url[p1 + colon + 2 : p2] + "}" + url[p2 + 1:]
        iters += 1
    raise ValueError("Too many iterations")


def _make_js_stub(
        func_name: str,
        param_names: MappingProxyType[str, Parameter],
        param_specs: list[WebParam[Any]],
        url: str,
        method: str
) -> str:

    has_request_body: bool = False
    has_response_body: bool = True

    full_body: WebParam[Any] | None = None
    for p in param_specs:
        if p.full_body:
            if full_body is None:
                full_body = p
            else:
                raise TypeError("Two or more full-body parameters")

    body_type: str = ""
    for p in param_specs:
        if p.body_type != "":
            if body_type == "":
                body_type = p.body_type
            elif body_type != p.body_type:
                raise TypeError("Two or more different body types")

    body_js: str = "{type: __EMPTY_REQUEST}"
    if body_type == "json":
        body_js = "{type: __JSON_REQUEST, body: []}"
    if body_type == "multipart":
        body_js = "{type: __PLAIN_REQUEST, body: []}"

    js: str = ""
    for p in param_specs:
        if p.js_snippet != "":
            js += "\n            " + p.js_snippet

    return _func_skeleton \
        .replace("=FUNC_NAME=", func_name) \
        .replace("=PARAMS=", ", ".join(param_names)) \
        .replace("=URL=", _fix_up_url(url)) \
        .replace("=METHOD=", method) \
        .replace("=BODY=", body_js) \
        .replace("=INJECT_JS=", js) \
        .replace("=HRB=", "__JSON_RESPONSE" if has_response_body else "__NO_RESPONSE")


class WebSuite:

    def __init__(self, app: Flask, map_url: str) -> None:
        self.__methods: list[WebMethod] = []
        self.__flask: Flask = app
        self.__js_stubs: list[str] = [_first_skeleton]

        @app.route(map_url)
        def map() -> Response:
            r: Response = make_response(self.js_stubs)
            r.headers["Content-Type"] = "text/javascript"
            return r

    @property
    def js_stubs(self) -> str:
        return "".join(self.__js_stubs) + _last_skeleton

    def hidden_route(self, method: str, url_template: str, *params: WebParam[Any]) -> Callable[[_C[Any]], _D]:
        return self.flaskenify(WebMethod(method, url_template, [*params]), True)

    def route(self, method: str, url_template: str, *params: WebParam[Any]) -> Callable[[_C[Any]], _D]:
        return self.flaskenify(WebMethod(method, url_template, [*params]), False)

    def flaskenify(self, wm: WebMethod, hidden: bool) -> Callable[[_C[Any]], _D]:
        def middle(what: _C[Any]) -> _D:
            s: Signature = signature(what)
            if len(s.parameters) != len(wm.params):
                raise Exception(f"Function parameters and web parameters length mismatch ({s.parameters}) - ({wm.params}).")

            if not hidden:
                js_stub: str = _make_js_stub(what.__name__, s.parameters, wm.params, wm.url_template, wm.http_method)
                self.__js_stubs.append(js_stub)

            @handler
            @wraps(what)
            def inner() -> tuple[Response, int]:
                request.get_data()  # Ensure caching
                try:
                    params: list[Any] = wm.handle()
                    return what(*params)
                except BaseException as x:
                    traceback.print_exc(file = sys.stdout)
                    raise x

            t: str = "\n".join([
                f"@app.route('{wm.url_template}', methods = ['{wm.http_method}'])",
                f"def {what.__name__}({', '.join([p.name for p in wm.params if p.on_path_to_flask])}):",
                "\n    return inner()",
            ])
            app: Flask = self.__flask
            exec(t, {"inner": inner, "app": app})
            return inner

        self.__methods.append(wm)
        return middle
