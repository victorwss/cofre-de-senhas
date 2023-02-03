# Cofre de senhas

from enum import Enum
from abc import ABC
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate
from dataclass_type_validator import TypeValidationError

# pip install dataclass_type_validator

class NivelAcesso(Enum):
    BANIDO = 0,
    NORMAL = 1,
    CHAVEIRO_DEUS_SUPREMO = 2

class TipoPermissao(Enum):
    SOMENTE_LEITURA = 1,
    LEITURA_E_ESCRITA = 2,
    PROPRIETARIO = 3

class TipoSegredo(Enum):
    PUBLICO = 1,
    ENCONTRAVEL = 2,
    CONFIDENCIAL = 3

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class SegredoPK:
    valor: int

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class CampoSegredoPK:
    valor: int

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class UsuarioPK:
    valor: int

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class LoginUsuario:
    login: str
    senha: str

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class UsuarioComNivel:
    login: str
    nivel_acesso: NivelAcesso

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class NovaSenha:
    senha: str

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class ResetLoginUsuario:
    login: str

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class SegredoSemPK:
    nome: str
    descricao: str
    tipo: TipoSegredo
    campos: dict[str, str]
    categorias: list[str]
    usuarios: list[str]

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class SegredoComPK:
    pk: SegredoPK
    nome: str
    descricao: str
    tipo: TipoSegredo
    campos: dict[str, str]
    categorias: list[str]
    usuarios: list[str]

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class PesquisaSegredos:
    nome: str
    categorias: list[str]

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class NomeCategoria:
    nome: str

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class RenomeCategoria:
    antigo: str
    novo: str

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class ResultadoPesquisa:
    segredos: list[SegredoComPK]

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class ResultadoUsuario:
    segredos: list[UsuarioComNivel]

class SenhaErradaException(Exception):
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

# Todos os métodos podem lançar SenhaErradaException ou UsuarioBanidoException.

class CofreDeSenhas(ABC):

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        pass

    def login(self, quem_faz: LoginUsuario) -> None:
        pass

    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoUsuario:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        pass

    # Pode lançar SegredoNaoExisteException
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        pass

    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisa:
        pass

    # Pode lançar CategoriaNaoExisteException
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisa:
        pass

    # Pode lançar CategoriaJaExisteException
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        pass

    # Pode lançar CategoriaNaoExisteException
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass