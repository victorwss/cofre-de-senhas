from typing import Any, Callable
from typing import TypeVar # Delete when PEP 695 is ready.
from flask import jsonify, request
from flask.wrappers import Response
from functools import wraps
from dacite import Config, from_dict
from enum import Enum
from.sucesso import *

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
            return jsonify(Sucesso.ok()), 200
        except BaseException as e:
            erro: Erro = Erro.criar(e)
            return jsonify(erro), erro.status
    return decorator

def _is_form(content_type: str, urlencoded: bool, multipart: bool) -> bool:
    return (content_type == "application/x-www-form-urlencoded" and urlencoded) or (content_type == "multipart/form-data" and multipart)

def _is_json(content_type: str, json: bool) -> bool:
    return content_type == "application/json" and json

def _get_body(content_type: str | None, json: bool, urlencoded: bool, multipart: bool) -> Any:
    if content_type is None:
        raise RequisicaoMalFormadaException()

    if _is_form(content_type, urlencoded, multipart):
        return request.form

    if _is_json(content_type, json):
        try:
            return request.json
        except:
            raise RequisicaoMalFormadaException()

    raise ConteudoNaoReconhecidoException()

_T = TypeVar("_T") # Delete when PEP 695 is ready.

#def read_body[T](target: type[T], *, json: bool = True, urlencoded: bool = True, multipart: bool = True) -> T: # PEP 695
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

    body: Any = _get_body(content_type, json, urlencoded, multipart)

    try:
        return from_dict(data_class = target, data = body, config = Config(cast = [Enum]))
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