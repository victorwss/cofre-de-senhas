from typing import override, ParamSpec, TypeAlias, TypeVar
from decorators.for_all import for_all_methods
from connection.trans import TransactedConnection
from .service import (
    GerenciadorLogin, ServicoBD, ServicoUsuario, ServicoCategoria, ServicoSegredo, Servicos,
    UsuarioComChave, ChaveUsuario, LoginUsuario, LoginComSenha, ResultadoListaDeUsuarios,
    TrocaSenha, SenhaAlterada, UsuarioComNivel, UsuarioNovo, ResetLoginUsuario, RenomeUsuario,
    CategoriaComChave, ChaveCategoria, NomeCategoria, RenomeCategoria, ResultadoListaDeCategorias,
    SegredoComChave, SegredoSemChave, ChaveSegredo, PesquisaSegredos, ResultadoPesquisaDeSegredos,
)
from .erro import (
    UsuarioNaoLogadoException, UsuarioBanidoException, PermissaoNegadaException, SenhaErradaException, LoginExpiradoException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    SegredoNaoExisteException,
    ValorIncorretoException, ExclusaoSemCascataException
)
from .dao import CofreDeSenhasDAO
from .categoria.categoria import ServicosImpl as CategoriaServicoInternoImpl
from .usuario.usuario import ServicosImpl as UsuarioServicoInternoImpl
from .segredo.segredo import ServicosImpl as SegredoServicoInternoImpl
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
_ESCE: TypeAlias = ExclusaoSemCascataException


class ServicosImpl(Servicos):

    def __init__(self, gl: GerenciadorLogin, trans: TransactedConnection) -> None:
        from .categoria.categoria_dao_impl import CategoriaDAOImpl
        from .usuario.usuario_dao_impl import UsuarioDAOImpl
        from .segredo.segredo_dao_impl import SegredoDAOImpl
        from .bd.bd_dao_impl import CofreDeSenhasDAOImpl

        self.__gl: GerenciadorLogin = gl
        self.__trans: TransactedConnection = trans

        udao: UsuarioDAOImpl = UsuarioDAOImpl(trans)
        cdao: CategoriaDAOImpl = CategoriaDAOImpl(trans)
        sdao: SegredoDAOImpl = SegredoDAOImpl(trans)
        bdao: CofreDeSenhasDAOImpl = CofreDeSenhasDAOImpl(trans)

        us: UsuarioServicoInternoImpl = UsuarioServicoInternoImpl(udao)
        cs: CategoriaServicoInternoImpl = CategoriaServicoInternoImpl(cdao, us)
        ss: SegredoServicoInternoImpl = SegredoServicoInternoImpl(sdao, us, cs)

        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna1(_ServicoBDImpl):
            def __init__(self) -> None:
                super().__init__(bdao, us, ss)

        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna2(_ServicoUsuarioImpl):
            def __init__(self) -> None:
                super().__init__(gl, us)

        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna3(_ServicoCategoriaImpl):
            def __init__(self) -> None:
                super().__init__(gl, cs)

        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna4(_ServicoSegredoImpl):
            def __init__(self) -> None:
                super().__init__(gl, ss)

        self.__bd: ServicoBD = Interna1()
        self.__usuario: ServicoUsuario = Interna2()
        self.__categoria: ServicoCategoria = Interna3()
        self.__segredo: ServicoSegredo = Interna4()

    @property
    @override
    def bd(self) -> ServicoBD:
        return self.__bd

    @property
    @override
    def usuario(self) -> ServicoUsuario:
        return self.__usuario

    @property
    @override
    def categoria(self) -> ServicoCategoria:
        return self.__categoria

    @property
    @override
    def segredo(self) -> ServicoSegredo:
        return self.__segredo


class _ServicoBDImpl(ServicoBD):

    def __init__(self, dao: CofreDeSenhasDAO, us: UsuarioServicoInternoImpl, ss: SegredoServicoInternoImpl) -> None:
        self.__dao: CofreDeSenhasDAO = dao
        self.__us: UsuarioServicoInternoImpl = us
        self.__ss: SegredoServicoInternoImpl = ss

    @override
    def criar_admin(self, dados: LoginComSenha) -> UsuarioComChave | _VIE | _UJEE:
        return self.__us.criar_admin(dados)

    @override
    def criar_bd(self) -> None:
        self.__dao.criar_bd()

    @override
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        return self.__ss.buscar_por_chave_sem_logar(chave)


class _ServicoUsuarioImpl(ServicoUsuario):

    def __init__(self, gl: GerenciadorLogin, us: UsuarioServicoInternoImpl) -> None:
        self.__gl: GerenciadorLogin = gl
        self.__us: UsuarioServicoInternoImpl = us

    @override
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        u: UsuarioComChave | _UBE | _SEE = self.__us.login(quem_faz)
        if isinstance(u, UsuarioComChave):
            self.__gl.login(u)
        return u

    @override
    def logout(self) -> None:
        self.__gl.logout()

    @override
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave | _UNLE | _UBE | _PNE | _UJEE | _LEE | _VIE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.criar(u, dados)

    @override
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None | _UNLE | _UBE | _SEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.trocar_senha_por_chave(u, dados)

    @override
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.resetar_senha_por_login(u, dados)

    @override
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.alterar_nivel_por_login(u, dados)

    @override
    def renomear_por_login(self, dados: RenomeUsuario) -> None | _UNLE | _UNEE | _UJEE | _UBE | _PNE | _LEE | _VIE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.renomear(u, dados)

    @override
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.buscar_por_login(u, dados)

    @override
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.buscar_por_chave(u, chave)

    @override
    def listar(self) -> ResultadoListaDeUsuarios | _UNLE | _UBE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__us.listar(u)


class _ServicoSegredoImpl(ServicoSegredo):

    def __init__(self, gl: GerenciadorLogin, ss: SegredoServicoInternoImpl) -> None:
        self.__gl: GerenciadorLogin = gl
        self.__ss: SegredoServicoInternoImpl = ss

    @override
    def criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE | _LEE | _VIE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__ss.criar(u, dados)

    @override
    def alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE | _VIE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__ss.alterar_por_chave(u, dados)

    @override
    def excluir_por_chave(self, dados: ChaveSegredo) -> None | _UNLE | _UBE | _SNEE | _PNE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__ss.excluir_por_chave(u, dados)

    @override
    def listar(self) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__ss.listar(u)

    @override
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__ss.buscar(u, chave)

    @override
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _SNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__ss.pesquisar(u, dados)


class _ServicoCategoriaImpl(ServicoCategoria):

    def __init__(self, gl: GerenciadorLogin, cs: CategoriaServicoInternoImpl) -> None:
        self.__gl: GerenciadorLogin = gl
        self.__cs: CategoriaServicoInternoImpl = cs

    @override
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__cs.buscar_por_nome(u, dados)

    @override
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__cs.buscar_por_chave(u, chave)

    @override
    def criar(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _LEE | _UBE | _PNE | _CJEE | _VIE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__cs.criar(u, dados)

    @override
    def renomear_por_nome(self, dados: RenomeCategoria) -> None | _UNLE | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__cs.renomear_por_nome(u, dados)

    @override
    def excluir_por_nome(self, dados: NomeCategoria) -> None | _UNLE | _UBE | _PNE | _CNEE | _LEE | _ESCE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__cs.excluir_por_nome(u, dados)

    @override
    def listar(self) -> ResultadoListaDeCategorias | _UNLE | _UBE | _LEE:
        u: ChaveUsuario | _UNLE = self.__gl.usuario_logado
        if isinstance(u, _UNLE):
            return u
        return self.__cs.listar(u)
