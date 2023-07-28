from typing import Any, cast
from flask import Flask, jsonify, request, session
from flask.wrappers import Response
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from cofre_de_senhas.httpwrap import *
from cofre_de_senhas.service import *
from cofre_de_senhas.service_impl import *
from validator import dataclass_validate
from dataclasses import dataclass
#from werkzeug.datastructures import MultiDict

PORTA: int = 5000
app: Flask = Flask(__name__)
app.secret_key = ""

SWAGGER_URL = "/docs"
API_URL = f"http://127.0.0.1:{PORTA}/spec"

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config = {
        "app_name": "Cofre de senhas"
    }
)

app.register_blueprint(swaggerui_blueprint)

class GerenciadorLoginImpl(GerenciadorLogin):

    def login(self, usuario: UsuarioComChave) -> None:
        session["chave"] = usuario.chave

    def logout(self) -> None:
        session.pop("chave", None)

    # Pode lançar UsuarioNaoLogadoException.
    @property
    def usuario_logado(self) -> ChaveUsuario:
        if app.secret_key == "": return ChaveUsuario(-1)
        if "chave" not in session: raise UsuarioNaoLogadoException()
        return cast(ChaveUsuario, session["chave"])

gl: GerenciadorLogin = GerenciadorLoginImpl()
su: ServicoUsuario = ServicoUsuarioImpl(gl)
sc: ServicoCategoria = ServicoCategoriaImpl(gl)
ss: ServicoSegredo = ServicoSegredoImpl(gl)

#### Usuários

@app.route("/login", methods = ["POST"])
@empty_json
def login() -> None:
    """Login
        ---
        post:
            tags: [""]
            body:
            responses:
                200:
                    content:
                        application/json:
                404:
                    uuuu
    """
    read_body(LoginComSenha)
    su.login(read_body(LoginComSenha))

@app.route("/logout", methods = ["POST"])
@empty_json
def logout() -> None:
    """Logout
        ---
        post:
            tags: [""]
            responses:
                200:
                    content:
                        application/json:
                404:
                    uuuu
    """
    bodyless()
    su.logout()

@app.route("/usuarios")
@jsoner
def listar_usuarios() -> ResultadoListaDeUsuarios:
    bodyless()
    return su.listar()

@app.route("/usuarios/<int:pk_usuario>")
@jsoner
def buscar_usuario_por_chave(pk_usuario: int) -> UsuarioComChave:
    bodyless()
    return su.buscar_por_chave(ChaveUsuario(pk_usuario))

@app.route("/usuarios/<nome>")
@jsoner
def buscar_usuario_por_login(nome: str) -> UsuarioComChave:
    bodyless()
    return su.buscar_por_login(LoginUsuario(nome))

@dataclass_validate
@dataclass(frozen = True)
class DadosNovoUsuario:
    senha: str
    nivel_acesso: str

@app.route("/usuarios/<nome>", methods = ["PUT"])
@jsoner
def criar_usuario(nome: str) -> UsuarioComChave:
    dados: DadosNovoUsuario = read_body(DadosNovoUsuario)
    try:
        p: NivelAcesso = NivelAcesso[dados.nivel_acesso]
    except:
        raise ConteudoIncompreensivelException()
    return su.criar(UsuarioNovo(nome, p, dados.senha))

@app.route("/trocar-senha", methods = ["POST"])
@empty_json
def trocar_senha() -> None:
    dados: TrocaSenha = read_body(TrocaSenha)
    return su.trocar_senha_por_chave(dados)

@dataclass_validate
@dataclass(frozen = True)
class DadosNovoNivel:
    nivel_acesso: str

@app.route("/usuarios/<nome>/alterar-nivel", methods = ["POST"])
@empty_json
def alterar_nivel(nome: str) -> None:
    dados: DadosNovoUsuario = read_body(DadosNovoUsuario)
    try:
        p: NivelAcesso = NivelAcesso[dados.nivel_acesso]
    except:
        raise ConteudoIncompreensivelException()
    su.alterar_nivel_por_login(UsuarioComNivel(nome, p))

@app.route("/usuarios/<nome>/resetar-senha", methods = ["POST"])
@jsoner
def resetar_senha(nome: str) -> SenhaAlterada:
    bodyless()
    return su.resetar_senha_por_login(ResetLoginUsuario(nome))

#### Categorias

@app.route("/categorias/<int:pk_categoria>")
@jsoner
def buscar_categoria_por_chave(pk_categoria: int) -> CategoriaComChave:
    bodyless()
    return sc.buscar_por_chave(ChaveCategoria(pk_categoria))

@app.route("/categorias/<nome>")
@jsoner
def buscar_categoria_por_nome(nome: str) -> CategoriaComChave:
    bodyless()
    return sc.buscar_por_nome(NomeCategoria(nome))

@app.route("/categorias/<nome>", methods = ["PUT"])
@jsoner
def criar_categoria(nome: str) -> CategoriaComChave:
    bodyless()
    return sc.criar(NomeCategoria(nome))

@app.route("/categorias/<nome>", methods = ["MOVE"])
@empty_json
def renomear_categoria(nome: str) -> None:
    bodyless()
    dest: str | None = request.headers.get("Destination")
    if dest is None: raise RequisicaoMalFormadaException()
    overwrite: str | None = request.headers.get("Overwrite")
    if overwrite not in [None, "F", "T"]: raise RequisicaoMalFormadaException()
    try:
        sc.renomear_por_nome(RenomeCategoria(nome, dest))
    except CategoriaJaExisteException as x:
        if overwrite == "F": raise PrecondicaoFalhouException()
        raise x

@app.route("/categorias")
@jsoner
def listar_categorias() -> ResultadoListaDeCategorias:
    bodyless()
    return sc.listar()

@app.route("/categorias/<nome>", methods = ["DELETE"])
@empty_json
def excluir_categoria(nome: str) -> None:
    bodyless()
    sc.excluir_por_nome(NomeCategoria(nome))

#### Segredos

@app.route("/segredos/", methods = ["PUT"])
@jsoner
def criar_segredo() -> SegredoComChave:
    dados: SegredoSemChave = read_body(SegredoSemChave)
    return ss.criar(dados)

@app.route("/segredos/<int:pk_segredo>", methods = ["PUT"])
@jsoner
def alterar_segredo(pk_segredo: int) -> SegredoComChave:
    dados: SegredoSemChave = read_body(SegredoSemChave)
    com_chave: SegredoComChave = dados.com_chave(ChaveSegredo(pk_segredo))
    ss.alterar_por_chave(com_chave)
    return com_chave

@app.route("/segredos/<int:pk_segredo>", methods = ["DELETE"])
@empty_json
def excluir_segredo(pk_segredo: int) -> None:
    bodyless()
    ss.excluir_por_chave(ChaveSegredo(pk_segredo))

@app.route("/segredos/<int:pk_segredo>")
@jsoner
def buscar_segredo_por_chave(pk_segredo: int) -> SegredoComChave:
    bodyless()
    return ss.buscar_por_chave(ChaveSegredo(pk_segredo))

@app.route("/segredos")
@jsoner
def listar_segredos() -> ResultadoPesquisaDeSegredos:
    bodyless()
    return ss.listar()

#### Swagger

@app.route("/spec")
def spec() -> Response:
    swag: dict[str, Any] = swagger(app)
    swag["info"]["version"] = "1.0"
    swag["info"]["title"] = "Cofre de senhas"
    print(swag)
    return jsonify(swag)

#### E aqui, a mágica acontece...

def servir() -> None:
    app.secret_key = ss.buscar_por_chave_sem_logar(ChaveSegredo(-1)).campos["Chave da sessão"]
    app.run(host = "0.0.0.0", port = PORTA, debug = True)