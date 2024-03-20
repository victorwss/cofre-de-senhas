from typing import Any, Callable, override, TypeAlias, TypeVar
from threading import Thread
from flask import Flask, redirect, session, url_for
from werkzeug import Response
from werkzeug.serving import BaseWSGIServer, make_server
from httpwrap import empty_json, bodyless, jsoner, move
from sucesso import PrecondicaoFalhouException, ConteudoIncompreensivelException
from webrpc import from_body_typed, from_path, from_path_int, WebSuite
from .service import (
    Servicos,
    GerenciadorLogin, UsuarioComChave, ChaveUsuario, NivelAcesso, UsuarioComNivel,
    UsuarioNovo, DadosNovoUsuario, RenomeUsuario, LoginComSenha, LoginUsuario, TrocaSenha, SenhaAlterada, ResetLoginUsuario, ResultadoListaDeUsuarios,
    NomeCategoria, CategoriaComChave, ChaveCategoria, RenomeCategoria, ResultadoListaDeCategorias,
    SegredoComChave, SegredoSemChave, ChaveSegredo, ResultadoPesquisaDeSegredos
)
from .erro import (
    UsuarioNaoLogadoException, UsuarioBanidoException, PermissaoNegadaException, SenhaErradaException, LoginExpiradoException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    SegredoNaoExisteException,
    ValorIncorretoException
)
from .service_impl import ServicosImpl
from .bd.bd_dao_impl import CofreDeSenhasDAOImpl
from .categoria.categoria_dao_impl import CategoriaDAOImpl
from .usuario.usuario_dao_impl import UsuarioDAOImpl
from .segredo.segredo_dao_impl import SegredoDAOImpl
from connection.trans import TransactedConnection
from connection.load import DatabaseConfig
from dacite import from_dict


_UNLE: TypeAlias = UsuarioNaoLogadoException
_UBE: TypeAlias = UsuarioBanidoException
_PNE: TypeAlias = PermissaoNegadaException
_UNEE: TypeAlias = UsuarioNaoExisteException
_UJEE: TypeAlias = UsuarioJaExisteException
_CNEE: TypeAlias = CategoriaNaoExisteException
_CJEE: TypeAlias = CategoriaJaExisteException
_SNEE: TypeAlias = SegredoNaoExisteException
_SEE: TypeAlias = SenhaErradaException
_VIE: TypeAlias = ValorIncorretoException
_LEE: TypeAlias = LoginExpiradoException


class GerenciadorLoginImpl(GerenciadorLogin):

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        print(f"Login {usuario}")
        session["chave"] = usuario.chave

    @override
    def logout(self) -> None:
        print("Logout")
        session.pop("chave", None)

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | _UNLE:
        if "chave" not in session:
            return UsuarioNaoLogadoException()
        return from_dict(data_class = ChaveUsuario, data = session["chave"])


_X = TypeVar("_X")


def _check(a: Any) -> None:
    if isinstance(a, BaseException):
        raise a


def _thrower(a: type[_X], b: _X | BaseException) -> _X:
    if isinstance(b, BaseException):
        raise b
    return b


def servir(porta: int, config: DatabaseConfig) -> Callable[[], None]:
    app: Flask = Flask(__name__)
    app.secret_key = ""
    ws: WebSuite = WebSuite(app, "/map")

    gl: GerenciadorLogin = GerenciadorLoginImpl()
    cofre: TransactedConnection = config.connect()

    CategoriaDAOImpl(cofre)
    CofreDeSenhasDAOImpl(cofre)
    SegredoDAOImpl(cofre)
    UsuarioDAOImpl(cofre)
    sx: Servicos = ServicosImpl(gl, cofre)

    segredo_chave: SegredoComChave | _SNEE = sx.bd.buscar_por_chave_sem_logar(ChaveSegredo(-1))
    if not isinstance(segredo_chave, SegredoComChave):
        raise segredo_chave
    app.secret_key = segredo_chave.campos["Chave da sessão"]

    # Usuários

    @ws.route("POST", "/login", from_body_typed("body", LoginComSenha))
    @jsoner
    def login(body: LoginComSenha) -> UsuarioComChave:
        return _thrower(UsuarioComChave, sx.usuario.login(body))

    @ws.route("POST", "/logout")
    @empty_json
    def logout() -> None:
        bodyless()
        sx.usuario.logout()

    @ws.route("GET", "/usuarios")
    @jsoner
    def listar_usuarios() -> ResultadoListaDeUsuarios:
        bodyless()
        return _thrower(ResultadoListaDeUsuarios, sx.usuario.listar())

    @ws.route("GET", "/usuarios/<pk_usuario>", from_path_int("pk_usuario"))
    @jsoner
    def buscar_usuario_por_chave(pk_usuario: int) -> UsuarioComChave:
        bodyless()
        return _thrower(UsuarioComChave, sx.usuario.buscar_por_chave(ChaveUsuario(pk_usuario)))

    @ws.route("GET", "/usuarios/<nome>", from_path("nome"))
    @jsoner
    def buscar_usuario_por_login(nome: str) -> UsuarioComChave:
        bodyless()
        return _thrower(UsuarioComChave, sx.usuario.buscar_por_login(LoginUsuario(nome)))

    @ws.route("PUT", "/usuarios/<nome>", from_path("nome"), from_body_typed("dados", DadosNovoUsuario))
    @jsoner
    def criar_usuario(nome: str, dados: DadosNovoUsuario) -> UsuarioComChave:
        try:
            p: NivelAcesso = dados.nivel
        except TypeError:
            raise ConteudoIncompreensivelException()
        return _thrower(UsuarioComChave, sx.usuario.criar(UsuarioNovo(nome, p, dados.senha)))

    @ws.route("POST", "/trocar-senha", from_body_typed("dados", TrocaSenha))
    @empty_json
    def trocar_senha(dados: TrocaSenha) -> None:
        _check(sx.usuario.trocar_senha_por_chave(dados))

    @ws.route("POST", "/usuarios/<nome>/alterar-nivel", from_path("nome"), from_body_typed("dados", DadosNovoUsuario))
    @empty_json
    def alterar_nivel(nome: str, dados: DadosNovoUsuario) -> None:
        try:
            p: NivelAcesso = dados.nivel
        except TypeError:
            raise ConteudoIncompreensivelException()
        _check(sx.usuario.alterar_nivel_por_login(UsuarioComNivel(nome, p)))

    @ws.route("MOVE", "/usuarios/<nome>", from_path("nome"))
    @jsoner
    def renomear_usuario(nome: str) -> None:
        bodyless()
        dest, overwrite = move()
        z: None | _UNLE | _UNEE | _UJEE | _UBE | _PNE | _LEE | _VIE = sx.usuario.renomear_por_login(RenomeUsuario(nome, dest))
        if isinstance(z, UsuarioJaExisteException) and not overwrite:
            raise PrecondicaoFalhouException()
        _check(z)

    @ws.route("POST", "/usuarios/<nome>/resetar-senha", from_path("nome"))
    @jsoner
    def resetar_senha(nome: str) -> SenhaAlterada:
        bodyless()
        return _thrower(SenhaAlterada, sx.usuario.resetar_senha_por_login(ResetLoginUsuario(nome)))

    # Categorias

    @ws.route("GET", "/categorias/<pk_categoria>", from_path_int("pk_categoria"))
    @jsoner
    def buscar_categoria_por_chave(pk_categoria: int) -> CategoriaComChave:
        bodyless()
        return _thrower(CategoriaComChave, sx.categoria.buscar_por_chave(ChaveCategoria(pk_categoria)))

    @ws.route("GET", "/categorias/<nome>", from_path("nome"))
    @jsoner
    def buscar_categoria_por_nome(nome: str) -> CategoriaComChave:
        bodyless()
        return _thrower(CategoriaComChave, sx.categoria.buscar_por_nome(NomeCategoria(nome)))

    @ws.route("PUT", "/categorias/<nome>", from_path("nome"))
    @jsoner
    def criar_categoria(nome: str) -> CategoriaComChave:
        bodyless()
        return _thrower(CategoriaComChave, sx.categoria.criar(NomeCategoria(nome)))

    @ws.route("MOVE", "/categorias/<nome>", from_path("nome"))
    @empty_json
    def renomear_categoria(nome: str) -> None:
        bodyless()
        dest, overwrite = move()
        z: None | _UNLE | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE = sx.categoria.renomear_por_nome(RenomeCategoria(nome, dest))
        if isinstance(z, CategoriaJaExisteException) and not overwrite:
            raise PrecondicaoFalhouException()
        _check(z)

    @ws.route("GET", "/categorias")
    @jsoner
    def listar_categorias() -> ResultadoListaDeCategorias:
        bodyless()
        return _thrower(ResultadoListaDeCategorias, sx.categoria.listar())

    @ws.route("DELETE", "/categorias/<nome>", from_path("nome"))
    @empty_json
    def excluir_categoria(nome: str) -> None:
        bodyless()
        _check(sx.categoria.excluir_por_nome(NomeCategoria(nome)))

    # Segredos

    @ws.route("PUT", "/segredos", from_body_typed("dados", SegredoSemChave))
    @jsoner
    def criar_segredo(dados: SegredoSemChave) -> SegredoComChave:
        return _thrower(SegredoComChave, sx.segredo.criar(dados))

    @ws.route("PUT", "/segredos/<pk_segredo>", from_path_int("pk_segredo"), from_body_typed("dados", SegredoSemChave))
    @jsoner
    def alterar_segredo(pk_segredo: int, dados: SegredoSemChave) -> SegredoComChave:
        com_chave: SegredoComChave = dados.com_chave(ChaveSegredo(pk_segredo))
        sx.segredo.alterar_por_chave(com_chave)
        return com_chave

    @ws.route("DELETE", "/segredos/<pk_segredo>", from_path_int("pk_segredo"))
    @empty_json
    def excluir_segredo(pk_segredo: int) -> None:
        bodyless()
        _check(sx.segredo.excluir_por_chave(ChaveSegredo(pk_segredo)))

    @ws.route("GET", "/segredos/<pk_segredo>", from_path_int("pk_segredo"))
    @jsoner
    def buscar_segredo_por_chave(pk_segredo: int) -> SegredoComChave:
        bodyless()
        return _thrower(SegredoComChave, sx.segredo.buscar_por_chave(ChaveSegredo(pk_segredo)))

    @ws.route("GET", "/segredos")
    @jsoner
    def listar_segredos() -> ResultadoPesquisaDeSegredos:
        bodyless()
        return _thrower(ResultadoPesquisaDeSegredos, sx.segredo.listar())

    # @ws.route("GET", "/segredos/...")
    # @jsoner
    # def pesquisar_segredos() -> ResultadoPesquisaDeSegredos:
    #     return _thrower(ResultadoPesquisaDeSegredos, sx.segredo.pesquisar(PesquisaSegredos(...)))

    @ws.route("GET", "/healthcheck")
    @empty_json
    def health_check() -> None:
        bodyless()

    # Front-end

    @app.route("/")
    def index() -> Response:
        bodyless()
        return redirect(url_for("static", filename = "index.html"))

    # E aqui, a mágica acontece...

    server: BaseWSGIServer = make_server("0.0.0.0", porta, app, True)
    app.app_context().push()

    def trabalho() -> None:
        server.serve_forever()

    def stop() -> None:
        server.shutdown()

    t: Thread = Thread(target = trabalho)
    t.start()

    return stop
