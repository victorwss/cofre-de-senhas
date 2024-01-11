import requests
from typing import Any, override, TypeAlias
from typing import Generic, TypeVar  # Delete when PEP 695 is ready.
from dacite import Config, from_dict
from enum import Enum
from dataclasses import asdict
from requests.models import Response
# from requests.cookies import RequestsCookieJar
from .service import (
    ServicoBD, ServicoUsuario, ServicoCategoria, ServicoSegredo,
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
from sucesso import Ok


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
        super.__init__(dados)


class _Requester:

    def __init__(self) -> None:
        self.__base_url: str = "http://127.0.0.1:5000"
        self.__cookies: dict[str, str] = {}

    # def get[T, X](self, path: str, t: type[T], x: type[X]) -> T | X: # PEP 695
    def get(self, path: str, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = requests.get(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def post[T, X](self, path: str, json: Any, t: type[T], x: type[X]) -> T | X: # PEP 695
    def post(self, path: str, json: Any, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = requests.post(self.__base_url + path, json = json, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def put[T, X](self, path: str, json: Any, t: type[T], x: type[X]) -> T | X: # PEP 695
    def put(self, path: str, json: Any, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = requests.put(self.__base_url + path, json = json, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def delete[T, X](self, path: str, t: type[T], x: type[X]) -> T | X: # PEP 695
    def delete(self, path: str, t: type[_T], x: type[_X]) -> _T | _X:
        r: Response = requests.delete(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t, x)

    # def move[T, X](self, path: str, to: str, overwrite: bool, t: type[T], x: type[X]) -> T | X: # PEP 695
    def move(self, path: str, to: str, overwrite: bool, t: type[_T], x: type[_X]) -> _T | _X:
        h: dict[str, str] = {
            "Destination": to,
            "Overwrite": "T" if overwrite else "F"
        }
        r: Response = requests.request("MOVE", self.__base_url + path, cookies = self.__cookies, headers = h)
        return self.__unwrap(r, t, x)

    # def __unwrap[T, X](self, r: Response, t: type[T] | None, x: type[X]]) -> T | X: # PEP 695
    def __unwrap(self, r: Response, t: type[_T], x: type[_X]) -> _T | _X:
        self.__cookies = dict(r.cookies)
        j: Any
        try:
            j = r.json()
        except BaseException as e:  # noqa: F841
            raise _ErroDesconhecido(r.text)
        if "sucesso" not in j:
            raise _ErroDesconhecido(r.text)
        if j["sucesso"] is True:
            if t is type(None):
                from_dict(data_class = Ok, data = j["conteudo"], config = Config(cast = [Enum]))
                return None  # type: ignore
            return from_dict(data_class = t, data = j["conteudo"], config = Config(cast = [Enum]))
        if "interno" not in j or "tipo" not in j or "mensagem" not in j or j["interno"] not in [True, False]:
            raise _ErroDesconhecido(r.text)
        if j["interno"] is False:
            raise _ErroDesconhecido(f"[{j['tipo']}] {j['mensagem']}")

        z: Any
        try:
            z = eval(j["tipo"])()
        except BaseException as e:  # noqa: F841
            raise _ErroDesconhecido(f"[{j['tipo']}] {j['mensagem']}")
        if isinstance(z, x):
            return z
        raise _ErroDesconhecido(f"[{j['tipo']}] {j['mensagem']}")


class Servicos:

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    @property
    def bd(self) -> ServicoBD:
        return _ServicoBDClient(self.__requester)

    @property
    def usuario(self) -> ServicoUsuario:
        return _ServicoUsuarioClient(self.__requester)

    @property
    def categoria(self) -> ServicoCategoria:
        return _ServicoCategoriaClient(self.__requester)

    @property
    def segredo(self) -> ServicoSegredo:
        return _ServicoSegredoClient(self.__requester)


class _ServicoBDClient(ServicoBD):

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    @override
    def criar_bd(self, dados: LoginComSenha) -> None:
        raise Exception("Não implementado")


# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoUsuarioClient(ServicoUsuario):

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    # Pode lançar SenhaErradaException
    @override
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        return self.__requester.post("/login", asdict(quem_faz), UsuarioComChave, typed(_UBE).join(_SEE).end)

    @override
    def logout(self) -> None:
        self.__requester.post("/logout", {}, type(None), typed(str).end)

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @override
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave | _UNLE | _UBE | _PNE | _UJEE | _LEE:
        d: dict[str, Any] = {"senha": dados.senha, "nivel_acesso": dados.nivel_acesso}
        return self.__requester.put(f"/usuarios/{dados.login}", d, UsuarioComChave, typed(_UNLE).join(_UBE).join(_PNE).join(_UJEE).join(_LEE).end)

    @override
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None | _UNLE | _UBE:
        return self.__requester.post("/trocar-senha", dados, type(None), typed(_UNLE).join(_UBE).end)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada | _UNLE | _UBE | _PNE | _UNEE:
        return self.__requester.post(f"/usuarios/{dados.login}/resetar-senha", {}, SenhaAlterada, typed(_UNLE).join(_UBE).join(_PNE).join(_UNEE).end)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None | _UNLE | _UBE | _PNE | _UNEE:
        d: dict[str, Any] = {"nivel_acesso": dados.nivel_acesso}
        return self.__requester.post(f"/usuarios/{dados.login}/alterar-nivel", d, type(None), typed(_UNLE).join(_UBE).join(_PNE).join(_UNEE).end)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE:
        return self.__requester.get(f"/usuarios/{dados.login}", UsuarioComChave, typed(_UNLE).join(_UBE).join(_UNEE).end)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE:
        return self.__requester.get(f"/usuarios/{chave.valor}", UsuarioComChave, typed(_UNLE).join(_UBE).join(_UNEE).end)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def listar(self) -> ResultadoListaDeUsuarios | _UNLE | _UBE | _PNE | _UNEE:
        return self.__requester.get("/usuarios", ResultadoListaDeUsuarios, typed(_UNLE).join(_UBE).join(_PNE).join(_UNEE).end)


# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoSegredoClient(ServicoSegredo):

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @override
    def criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE:
        return self.__requester.put("/segredos", dados, SegredoComChave, typed(_UNLE).join(_UBE).join(_UNEE).join(_CNEE).end)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    @override
    def alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UBE | _UNEE | _CNEE | _SNEE:
        return self.__requester.put(
            f"/segredos/{dados.chave.valor}",
            dados.sem_chave,
            type(None),
            typed(_UNLE).join(_UBE).join(_UNEE).join(_CNEE).join(_SNEE).end
        )

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    @override
    def excluir_por_chave(self, dados: ChaveSegredo) -> None | _UNLE | _UBE | _SNEE:
        return self.__requester.delete(f"/segredos/{dados.valor}", type(None), typed(_UNLE).join(_UBE).join(_SNEE).end)

    @override
    def listar(self) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE:
        return self.__requester.get("/segredos", ResultadoPesquisaDeSegredos, typed(_UNLE).join(_UBE).end)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE:
        return self.__requester.get(f"/segredos/{chave.valor}", SegredoComChave, typed(_UNLE).join(_UBE).join(_SNEE).end)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        raise Exception("Não implementado")

    # Pode lançar SegredoNaoExisteException
    @override
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _SNEE:
        raise Exception("Não implementado")


# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoCategoriaClient(ServicoCategoria):

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE:
        return self.__requester.get(f"/categorias/{dados.nome}", CategoriaComChave, typed(_UNLE).join(_UBE).join(_CNEE).end)

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE:
        return self.__requester.get(f"/categorias/{chave.valor}", CategoriaComChave, typed(_UNLE).join(_UBE).join(_CNEE).end)

    # Pode lançar CategoriaJaExisteException
    @override
    def criar(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CJEE:
        return self.__requester.put(f"/categorias/{dados.nome}", {}, CategoriaComChave, typed(_UNLE).join(_UBE).join(_CJEE).end)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @override
    def renomear_por_nome(self, dados: RenomeCategoria) -> None | _UNLE | _UBE | _CJEE | _CNEE | _VIE:
        return self.__requester.move(
            f"/categorias/{dados.antigo}",
            dados.novo,
            False,
            type(None),
            typed(_UNLE).join(_UBE).join(_CJEE).join(_CNEE).join(_VIE).end
        )

    # Pode lançar CategoriaNaoExisteException
    @override
    def excluir_por_nome(self, dados: NomeCategoria) -> None | _UNLE | _UBE | _CNEE:
        return self.__requester.delete(f"/categorias/{dados.nome}", type(None), typed(_UNLE).join(_UBE).join(_CNEE).end)

    @override
    def listar(self) -> ResultadoListaDeCategorias | _UNLE | _UBE | _CJEE:
        return self.__requester.get("/categorias", ResultadoListaDeCategorias, typed(_UNLE).join(_UBE).join(_CJEE).end)
