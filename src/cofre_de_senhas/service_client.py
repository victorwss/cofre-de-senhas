from typing import Any, Literal, override, TypeAlias
from typing import TypeVar  # Delete when PEP 695 is ready.
from dacite import Config, from_dict
from enum import Enum, IntEnum
from validator import dataclass_validate
from dataclasses import dataclass
# from requests.cookies import RequestsCookieJar
from .service import (
    ServicoBD, ServicoUsuario, ServicoCategoria, ServicoSegredo, Servicos,
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
from sucesso import ConteudoBloqueadoException
from sucesso import Ok
from sucesso import RequisicaoMalFormadaException, PrecondicaoFalhouException, ConteudoNaoReconhecidoException, ConteudoIncompreensivelException  # noqa: F401
from requester import Requester, RequesterStrategy, ErrorData
from typeor import typed


_T = TypeVar("_T")  # Delete when PEP 695 is ready.
_X = TypeVar("_X", bound = BaseException)  # Delete when PEP 695 is ready.

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
_CBE: TypeAlias = ConteudoBloqueadoException

_exceptions: list[type[BaseException]] = [
    UsuarioNaoLogadoException, UsuarioBanidoException, PermissaoNegadaException, SenhaErradaException, LoginExpiradoException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    SegredoNaoExisteException,
    ValorIncorretoException, ExclusaoSemCascataException,
    ConteudoBloqueadoException
]
_exceptions_names: dict[str, type[BaseException]] = {x.__name__: x for x in _exceptions}


@dataclass_validate
@dataclass(frozen = True)
class _Empty:
    pass


@dataclass_validate
@dataclass(frozen = True)
class _ErroRemoto:
    sucesso: Literal[False]
    interno: bool
    tipo: str
    mensagem: str

    @property
    def error_data(self) -> ErrorData:
        return ErrorData(self.interno, self.tipo, self.mensagem)


def _sucesso(j: Any) -> bool:
    return "sucesso" in j and j["sucesso"] is True and "conteudo" in j


def _error_maker(j: Any) -> ErrorData:
    return from_dict(data_class = _ErroRemoto, data = j, config = Config(cast = [Enum, IntEnum])).error_data


def _result_maker(j: Any, t: type[_T]) -> _T:
    return from_dict(data_class = t, data = j["conteudo"], config = Config(cast = [Enum, IntEnum]))


def _eval(error_type: str, error_message: str) -> Any:
    if error_type not in _exceptions_names:
        raise NameError(error_type)
    return _exceptions_names[error_type]()


class ServicosClient(Servicos):

    def __init__(self, url: str) -> None:
        stt: RequesterStrategy = RequesterStrategy(_sucesso, _error_maker, Ok, _result_maker, _eval)
        self.__requester: Requester = Requester(url, stt)

    @property
    @override
    def bd(self) -> ServicoBD:
        return _ServicoBDClient(self.__requester)

    @property
    @override
    def usuario(self) -> ServicoUsuario:
        return _ServicoUsuarioClient(self.__requester)

    @property
    @override
    def categoria(self) -> ServicoCategoria:
        return _ServicoCategoriaClient(self.__requester)

    @property
    @override
    def segredo(self) -> ServicoSegredo:
        return _ServicoSegredoClient(self.__requester)


class _ServicoBDClient(ServicoBD):

    def __init__(self, requester: Requester) -> None:
        self.__requester: Requester = requester

    @override
    def criar_bd(self) -> None:
        raise NotImplementedError("Não implementado")

    @override
    def criar_admin(self, dados: LoginComSenha) -> UsuarioComChave | _VIE | _UJEE | _CBE:
        return self.__requester.put(
            f"/admin/nome/{dados.login}",
            dados.internos,
            UsuarioComChave,
            typed(_VIE).join(_UJEE).join(_CBE).end
        )


class _ServicoUsuarioClient(ServicoUsuario):

    def __init__(self, requester: Requester) -> None:
        self.__requester: Requester = requester

    @override
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        return self.__requester.post("/login", quem_faz, UsuarioComChave, typed(_UBE).join(_SEE).end)

    @override
    def logout(self) -> None:
        self.__requester.post("/logout", _Empty(), type(None), typed(str).end)

    @override
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave | _UNLE | _UBE | _PNE | _UJEE | _LEE | _VIE:
        return self.__requester.put(
            f"/usuarios/nome/{dados.login}",
            dados.internos,
            UsuarioComChave,
            typed(_UNLE).join(_UBE).join(_PNE).join(_UJEE).join(_LEE).join(_VIE).end
        )

    @override
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None | _UNLE | _UBE | _LEE:
        return self.__requester.post("/trocar-senha", dados, type(None), typed(_UNLE).join(_UBE).join(_LEE).end)

    @override
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        return self.__requester.post(
            f"/usuarios/nome/{dados.login}/resetar-senha",
            _Empty(),
            SenhaAlterada,
            typed(_UNLE).join(_UBE).join(_PNE).join(_UNEE).join(_LEE).end
        )

    @override
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        return self.__requester.post(
            f"/usuarios/nome/{dados.login}/alterar-nivel",
            dados.internos,
            type(None),
            typed(_UNLE).join(_UBE).join(_PNE).join(_UNEE).join(_LEE).end
        )

    @override
    def renomear_por_login(self, dados: RenomeUsuario) -> None | _UNLE | _UNEE | _UJEE | _UBE | _PNE | _LEE | _VIE:
        return self.__requester.move(
            f"/usuarios/nome/{dados.antigo}",
            dados.novo,
            False,
            type(None),
            typed(_UNLE).join(_UNEE).join(_UJEE).join(_UBE).join(_PNE).join(_LEE).join(_VIE).end
        )

    @override
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        return self.__requester.get(f"/usuarios/nome/{dados.login}", UsuarioComChave, typed(_UNLE).join(_UBE).join(_UNEE).join(_LEE).end)

    @override
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        return self.__requester.get(f"/usuarios/chave/{chave.valor}", UsuarioComChave, typed(_UNLE).join(_UBE).join(_UNEE).join(_LEE).end)

    @override
    def listar(self) -> ResultadoListaDeUsuarios | _UNLE | _UBE | _LEE:
        return self.__requester.get("/usuarios", ResultadoListaDeUsuarios, typed(_UNLE).join(_UBE).join(_LEE).end)


class _ServicoSegredoClient(ServicoSegredo):

    def __init__(self, requester: Requester) -> None:
        self.__requester: Requester = requester

    @override
    def criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE | _LEE | _VIE:
        return self.__requester.put("/segredos", dados, SegredoComChave, typed(_UNLE).join(_UBE).join(_UNEE).join(_CNEE).join(_LEE).join(_VIE).end)

    @override
    def alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE | _VIE:
        return self.__requester.put(
            f"/segredos/chave/{dados.chave.valor}",
            dados.sem_chave,
            type(None),
            typed(_UNLE).join(_UNEE).join(_UBE).join(_SNEE).join(_PNE).join(_CNEE).join(_LEE).join(_VIE).end
        )

    @override
    def excluir_por_chave(self, dados: ChaveSegredo) -> None | _UNLE | _UBE | _SNEE | _PNE | _LEE:
        return self.__requester.delete(f"/segredos/chave/{dados.valor}", type(None), typed(_UNLE).join(_UBE).join(_SNEE).join(_PNE).join(_LEE).end)

    @override
    def listar(self) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _LEE:
        return self.__requester.get("/segredos", ResultadoPesquisaDeSegredos, typed(_UNLE).join(_UBE).join(_LEE).end)

    @override
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE | _LEE:
        return self.__requester.get(f"/segredos/chave/{chave.valor}", SegredoComChave, typed(_UNLE).join(_UBE).join(_SNEE).join(_LEE).end)

    @override
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _SNEE:
        raise NotImplementedError("Não implementado")


class _ServicoCategoriaClient(ServicoCategoria):

    def __init__(self, requester: Requester) -> None:
        self.__requester: Requester = requester

    @override
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        return self.__requester.get(f"/categorias/nome/{dados.nome}", CategoriaComChave, typed(_UNLE).join(_UBE).join(_CNEE).join(_LEE).end)

    @override
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        return self.__requester.get(f"/categorias/chave/{chave.valor}", CategoriaComChave, typed(_UNLE).join(_UBE).join(_CNEE).join(_LEE).end)

    @override
    def criar(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _LEE | _UBE | _PNE | _CJEE | _VIE:
        return self.__requester.put(
            f"/categorias/nome/{dados.nome}",
            _Empty(),
            CategoriaComChave,
            typed(_UNLE).join(_LEE).join(_UBE).join(_PNE).join(_CJEE).join(_VIE).end
        )

    @override
    def renomear_por_nome(self, dados: RenomeCategoria) -> None | _UNLE | _UBE | _PNE | _CJEE | _CNEE | _VIE | _LEE:
        return self.__requester.move(
            f"/categorias/nome/{dados.antigo}",
            dados.novo,
            False,
            type(None),
            typed(_UNLE).join(_UBE).join(_PNE).join(_CJEE).join(_CNEE).join(_VIE).join(_LEE).end
        )

    @override
    def excluir_por_nome(self, dados: NomeCategoria) -> None | _UNLE | _UBE | _PNE | _CNEE | _LEE | _ESCE:
        return self.__requester.delete(
            f"/categorias/nome/{dados.nome}",
            type(None),
            typed(_UNLE).join(_UBE).join(_PNE).join(_CNEE).join(_LEE).join(_ESCE).end
        )

    @override
    def listar(self) -> ResultadoListaDeCategorias | _UNLE | _UBE | _LEE:
        return self.__requester.get("/categorias", ResultadoListaDeCategorias, typed(_UNLE).join(_UBE).join(_LEE).end)
