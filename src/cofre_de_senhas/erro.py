from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate

class Status(ABC):

    @property
    @abstractmethod
    def status(self) -> int:
        pass

class SenhaErradaException(Exception, Status):
    @property
    def status(self) -> int:
        return 401

class UsuarioNaoLogadoException(Exception, Status):
    @property
    def status(self) -> int:
        return 401

class UsuarioBanidoException(Exception, Status):
    @property
    def status(self) -> int:
        return 403

class PermissaoNegadaException(Exception, Status):
    @property
    def status(self) -> int:
        return 403

class UsuarioJaExisteException(Exception, Status):
    @property
    def status(self) -> int:
        return 409

class UsuarioNaoExisteException(Exception, Status):
    @property
    def status(self) -> int:
        return 404

class CategoriaJaExisteException(Exception, Status):
    @property
    def status(self) -> int:
        return 409

class CategoriaNaoExisteException(Exception, Status):
    @property
    def status(self) -> int:
        return 404

class SegredoNaoExisteException(Exception, Status):
    @property
    def status(self) -> int:
        return 404

@dataclass_validate
@dataclass(frozen = True)
class Erro:
    mensagem: str
    tipo: str
    status: int

    @staticmethod
    def criar(e: BaseException) -> "Erro":
        return Erro(e.__str__(), e.__class__.__name__, e.status if isinstance(e, Status) else 500)