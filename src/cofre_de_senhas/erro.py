from typing import override
from sucesso import Status


class SenhaErradaException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 401


class UsuarioNaoLogadoException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 401


class UsuarioBanidoException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 403


class PermissaoNegadaException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 403


class UsuarioJaExisteException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 409


class UsuarioNaoExisteException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 404


class CategoriaJaExisteException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 409


class CategoriaNaoExisteException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 404


class SegredoNaoExisteException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 404
