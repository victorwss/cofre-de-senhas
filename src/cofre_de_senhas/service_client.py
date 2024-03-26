import requests
from typing import Any, Literal, override, TypeAlias, TYPE_CHECKING
from typing import Generic, TypeVar  # Delete when PEP 695 is ready.
from dacite import Config, from_dict
from enum import Enum, IntEnum
from validator import dataclass_validate
from dataclasses import asdict, dataclass
from requests.models import Response
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
from sucesso import Ok, Status
from sucesso import RequisicaoMalFormadaException, PrecondicaoFalhouException, ConteudoNaoReconhecidoException, ConteudoIncompreensivelException  # noqa: F401


if TYPE_CHECKING:
    from _typeshed import DataclassInstance
    _D = TypeVar("_D", bound = DataclassInstance)
else:
    _D = TypeVar("_D")

_T = TypeVar("_T")  # Delete when PEP 695 is ready.
_X = TypeVar("_X")  # Delete when PEP 695 is ready.

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


class OngoingTyping(Generic[_X]):

    def __init__(self, x: type[_X]) -> None:
        self.__x: type[_X] = x

    def join(self, t: type[_T]) -> "OngoingTyping[_X | _T]":
        return OngoingTyping(self.__x | t)   # type: ignore

    @property
    def end(self) -> type[_X]:
        return self.__x


def typed(x: type[_X]) -> OngoingTyping[_X]:
    return OngoingTyping(x)


class _ErroDesconhecido(Exception):
    def __init__(self, dados: Any):
        super(_ErroDesconhecido, self).__init__(dados)


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

    def __eval(self) -> Any:
        try:
            return eval(self.tipo)()
        except BaseException:
            raise _ErroDesconhecido(f"[{self.tipo}] {self.mensagem}")

    # def __raise_it[X](self, j: Any, x: type[X]) -> X:  # PEP 695
    def raise_it(self, x: type[_X]) -> _X:
        z: Any = self.__eval()
        if isinstance(z, x):
            return z
        if isinstance(z, Status) and isinstance(z, BaseException):
            raise z
        raise _ErroDesconhecido(f"[{self.tipo}] {self.mensagem}")


def _islist(e: Any) -> bool:
    return isinstance(e, set) or isinstance(e, frozenset) or isinstance(e, tuple)


def _is_inside(x: Any, recurse_guard: list[Any]) -> bool:
    for k in recurse_guard:
        if x is k:
            return True
    return False


def _dictfix_in(x: dict[Any, Any], recurse_guard: list[Any]) -> dict[Any, Any]:
    if _is_inside(x, recurse_guard):
        return x
    for i in list(x.keys()):
        e: Any = x[i]
        if _islist(e):
            x[i] = list(e)
        elif isinstance(e, dict):
            recurse_guard.append(x)
            x[i] = _dictfix_in(e, recurse_guard)
            recurse_guard.pop()
    return x


def dictfix(x: dict[Any, Any]) -> dict[Any, Any]:
    return _dictfix_in(x, [])


class _Requester:

    def __init__(self, url: str) -> None:
        self.__base_url: str = url
        self.__session: requests.Session = requests.Session()
        self.__cookies: dict[str, str] = {}
        self.__session.trust_env = False

    # def get[T, X](self, path: str, t: type[T], x: type[X]) -> T | X: # PEP 695
    def get(self, path: str, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.get(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def post[T, X](self, path: str, data: _D, t: type[T], x: type[X]) -> T | X: # PEP 695
    def post(self, path: str, data: _D, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.post(self.__base_url + path, json = dictfix(asdict(data)), cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def put[T, X](self, path: str, data: _D, t: type[T], x: type[X]) -> T | X: # PEP 695
    def put(self, path: str, data: _D, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.put(self.__base_url + path, json = dictfix(asdict(data)), cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def delete[T, X](self, path: str, t: type[T], x: type[X]) -> T | X: # PEP 695
    def delete(self, path: str, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = self.__session.delete(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def move[T, X](self, path: str, to: str, overwrite: bool, t: type[T], x: type[X]) -> T | X: # PEP 695
    def move(self, path: str, to: str, overwrite: bool, t: type[_T], x: type[_X]) -> _T | _X:
        h: dict[str, str] = {
            "Destination": to,
            "Overwrite": "T" if overwrite else "F"
        }
        r: Response = self.__session.request("MOVE", self.__base_url + path, cookies = self.__cookies, headers = h)
        return self.__unwrap(r, t, x)

    @staticmethod
    def __sucesso(j: Any) -> bool:
        return "sucesso" in j and j["sucesso"] is True and "conteudo" in j

    def __json_validate(self, j: Any, rt: str) -> _ErroRemoto | None:
        if _Requester.__sucesso(j):
            return None
        try:
            remoto: _ErroRemoto = from_dict(data_class = _ErroRemoto, data = j, config = Config(cast = [Enum, IntEnum]))
            if remoto.interno:
                raise _ErroDesconhecido(f"[{remoto.tipo}] {remoto.mensagem}")
            return remoto
        except BaseException:
            raise _ErroDesconhecido(rt)

    def __json_it(self, r: Response) -> Any:
        try:
            return r.json()
        except BaseException:
            raise _ErroDesconhecido(r.text)

    # def __unwrap[T, X](self, r: Response, t: type[T] | None, x: type[X]]) -> T | X: # PEP 695
    def __unwrap(self, r: Response, t: type[_T], x: type[_X]) -> _T | _X:
        self.__cookies = dict(r.cookies)
        print(self.__cookies)
        j: Any = self.__json_it(r)
        erro: _ErroRemoto | None = self.__json_validate(j, r.text)
        if erro is not None:
            return erro.raise_it(x)
        if t is type(None):
            from_dict(data_class = Ok, data = j["conteudo"], config = Config(cast = [Enum, IntEnum]))
            return None  # type: ignore
        return from_dict(data_class = t, data = j["conteudo"], config = Config(cast = [Enum, IntEnum]))


class ServicosClient(Servicos):

    def __init__(self, url: str) -> None:
        self.__requester: _Requester = _Requester(url)

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

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    @override
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        raise NotImplementedError("Não implementado")

    @override
    def criar_bd(self) -> None:
        raise NotImplementedError("Não implementado")

    @override
    def criar_admin(self, dados: LoginComSenha) -> UsuarioComChave | _VIE | _UJEE:
        raise NotImplementedError("Não implementado")


class _ServicoUsuarioClient(ServicoUsuario):

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

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

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    @override
    def criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE | _LEE | _VIE:
        return self.__requester.put("/segredos", dados, SegredoComChave, typed(_UNLE).join(_UBE).join(_UNEE).join(_CNEE).join(_LEE).join(_VIE).end)

    @override
    def alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UBE | _UNEE | _CNEE | _SNEE | _VIE:
        return self.__requester.put(
            f"/segredos/chave/{dados.chave.valor}",
            dados.sem_chave,
            type(None),
            typed(_UNLE).join(_UBE).join(_UNEE).join(_CNEE).join(_SNEE).join(_VIE).end
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

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    @override
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        return self.__requester.get(f"/categorias/nome/{dados.nome}", CategoriaComChave, typed(_UNLE).join(_UBE).join(_CNEE).join(_LEE).end)

    @override
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        return self.__requester.get(f"/categorias/chave/{chave.valor}", CategoriaComChave, typed(_UNLE).join(_UBE).join(_CNEE).join(_LEE).end)

    @override
    def criar(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CJEE | _LEE:
        return self.__requester.put(f"/categorias/nome/{dados.nome}", _Empty(), CategoriaComChave, typed(_UNLE).join(_UBE).join(_CJEE).join(_LEE).end)

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
        return self.__requester.delete(f"/categorias/nome/{dados.nome}", type(None), typed(_UNLE).join(_UBE).join(_PNE).join(_CNEE).join(_LEE).join(_ESCE).end)

    @override
    def listar(self) -> ResultadoListaDeCategorias | _UNLE | _UBE | _LEE:
        return self.__requester.get("/categorias", ResultadoListaDeCategorias, typed(_UNLE).join(_UBE).join(_LEE).end)
