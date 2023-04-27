from typing import Any, Callable, cast, TypeVar
from flask import Flask, jsonify, request, session
from flask.wrappers import Response
from functools import wraps
from .cofre_enum import *
from .service import *
from .service_impl import *

class GerenciadorLoginImpl(GerenciadorLogin):

    def login(self, chave: UsuarioChave) -> None:
        session["chave"] = chave

    def logout(self) -> None:
        session.pop("chave", None)

    # Pode lançar UsuarioNaoLogadoException.
    @property
    def usuario_logado(self) -> UsuarioChave:
        if "chave" not in session: raise UsuarioNaoLogadoException
        return cast(UsuarioChave, session["chave"])

codigos: dict[type[BaseException], int] = {
    SenhaErradaException: 401,
    UsuarioNaoLogadoException: 401,
    UsuarioBanidoException: 403,
    PermissaoNegadaException: 403,
    UsuarioJaExisteException: 409,
    UsuarioNaoExisteException: 404,
    CategoriaJaExisteException: 409,
    CategoriaNaoExisteException: 404,
    SegredoNaoExisteException: 404
}

FuncE = TypeVar("FuncE", bound = Callable[..., Response | tuple[Response, int]])
def handler(decorate: FuncE) -> FuncE:
    @wraps(decorate)
    def decorator(*args: Any, **kwargs: Any) -> Response | tuple[Response, int]:
        try:
            return decorate(*args, **kwargs)
        except BaseException as e:
            codigo: int = codigos.get(e.__class__, 500)
            return jsonify(Erro(e.__str__(), e.__class__.__name__, codigo)), codigo
    return cast(FuncE, decorator)

app: Flask = Flask(__name__)
app.secret_key = "Senha super-secreta que ninguém pode saber qual é" # TO DO: Colocar isso dentro do próprio cofre de senhas.

gl: GerenciadorLogin = GerenciadorLoginImpl()
su: ServicoUsuario = ServicoUsuarioImpl(gl)
sc: ServicoCategoria = ServicoCategoriaImpl(gl)
ss: ServicoSegredo = ServicoSegredoImpl(gl)

@app.route("/categorias/<pk_categoria:int>")
@handler
def buscar_categoria(pk_categoria: int) -> Response:
    return jsonify(sc.listar_categorias())

@app.route("/categorias")
@handler
def listar_categorias() -> Response:
    return jsonify(sc.listar_categorias())

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)