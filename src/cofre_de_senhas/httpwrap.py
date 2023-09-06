from typing import Any, Callable, TypeVar
from typing_extensions import Protocol, runtime_checkable
from dataclasses import dataclass
from validator import dataclass_validate
from flask import jsonify, request
from flask.wrappers import Response
from functools import wraps
from dacite import Config, from_dict
from enum import Enum

@runtime_checkable
class StatusProtocol(Protocol):
    @property
    def status(self) -> int:
        pass

@dataclass_validate
@dataclass(frozen = True)
class Erro:
    sucesso: bool # Sempre falso aqui. Mas o campo se faz presente ainda assim para ser serializado via JSON.
    mensagem: str
    tipo: str
    status: int

    @staticmethod
    def criar(e: BaseException) -> "Erro":
        return Erro(False, e.__str__(), e.__class__.__name__, e.status if isinstance(e, StatusProtocol) else 500)

@dataclass_validate
@dataclass(frozen = True)
class Ok:
    pass

@dataclass_validate
@dataclass(frozen = True)
class Sucesso:
    sucesso: bool # Sempre verdadeiro aqui. Mas o campo se faz presente ainda assim para ser serializado via JSON.
    conteudo: Any
    status: int

    @staticmethod
    def criar(conteudo: Any, status: int = 200) -> "Sucesso":
        return Sucesso(True, conteudo, status)

def handler(decorate: Callable[..., Response | tuple[Response, int]]) -> Callable[..., tuple[Response, int]]:
    @wraps(decorate)
    def decorator(*args: Any, **kwargs: Any) -> tuple[Response, int]:
        try:
            f: Response | tuple[Response, int] = decorate(*args, **kwargs)
            if isinstance(f, Response): return f, 200
            return f
        except BaseException as e:
            erro: Erro = Erro.criar(e)
            return jsonify(erro), erro.status
    return decorator

def jsoner(decorate: Callable[..., Any]) -> Callable[..., tuple[Response, int]]:
    @wraps(decorate)
    def decorator(*args: Any, **kwargs: Any) -> tuple[Response, int]:
        try:
            output: Any = decorate(*args, **kwargs)
            return jsonify(Sucesso.criar(output)), 200
        except BaseException as e:
            erro: Erro = Erro.criar(e)
            return jsonify(erro), erro.status
    return decorator

def empty_json(decorate: Callable[..., None]) -> Callable[..., tuple[Response, int]]:
    @wraps(decorate)
    def decorator(*args: Any, **kwargs: Any) -> tuple[Response, int]:
        try:
            decorate(*args, **kwargs)
            return jsonify(Sucesso.criar(Ok())), 200
        except BaseException as e:
            erro: Erro = Erro.criar(e)
            return jsonify(erro), erro.status
    return decorator

class RequisicaoMalFormadaException(Exception):
    @property
    def status(self) -> int:
        return 400

class PrecondicaoFalhouException(Exception):
    @property
    def status(self) -> int:
        return 412

class ConteudoNaoReconhecidoException(Exception):
    @property
    def status(self) -> int:
        return 415

class ConteudoIncompreensivelException(Exception):
    @property
    def status(self) -> int:
        return 422

_T = TypeVar("_T")
def read_body(target: type[_T], *, json: bool = True, urlencoded: bool = True, multipart: bool = True) -> _T:
    """
    Lê o corpo da requisição. O corpo é interpretado primeiramente como um dicionário. Em seguida, a partir desse dicionário (graças à função from_dict), uma instância de uma dataclass é criada.
    Caso a requisição não tiver um corpo ou tiver um que não possa ser compreendido, uma exceção que causará um erro 400 será lançada.

    Parameters:
        target (type[_T]): O tipo de objeto que deve ser lido a partir do corpo da requisição. Deve ser uma dataclass.
        json (bool): Indica se o corpo da requisição poderá ser aceito em formato JSON quando o cabeçalho Content-Type é do tipo "application/json". O padrão é True.
        urlencoded (bool): Indica se o corpo da requisição poderá ser aceito em formato urlencoded quando o cabeçalho Content-Type é do tipo "application/x-www-form-urlencoded". O padrão é True.
        multipart (bool): Indica se o corpo da requisição poderá ser aceito em formato urlencoded quando o cabeçalho Content-Type é do tipo "multipart/form-data". O padrão é True.

    Returns:
        _T: Uma instância dataclass do tipo especificado no parâmetro target a ser montada a partir do corpo da requisição.
    """

    content_type: str | None = request.headers.get("Content-Type")

    conteudo: Any
    if content_type is None:
        raise RequisicaoMalFormadaException()
    if content_type == "application/json" and json:
        try:
            conteudo = request.json
        except:
            raise RequisicaoMalFormadaException()
    elif (content_type == "application/x-www-form-urlencoded" and urlencoded) or (content_type == "multipart/form-data" and multipart):
        conteudo = request.form
    else:
        raise ConteudoNaoReconhecidoException()

    try:
        return from_dict(data_class = target, data = conteudo, config = Config(cast = [Enum]))
    except:
        raise ConteudoIncompreensivelException()

def bodyless() -> None:
    """
    Procedimento que garante que uma requisição não tenha corpo.
    Caso houver um corpo, uma exceção que causará um erro 400 será lançada.
    """
    content_type: str | None = request.headers.get("Content-Type")
    if content_type is not None: raise RequisicaoMalFormadaException()

def move() -> tuple[str, bool]:
    dest: str | None = request.headers.get("Destination")
    if dest is None: raise RequisicaoMalFormadaException()
    overwrite: str | None = request.headers.get("Overwrite")
    if overwrite not in [None, "F", "T"]: raise RequisicaoMalFormadaException()
    return (dest, overwrite != "F")