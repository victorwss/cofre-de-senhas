from typing import Callable, override, ParamSpec, TypeAlias, TypeVar
from decorators.for_all import for_all_methods
from connection.trans import TransactedConnection
from .service import (
    GerenciadorLogin, ServicoBD, ServicoUsuario, ServicoCategoria, ServicoSegredo,
    UsuarioComChave, ChaveUsuario, LoginUsuario, LoginComSenha, ResultadoListaDeUsuarios,
    TrocaSenha, SenhaAlterada, UsuarioComNivel, UsuarioNovo, ResetLoginUsuario,
    CategoriaComChave, ChaveCategoria, NomeCategoria, RenomeCategoria, ResultadoListaDeCategorias,
    SegredoComChave, SegredoSemChave, ChaveSegredo, PesquisaSegredos, ResultadoPesquisaDeSegredos,
)
from .erro import (
    UsuarioNaoLogadoException, UsuarioBanidoException, PermissaoNegadaException, SenhaErradaException, LoginExpiradoException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    SegredoNaoExisteException,
    ValorIncorretoException
)
from .dao import CofreDeSenhasDAO
from .categoria.categoria import Servicos as CategoriaServico
from .usuario.usuario import Servicos as UsuarioServico
from .segredo.segredo import Servicos as SegredoServico
from decorators.tracer import Logger

_log: Logger = Logger.for_print_fn()

_P = ParamSpec("_P")
_R = TypeVar("_R")

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


class Servicos:

    def __init__(self, gl: GerenciadorLogin, trans: TransactedConnection) -> None:
        self.__gl: GerenciadorLogin = gl
        self.__trans: TransactedConnection = trans

    @property
    def bd(self) -> ServicoBD:
        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        @for_all_methods(self.__inject)
        class Interna(_ServicoBDImpl):
            pass
        return Interna()

    @property
    def usuario(self) -> ServicoUsuario:
        gl: GerenciadorLogin = self.__gl

        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        @for_all_methods(self.__inject)
        class Interna(_ServicoUsuarioImpl):
            def __init__(self2) -> None:
                super().__init__(gl)
        return Interna()

    @property
    def categoria(self) -> ServicoCategoria:
        gl: GerenciadorLogin = self.__gl

        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        @for_all_methods(self.__inject)
        class Interna(_ServicoCategoriaImpl):
            def __init__(self2) -> None:
                super().__init__(gl)
        return Interna()

    @property
    def segredo(self) -> ServicoSegredo:
        gl: GerenciadorLogin = self.__gl

        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        @for_all_methods(self.__inject)
        class Interna(_ServicoSegredoImpl):
            def __init__(self2) -> None:
                super().__init__(gl)
        return Interna()

    def __inject(self, what: Callable[_P, _R]) -> Callable[_P, _R]:
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            from .categoria.categoria_dao_impl import CategoriaDAOImpl
            from .usuario.usuario_dao_impl import UsuarioDAOImpl
            from .segredo.segredo_dao_impl import SegredoDAOImpl
            from .bd.bd_dao_impl import CofreDeSenhasDAOImpl
            CofreDeSenhasDAOImpl(self.__trans)
            UsuarioDAOImpl(self.__trans)
            SegredoDAOImpl(self.__trans)
            CategoriaDAOImpl(self.__trans)
            return what(*args, **kwargs)
        return inner


class _ServicoBDImpl(ServicoBD):

    @override
    def criar_bd(self, dados: LoginComSenha) -> None:
        CofreDeSenhasDAO.instance().criar_bd()
        UsuarioServico.criar_admin(dados)


# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoUsuarioImpl(ServicoUsuario):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl: GerenciadorLogin = gl

    # Pode lançar SenhaErradaException
    @override
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        u: UsuarioComChave | _UBE | _SEE = UsuarioServico.login(quem_faz)
        if isinstance(u, UsuarioComChave):
            self.__gl.login(u)
        return u

    @override
    def logout(self) -> None:
        self.__gl.logout()

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @override
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave | _UNLE | _UBE | _PNE | _UJEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return UsuarioServico.criar(u, dados)

    @override
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None | _UNLE | _UBE | _SEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return UsuarioServico.trocar_senha_por_chave(u, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return UsuarioServico.resetar_senha_por_login(u, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return UsuarioServico.alterar_nivel_por_login(u, dados)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return UsuarioServico.buscar_por_login(u, dados)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return UsuarioServico.buscar_por_chave(u, chave)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def listar(self) -> ResultadoListaDeUsuarios | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return UsuarioServico.listar(u)


# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoSegredoImpl(ServicoSegredo):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl: GerenciadorLogin = gl

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @override
    def criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE | _PNE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return SegredoServico.criar(u, dados)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    @override
    def alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return SegredoServico.alterar_por_chave(u, dados)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    @override
    def excluir_por_chave(self, dados: ChaveSegredo) -> None | _UNLE | _UBE | _SNEE | _PNE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return SegredoServico.excluir_por_chave(u, dados)

    @override
    def listar(self) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return SegredoServico.listar(u)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return SegredoServico.buscar(u, chave)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        return SegredoServico.buscar_sem_logar(chave)

    # Pode lançar SegredoNaoExisteException
    @override
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _SNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return SegredoServico.pesquisar(u, dados)


# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoCategoriaImpl(ServicoCategoria):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl: GerenciadorLogin = gl

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return CategoriaServico.buscar_por_nome(u, dados)

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return CategoriaServico.buscar_por_chave(u, chave)

    # Pode lançar CategoriaJaExisteException
    @override
    def criar(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _LEE | _UBE | _PNE | _CJEE | _VIE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return CategoriaServico.criar(u, dados)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @override
    def renomear_por_nome(self, dados: RenomeCategoria) -> None | _UNLE | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return CategoriaServico.renomear_por_nome(u, dados)

    # Pode lançar CategoriaNaoExisteException
    @override
    def excluir_por_nome(self, dados: NomeCategoria) -> None | _UNLE | _UBE | _PNE | _CNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return CategoriaServico.excluir_por_nome(u, dados)

    @override
    def listar(self) -> ResultadoListaDeCategorias | _UNLE | _UBE | _CJEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return CategoriaServico.listar(u)
