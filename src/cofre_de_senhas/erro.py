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


class LoginExpiradoException(Exception, Status):
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

    def __init__(self) -> None:
        self.__status: int = 409

    @property
    def precondicao_falhou(self) -> "UsuarioJaExisteException":
        x: UsuarioJaExisteException = UsuarioJaExisteException()
        x.__status = 412
        return x

    @override
    @property
    def status(self) -> int:
        return self.__status


class UsuarioNaoExisteException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 404


class CategoriaJaExisteException(Exception, Status):

    def __init__(self) -> None:
        self.__status: int = 409

    @property
    def precondicao_falhou(self) -> "CategoriaJaExisteException":
        x: CategoriaJaExisteException = CategoriaJaExisteException()
        x.__status = 412
        return x

    @override
    @property
    def status(self) -> int:
        return self.__status


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


class ValorIncorretoException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 422


class ExclusaoSemCascataException(Exception, Status):
    @override
    @property
    def status(self) -> int:
        return 409
