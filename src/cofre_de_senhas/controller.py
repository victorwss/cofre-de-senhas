from typing import Any, Callable, cast, TypeVar
from flask import Flask, jsonify, request, session
from flask.wrappers import Response
from functools import wraps
from cofre_de_senhas.cofre_enum import *
from cofre_de_senhas.service import *
from cofre_de_senhas.service_impl import *
from dacite import from_dict
#from werkzeug.datastructures import MultiDict

app: Flask = Flask(__name__)
app.secret_key = ""

#_T = TypeVar("_T")
#def read_body(target: type[_T]) -> _T:
#    content_type: str = cast(str, request.headers.get("Content-Type"))
#    if (content_type == "application/json"):
#        json = request.json
#    else:
#        json = request.form
#    return from_dict(data_class = target, data = json)

class GerenciadorLoginImpl(GerenciadorLogin):

    def login(self, chave: UsuarioChave) -> None:
        session["chave"] = chave

    def logout(self) -> None:
        session.pop("chave", None)

    # Pode lançar UsuarioNaoLogadoException.
    @property
    def usuario_logado(self) -> UsuarioChave:
        if app.secret_key == "": return UsuarioChave(-1)
        if "chave" not in session: raise UsuarioNaoLogadoException()
        return cast(UsuarioChave, session["chave"])

gl: GerenciadorLogin = GerenciadorLoginImpl()
su: ServicoUsuario = ServicoUsuarioImpl(gl)
sc: ServicoCategoria = ServicoCategoriaImpl(gl)
ss: ServicoSegredo = ServicoSegredoImpl(gl)

_FuncE = TypeVar("_FuncE", bound = Callable[..., Response | tuple[Response, int]])
def handler(decorate: _FuncE) -> _FuncE:
    @wraps(decorate)
    def decorator(*args: Any, **kwargs: Any) -> Response | tuple[Response, int]:
        try:
            return decorate(*args, **kwargs)
        except BaseException as e:
            erro: Erro = Erro.criar(e)
            return jsonify(erro), erro.status
    return cast(_FuncE, decorator)

app.secret_key = ss.buscar_segredo_por_chave(SegredoChave(-1)).campos["Chave da sessão"]

@app.route("/login", methods = ["POST"])
@handler
def login() -> Response:
    raise Exception("TO DO")

@app.route("/categorias/<int:pk_categoria>")
@handler
def buscar_categoria(pk_categoria: int) -> Response:
    return jsonify(sc.listar_categorias())

@app.route("/categorias")
@handler
def listar_categorias() -> Response:
    return jsonify(sc.listar_categorias())

def servir() -> None:
    app.run(host = "0.0.0.0", port = 5000)