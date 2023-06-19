from abc import ABC, abstractmethod

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