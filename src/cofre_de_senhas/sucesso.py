from typing import Any, Literal
from typing_extensions import Protocol, runtime_checkable
from dataclasses import dataclass
from validator import dataclass_validate

@runtime_checkable
class Status(Protocol):
    @property
    def status(self) -> int:
        pass

@dataclass_validate
@dataclass(frozen = True)
class Erro:
    sucesso: Literal[False] # Sempre falso aqui. Mas o campo se faz presente ainda assim para ser serializado via JSON.
    interno: bool
    mensagem: str
    tipo: str
    status: int

    @staticmethod
    def criar(e: BaseException) -> "Erro":
        return Erro(False, isinstance(e, Status), e.__str__(), e.__class__.__name__, e.status if isinstance(e, Status) else 500)

@dataclass_validate
@dataclass(frozen = True)
class Ok:
    pass

@dataclass_validate
@dataclass(frozen = True)
class Sucesso:
    sucesso: Literal[True] # Sempre verdadeiro aqui. Mas o campo se faz presente ainda assim para ser serializado via JSON.
    conteudo: Any
    status: int

    @staticmethod
    def criar(conteudo: Any, status: int = 200) -> "Sucesso":
        return Sucesso(True, conteudo, status)

class RequisicaoMalFormadaException(Exception, Status):
    @property
    def status(self) -> int:
        return 400

class PrecondicaoFalhouException(Exception, Status):
    @property
    def status(self) -> int:
        return 412

class ConteudoNaoReconhecidoException(Exception, Status):
    @property
    def status(self) -> int:
        return 415

class ConteudoIncompreensivelException(Exception, Status):
    @property
    def status(self) -> int:
        return 422