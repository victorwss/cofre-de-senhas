from dataclasses import dataclass
from validator import dataclass_validate

class SenhaErradaException(Exception):
    pass

class UsuarioNaoLogadoException(Exception):
    pass

class UsuarioBanidoException(Exception):
    pass

class PermissaoNegadaException(Exception):
    pass

class UsuarioJaExisteException(Exception):
    pass

class UsuarioNaoExisteException(Exception):
    pass

class CategoriaJaExisteException(Exception):
    pass

class CategoriaNaoExisteException(Exception):
    pass

class SegredoNaoExisteException(Exception):
    pass

@dataclass_validate
@dataclass(frozen = True)
class Erro:
    mensagem: str
    tipo: str
    status: int