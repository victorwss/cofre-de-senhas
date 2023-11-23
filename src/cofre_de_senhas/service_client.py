import requests
import hashlib
from typing import Any, override
from typing import TypeVar # Delete when PEP 695 is ready.
from dacite import Config, from_dict
from enum import Enum
from decorators.for_all import for_all_methods
from dataclasses import dataclass, replace, asdict
from requests.models import Response
from requests.cookies import RequestsCookieJar
from .service import *
from sucesso import *
from .erro import *

_X = TypeVar("_X") # Delete when PEP 695 is ready.

class _ErroDesconhecido(Exception):
    def __init__(self, dados: Any):
        super.__init__(dados)

class _Requester:

    def __init__(self) -> None:
        self.__base_url: str = "http://127.0.0.1:5000"
        self.__cookies: dict[str, str] = {}

    #def get[X](self, path: str, t: type[X]) -> X: # PEP 695
    def get(self, path: str, t: type[_X]) -> _X:
        r: Response = requests.get(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t)

    #def post[X](self, path: str, json: Any, t: type[X]) -> X: # PEP 695
    def post(self, path: str, json: Any, t: type[_X]) -> _X:
        r: Response = requests.post(self.__base_url + path, json = json, cookies = self.__cookies)
        return self.__unwrap(r, t)

    #def put[X](self, path: str, json: Any, t: type[X]) -> X: # PEP 695
    def put(self, path: str, json: Any, t: type[_X]) -> _X:
        r: Response = requests.put(self.__base_url + path, json = json, cookies = self.__cookies)
        return self.__unwrap(r, t)

    #def delete[X](self, path: str, t: type[X]) -> X: # PEP 695
    def delete(self, path: str, t: type[_X]) -> _X:
        r: Response = requests.delete(self.__base_url + path, cookies = self.__cookies)
        return self.__unwrap(r, t)

    #def move[X](self, path: str, to: str, overwrite: bool, t: type[X]) -> X: # PEP 695
    def move(self, path: str, to: str, overwrite: bool, t: type[_X]) -> _X:
        h: dict[str, str] = {
            "Destination": to,
            "Overwrite": "T" if overwrite else "F"
        }
        r: Response = requests.request("MOVE", self.__base_url + path, cookies = self.__cookies, headers = h)
        return self.__unwrap(r, t)

    #def __unwrap[X](self, r: Response, t: type[X]) -> X: # PEP 695
    def __unwrap(self, r: Response, t: type[_X]) -> _X:
        self.__cookies = dict(r.cookies)
        j: Any
        try:
            j = r.json()
        except BaseException:
            raise _ErroDesconhecido(r.text)
        if "sucesso" not in j:
            raise _ErroDesconhecido(r.text)
        if j["sucesso"]:
            return from_dict(data_class = t, data = j["conteudo"], config = Config(cast = [Enum]))
        if not j["interno"]:
            raise eval(j["tipo"])()
        raise _ErroDesconhecido(f"[{j["tipo"]}] {j["mensagem"]}")

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
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave:
        return self.__requester.post("/login", asdict(quem_faz), UsuarioComChave)

    @override
    def logout(self) -> None:
        self.__requester.post("/logout", {}, Ok)

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @override
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave:
        return self.__requester.put(f"/usuarios/{dados.login}", {"senha": dados.senha, "nivel_acesso": dados.nivel_acesso}, UsuarioComChave)

    @override
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None:
        self.__requester.post("/trocar-senha", dados, Ok)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada:
        return self.__requester.post(f"/usuarios/{dados.login}/resetar-senha", {}, SenhaAlterada)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None:
        self.__requester.post(f"/usuarios/{dados.login}/alterar-nivel", {"nivel_acesso": dados.nivel_acesso}, Ok)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave:
        return self.__requester.get(f"/usuarios/{dados.login}", UsuarioComChave)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave:
        return self.__requester.get(f"/usuarios/{chave.valor}", UsuarioComChave)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def listar(self) -> ResultadoListaDeUsuarios:
        return self.__requester.get(f"/usuarios", ResultadoListaDeUsuarios)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoSegredoClient(ServicoSegredo):

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @override
    def criar(self, dados: SegredoSemChave) -> SegredoComChave:
        return self.__requester.put(f"/segredos", dados, SegredoComChave)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    @override
    def alterar_por_chave(self, dados: SegredoComChave) -> None:
        self.__requester.put(f"/segredos/{dados.chave.valor}", dados.sem_chave, Ok)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    @override
    def excluir_por_chave(self, dados: ChaveSegredo) -> None:
        self.__requester.delete(f"/segredos/{dados.valor}", Ok)

    @override
    def listar(self) -> ResultadoPesquisaDeSegredos:
        return self.__requester.get(f"/segredos", ResultadoPesquisaDeSegredos)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave:
        return self.__requester.get(f"/segredos/{chave.valor}", SegredoComChave)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave:
        raise Exception("Não implementado")

    # Pode lançar SegredoNaoExisteException
    @override
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        raise Exception("Não implementado")

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoCategoriaClient(ServicoCategoria):

    def __init__(self, requester: _Requester) -> None:
        self.__requester: _Requester = requester

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave:
        return self.__requester.get(f"/categorias/{dados.nome}", CategoriaComChave)

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave:
        return self.__requester.get(f"/categorias/{chave.valor}", CategoriaComChave)

    # Pode lançar CategoriaJaExisteException
    @override
    def criar(self, dados: NomeCategoria) -> CategoriaComChave:
        return self.__requester.put(f"/categorias/{dados.nome}", {}, CategoriaComChave)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @override
    def renomear_por_nome(self, dados: RenomeCategoria) -> None:
        self.__requester.move(f"/categorias/{dados.antigo}", dados.novo, False, Ok)

    # Pode lançar CategoriaNaoExisteException
    @override
    def excluir_por_nome(self, dados: NomeCategoria) -> None:
        self.__requester.delete(f"/categorias/{dados.nome}", Ok)

    @override
    def listar(self) -> ResultadoListaDeCategorias:
        return self.__requester.get(f"/categorias", ResultadoListaDeCategorias)