from typing import cast, override
from flask import Flask, redirect, session, url_for
from werkzeug import Response
from httpwrap import empty_json, bodyless, jsoner, read_body, move
from sucesso import PrecondicaoFalhouException, ConteudoIncompreensivelException
from webrpc import WebParam, WebSuite, from_body_typed, from_path, from_path_int
from .service import (
    GerenciadorLogin, UsuarioComChave, ChaveUsuario, NivelAcesso, UsuarioComNivel,
    UsuarioNovo, LoginComSenha, LoginUsuario, TrocaSenha, SenhaAlterada, ResetLoginUsuario, ResultadoListaDeUsuarios,
    NomeCategoria, CategoriaComChave, ChaveCategoria, RenomeCategoria, ResultadoListaDeCategorias,
    SegredoComChave, SegredoSemChave, ChaveSegredo, ResultadoPesquisaDeSegredos
)
from .service_impl import Servicos
from .erro import UsuarioNaoLogadoException, CategoriaJaExisteException
from validator import dataclass_validate
from dataclasses import dataclass
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
        # if app.secret_key == "":
        #    return ChaveUsuario(-1)
        if "chave" not in session:
            raise UsuarioNaoLogadoException()
        return cast(ChaveUsuario, session["chave"])


@dataclass_validate
@dataclass(frozen = True)
class DadosNovoUsuario:
    senha: str
    nivel_acesso: str


def servir() -> None:
    PORTA: int = 5000
    app: Flask = Flask(__name__)
    app.secret_key = ""
    ws: WebSuite = WebSuite(app, "/map")

    gl: GerenciadorLogin = GerenciadorLoginImpl()
    cofre: TransactedConnection = connect()

    CategoriaDAOImpl(cofre)
    CofreDeSenhasDAOImpl(cofre)
    SegredoDAOImpl(cofre)
    UsuarioDAOImpl(cofre)
    sx: Servicos = Servicos(gl, cofre)

    app.secret_key = sx.segredo.buscar_por_chave_sem_logar(ChaveSegredo(-1)).campos["Chave da sessão"]

    # Usuários

    @ws.route("POST", "/login", WebParam("body", from_body_typed(LoginComSenha)))
    @empty_json
    def login(body: LoginComSenha) -> None:
        sx.usuario.login(body)

    @ws.route("POST", "/logout")
    @empty_json
    def logout() -> None:
        bodyless()
        sx.usuario.logout()

    @ws.route("GET", "/usuarios")
    @jsoner
    def listar_usuarios() -> ResultadoListaDeUsuarios:
        bodyless()
        return sx.usuario.listar()

    @ws.route("GET", "/usuarios/<pk_usuario>", WebParam("pk_usuario", from_path_int("pk_usuario")))
    @jsoner
    def buscar_usuario_por_chave(pk_usuario: int) -> UsuarioComChave:
        bodyless()
        return sx.usuario.buscar_por_chave(ChaveUsuario(pk_usuario))

    @ws.route("GET", "/usuarios/<nome>", WebParam("nome", from_path("nome")))
    @jsoner
    def buscar_usuario_por_login(nome: str) -> UsuarioComChave:
        bodyless()
        return sx.usuario.buscar_por_login(LoginUsuario(nome))

    @ws.route("PUT", "/usuarios/<nome>", WebParam("nome", from_path("nome")))
    @jsoner
    def criar_usuario(nome: str) -> UsuarioComChave:
        dados: DadosNovoUsuario = read_body(DadosNovoUsuario)
        try:
            p: NivelAcesso = NivelAcesso[dados.nivel_acesso]
        except BaseException as e:  # noqa: F841
            raise ConteudoIncompreensivelException()
        return sx.usuario.criar(UsuarioNovo(nome, p, dados.senha))

    @ws.route("POST", "/trocar-senha")
    @empty_json
    def trocar_senha() -> None:
        dados: TrocaSenha = read_body(TrocaSenha)
        return sx.usuario.trocar_senha_por_chave(dados)

    @dataclass_validate
    @dataclass(frozen = True)
    class DadosNovoNivel:
        nivel_acesso: str

    @ws.route("POST", "/usuarios/<nome>/alterar-nivel", WebParam("nome", from_path("nome")))
    @empty_json
    def alterar_nivel(nome: str) -> None:
        dados: DadosNovoUsuario = read_body(DadosNovoUsuario)
        try:
            p: NivelAcesso = NivelAcesso[dados.nivel_acesso]
        except BaseException as e:  # noqa: F841
            raise ConteudoIncompreensivelException()
        sx.usuario.alterar_nivel_por_login(UsuarioComNivel(nome, p))

    @ws.route("POST", "/usuarios/<nome>/resetar-senha", WebParam("nome", from_path("nome")))
    @jsoner
    def resetar_senha(nome: str) -> SenhaAlterada:
        bodyless()
        return sx.usuario.resetar_senha_por_login(ResetLoginUsuario(nome))

    # Categorias

    @ws.route("GET", "/categorias/<pk_categoria>", WebParam("pk_categoria", from_path_int("pk_categoria")))
    @jsoner
    def buscar_categoria_por_chave(pk_categoria: int) -> CategoriaComChave:
        bodyless()
        return sx.categoria.buscar_por_chave(ChaveCategoria(pk_categoria))

    @ws.route("GET", "/categorias/<nome>", WebParam("nome", from_path("nome")))
    @jsoner
    def buscar_categoria_por_nome(nome: str) -> CategoriaComChave:
        bodyless()
        return sx.categoria.buscar_por_nome(NomeCategoria(nome))

    @ws.route("PUT", "/categorias/<nome>", WebParam("nome", from_path("nome")))
    @jsoner
    def criar_categoria(nome: str) -> CategoriaComChave:
        bodyless()
        return sx.categoria.criar(NomeCategoria(nome))

    @ws.route("MOVE", "/categorias/<nome>", WebParam("nome", from_path("nome")))
    @empty_json
    def renomear_categoria(nome: str) -> None:
        bodyless()
        dest, overwrite = move()
        try:
            sx.categoria.renomear_por_nome(RenomeCategoria(nome, dest))
        except CategoriaJaExisteException as x:  # noqa: F841
            if not overwrite:
                raise PrecondicaoFalhouException()
            raise x

    @ws.route("GET", "/categorias")
    @jsoner
    def listar_categorias() -> ResultadoListaDeCategorias:
        bodyless()
        return sx.categoria.listar()

    @ws.route("DELETE", "/categorias/<nome>", WebParam("nome", from_path("nome")))
    @empty_json
    def excluir_categoria(nome: str) -> None:
        bodyless()
        sx.categoria.excluir_por_nome(NomeCategoria(nome))

    # Segredos

    @ws.route("PUT", "/segredos")
    @jsoner
    def criar_segredo() -> SegredoComChave:
        dados: SegredoSemChave = read_body(SegredoSemChave)
        return sx.segredo.criar(dados)

    @ws.route("PUT", "/segredos/<pk_segredo>", WebParam("pk_segredo", from_path_int("pk_segredo")))
    @jsoner
    def alterar_segredo(pk_segredo: int) -> SegredoComChave:
        dados: SegredoSemChave = read_body(SegredoSemChave)
        com_chave: SegredoComChave = dados.com_chave(ChaveSegredo(pk_segredo))
        sx.segredo.alterar_por_chave(com_chave)
        return com_chave

    @ws.route("DELETE", "/segredos/<pk_segredo>", WebParam("pk_segredo", from_path_int("pk_segredo")))
    @empty_json
    def excluir_segredo(pk_segredo: int) -> None:
        bodyless()
        sx.segredo.excluir_por_chave(ChaveSegredo(pk_segredo))

    @ws.route("GET", "/segredos/<pk_segredo>", WebParam("pk_segredo", from_path_int("pk_segredo")))
    @jsoner
    def buscar_segredo_por_chave(pk_segredo: int) -> SegredoComChave:
        bodyless()
        return sx.segredo.buscar_por_chave(ChaveSegredo(pk_segredo))

    @ws.route("GET", "/segredos")
    @jsoner
    def listar_segredos() -> ResultadoPesquisaDeSegredos:
        bodyless()
        return sx.segredo.listar()

    # Front-end

    @app.route("/")
    def index() -> Response:
        bodyless()
        return redirect(url_for("static", filename = "index.html"))

    # E aqui, a mágica acontece...

    app.run(host = "0.0.0.0", port = PORTA, debug = True)
