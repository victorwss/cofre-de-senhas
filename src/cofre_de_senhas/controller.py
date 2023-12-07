from typing import Any, cast, override
from flask import Flask, jsonify, redirect, request, session, url_for
from werkzeug import Response
from httpwrap import *
from webrpc import *
from .service import *
from .service_impl import Servicos
from validator import dataclass_validate
from dataclasses import dataclass
#from werkzeug.datastructures import MultiDict
from .bd.bd_dao_impl import CofreDeSenhasDAOImpl
from .categoria.categoria_dao_impl import CategoriaDAOImpl
from .usuario.usuario_dao_impl import UsuarioDAOImpl
from .segredo.segredo_dao_impl import SegredoDAOImpl
from connection.trans import TransactedConnection
from .conn_factory import connect

class GerenciadorLoginImpl(GerenciadorLogin):

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        session["chave"] = usuario.chave

    @override
    def logout(self) -> None:
        session.pop("chave", None)

    # Pode lançar UsuarioNaoLogadoException.
    @property
    @override
    def usuario_logado(self) -> ChaveUsuario:
        #if app.secret_key == "": return ChaveUsuario(-1)
        if "chave" not in session: raise UsuarioNaoLogadoException()
        return cast(ChaveUsuario, session["chave"])

@dataclass
class Foo:
    ba: int

def servir() -> None:
    PORTA: int = 5000
    app: Flask = Flask(__name__)
    app.secret_key = ""
    ws: WebSuite = WebSuite(app)

    gl: GerenciadorLogin = GerenciadorLoginImpl()
    cofre: TransactedConnection = connect()

    CategoriaDAOImpl(cofre)
    CofreDeSenhasDAOImpl(cofre)
    SegredoDAOImpl(cofre)
    UsuarioDAOImpl(cofre)
    sx: Servicos = Servicos(gl, cofre)

    app.secret_key = sx.segredo.buscar_por_chave_sem_logar(ChaveSegredo(-1)).campos["Chave da sessão"]

    #### Usuários

    @ws.flaskenify(WebMethod("POST", "/test", []))
    @jsoner
    def foobar() -> Foo:
        return Foo(123)

    @ws.flaskenify(WebMethod("POST", "/login", [WebParam("body", from_body_typed(LoginComSenha))]))
    @empty_json
    def login(body: LoginComSenha) -> None:
        sx.usuario.login(body)

    @app.route("/logout", methods = ["POST"])
    @empty_json
    def logout() -> None:
        bodyless()
        sx.usuario.logout()

    @app.route("/usuarios")
    @jsoner
    def listar_usuarios() -> ResultadoListaDeUsuarios:
        bodyless()
        return sx.usuario.listar()

    @app.route("/usuarios/<int:pk_usuario>")
    @jsoner
    def buscar_usuario_por_chave(pk_usuario: int) -> UsuarioComChave:
        bodyless()
        return sx.usuario.buscar_por_chave(ChaveUsuario(pk_usuario))

    @app.route("/usuarios/<nome>")
    @jsoner
    def buscar_usuario_por_login(nome: str) -> UsuarioComChave:
        bodyless()
        return sx.usuario.buscar_por_login(LoginUsuario(nome))

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
        return sx.usuario.criar(UsuarioNovo(nome, p, dados.senha))

    @app.route("/trocar-senha", methods = ["POST"])
    @empty_json
    def trocar_senha() -> None:
        dados: TrocaSenha = read_body(TrocaSenha)
        return sx.usuario.trocar_senha_por_chave(dados)

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
        sx.usuario.alterar_nivel_por_login(UsuarioComNivel(nome, p))

    @app.route("/usuarios/<nome>/resetar-senha", methods = ["POST"])
    @jsoner
    def resetar_senha(nome: str) -> SenhaAlterada:
        bodyless()
        return sx.usuario.resetar_senha_por_login(ResetLoginUsuario(nome))

    #### Categorias

    @app.route("/categorias/<int:pk_categoria>")
    @jsoner
    def buscar_categoria_por_chave(pk_categoria: int) -> CategoriaComChave:
        bodyless()
        return sx.categoria.buscar_por_chave(ChaveCategoria(pk_categoria))

    @app.route("/categorias/<nome>")
    @jsoner
    def buscar_categoria_por_nome(nome: str) -> CategoriaComChave:
        bodyless()
        return sx.categoria.buscar_por_nome(NomeCategoria(nome))

    @app.route("/categorias/<nome>", methods = ["PUT"])
    @jsoner
    def criar_categoria(nome: str) -> CategoriaComChave:
        bodyless()
        return sx.categoria.criar(NomeCategoria(nome))

    @app.route("/categorias/<nome>", methods = ["MOVE"])
    @empty_json
    def renomear_categoria(nome: str) -> None:
        bodyless()
        dest, overwrite = move()
        try:
            sx.categoria.renomear_por_nome(RenomeCategoria(nome, dest))
        except CategoriaJaExisteException as x:
            if not overwrite: raise PrecondicaoFalhouException()
            raise x

    @app.route("/categorias")
    @jsoner
    def listar_categorias() -> ResultadoListaDeCategorias:
        bodyless()
        return sx.categoria.listar()

    @app.route("/categorias/<nome>", methods = ["DELETE"])
    @empty_json
    def excluir_categoria(nome: str) -> None:
        bodyless()
        sx.categoria.excluir_por_nome(NomeCategoria(nome))

    #### Segredos

    @app.route("/segredos", methods = ["PUT"])
    @jsoner
    def criar_segredo() -> SegredoComChave:
        dados: SegredoSemChave = read_body(SegredoSemChave)
        return sx.segredo.criar(dados)

    @app.route("/segredos/<int:pk_segredo>", methods = ["PUT"])
    @jsoner
    def alterar_segredo(pk_segredo: int) -> SegredoComChave:
        dados: SegredoSemChave = read_body(SegredoSemChave)
        com_chave: SegredoComChave = dados.com_chave(ChaveSegredo(pk_segredo))
        sx.segredo.alterar_por_chave(com_chave)
        return com_chave

    @app.route("/segredos/<int:pk_segredo>", methods = ["DELETE"])
    @empty_json
    def excluir_segredo(pk_segredo: int) -> None:
        bodyless()
        sx.segredo.excluir_por_chave(ChaveSegredo(pk_segredo))

    @app.route("/segredos/<int:pk_segredo>")
    @jsoner
    def buscar_segredo_por_chave(pk_segredo: int) -> SegredoComChave:
        bodyless()
        return sx.segredo.buscar_por_chave(ChaveSegredo(pk_segredo))

    @app.route("/segredos")
    @jsoner
    def listar_segredos() -> ResultadoPesquisaDeSegredos:
        bodyless()
        return sx.segredo.listar()

    #### Front-end

    @app.route("/")
    def index() -> Response:
        bodyless()
        return redirect(url_for("static", filename = "index.html"))

    @app.route("/map")
    def map() -> str:
        prefix = f"http://127.0.0.1:{PORTA}/"
        x = ""
        for rule in app.url_map.iter_rules():
            for method in rule.methods if rule.methods is not None else []:
                j: str = ", ".join([str(arg) for arg in rule.arguments])
                f = f"function {rule.rule}({j}) {{\n    fetch(\"{prefix}/{rule}\");\n}}"
                x += str(rule.endpoint)
                x += f
        return x

    #### E aqui, a mágica acontece...

    app.run(host = "0.0.0.0", port = PORTA, debug = True)