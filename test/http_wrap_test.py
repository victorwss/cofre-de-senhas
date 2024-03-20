from threading import Thread
from flask import Flask
from werkzeug.serving import BaseWSGIServer, make_server
from httpwrap import empty_json, bodyless
from webrpc import from_body_typed, from_path_int, WebSuite
from dataclasses import dataclass
import requests


@dataclass(frozen = True)
class Foo:
    x: int


expected_out: str = "\n".join([
    'const RPC = (() => {',
    '    const __NO_RESPONSE   = 0, __JSON_RESPONSE = 1, __BLOB_RESPONSE = 2;',
    '    const __EMPTY_REQUEST = 0, __JSON_REQUEST  = 1, __PLAIN_REQUEST = 2;',
    '',
    '    async function __call(url, method, data, headers, has_response_body) {',
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
    '            throw new Error(`Ops, status was ${response.status}`);',
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
    '',
    '        teste_post: async function teste_post(bla) {',
    '            return await __call(`/teste/${int:bla}`, "POST", {type: __EMPTY_REQUEST}, {}, __JSON_RESPONSE);',
    '        },',
    '',
    '        teste_get: async function teste_get(bla) {',
    '            return await __call(`/teste/${int:bla}`, "GET", {type: __EMPTY_REQUEST}, {}, __JSON_RESPONSE);',
    '        },',
    '',
    '        teste_put: async function teste_put(bla) {',
    '            return await __call(`/teste/${int:bla}`, "PUT", {type: __EMPTY_REQUEST}, {}, __JSON_RESPONSE);',
    '        },',
    '',
    '        teste_borg: async function teste_borg(bla) {',
    '            return await __call(`/teste/${int:bla}`, "BORG", {type: __EMPTY_REQUEST}, {}, __JSON_RESPONSE);',
    '        },',
    '',
    '        teste_body: async function teste_body(body) {',
    '            return await __call(`/teste`, "POST", {type: __EMPTY_REQUEST}, {}, __JSON_RESPONSE);',
    '        },',
    '',
    '    };',
    '',
    '    return Object.freeze(_client);',
    '})();'
])


def test_post() -> None:
    app: Flask = Flask(__name__)
    ws: WebSuite = WebSuite(app, "/map")
    porta = 9999

    called = False

    @ws.route("POST", "/teste")
    @empty_json
    def teste() -> None:
        nonlocal called
        bodyless()
        called = True

    server: BaseWSGIServer = make_server("0.0.0.0", porta, app, True)
    app.app_context().push()

    def trabalho() -> None:
        server.serve_forever()

    t: Thread = Thread(target = trabalho)
    t.start()

    try:
        session: requests.Session = requests.Session()
        session.trust_env = False
        r: requests.Response = session.post(f"http://127.0.0.1:{porta}/teste", data = "")
        assert r.text.strip() == '{"conteudo":{},"status":200,"sucesso":true}'
        assert r.status_code == 200
        assert called

    finally:
        server.shutdown()
        t.join()


def test_post_param() -> None:
    app: Flask = Flask(__name__)
    ws: WebSuite = WebSuite(app, "/map")
    porta = 9999

    called = False

    @ws.route("POST", "/teste/<int:bla>", from_path_int("bla"))
    @empty_json
    def teste(bla: int) -> None:
        nonlocal called
        bodyless()
        assert bla == 42
        called = True

    server: BaseWSGIServer = make_server("0.0.0.0", porta, app, True)
    app.app_context().push()

    def trabalho() -> None:
        server.serve_forever()

    t: Thread = Thread(target = trabalho)
    t.start()

    try:
        session: requests.Session = requests.Session()
        session.trust_env = False
        r: requests.Response = session.post(f"http://127.0.0.1:{porta}/teste/42", data = "")
        assert r.text.strip() == '{"conteudo":{},"status":200,"sucesso":true}'
        assert r.status_code == 200
        assert called

    finally:
        server.shutdown()
        t.join()


def test_post_body() -> None:
    app: Flask = Flask(__name__)
    ws: WebSuite = WebSuite(app, "/map")
    porta = 9999

    called = False

    @ws.route("POST", "/teste", from_body_typed("bla", Foo))
    @empty_json
    def teste(body: Foo) -> None:
        nonlocal called
        assert body.x == 42
        called = True

    server: BaseWSGIServer = make_server("0.0.0.0", porta, app, True)
    app.app_context().push()

    def trabalho() -> None:
        server.serve_forever()

    t: Thread = Thread(target = trabalho)
    t.start()

    try:
        session: requests.Session = requests.Session()
        session.trust_env = False
        r: requests.Response = session.post(f"http://127.0.0.1:{porta}/teste", json = {"x": 42}, headers = {"Content-Type": "application/json"})
        assert r.text.strip() == '{"conteudo":{},"status":200,"sucesso":true}'
        assert r.status_code == 200
        assert called

    finally:
        server.shutdown()
        t.join()


def test_map() -> None:
    app: Flask = Flask(__name__)
    ws: WebSuite = WebSuite(app, "/map")
    porta = 9999

    @ws.route("POST", "/teste/<int:bla>", from_path_int("bla"))
    @empty_json
    def teste_post(bla: int) -> None:
        assert False

    @ws.route("GET", "/teste/<int:bla>", from_path_int("bla"))
    @empty_json
    def teste_get(bla: int) -> None:
        assert False

    @ws.route("PUT", "/teste/<int:bla>", from_path_int("bla"))
    @empty_json
    def teste_put(bla: int) -> None:
        assert False

    @ws.route("BORG", "/teste/<int:bla>", from_path_int("bla"))
    @empty_json
    def teste_borg(bla: int) -> None:
        assert False

    @ws.route("POST", "/teste", from_body_typed("body", Foo))
    @empty_json
    def teste_body(body: Foo) -> None:
        assert False

    server: BaseWSGIServer = make_server("0.0.0.0", porta, app, True)
    app.app_context().push()

    def trabalho() -> None:
        server.serve_forever()

    t: Thread = Thread(target = trabalho)
    t.start()

    try:
        session: requests.Session = requests.Session()
        session.trust_env = False
        r: requests.Response = session.get(f"http://127.0.0.1:{porta}/map")
        assert r.text == expected_out
        assert r.status_code == 200
        assert r.headers["Content-Type"] == "text/javascript"

    finally:
        server.shutdown()
        t.join()
