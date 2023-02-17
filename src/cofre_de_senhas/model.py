# Cofre de senhas

from enum import Enum
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate  # pip install dataclass_type_validator
from dataclass_type_validator import TypeValidationError

class NivelAcesso(Enum):
    BANIDO = 0,
    NORMAL = 1,
    CHAVEIRO_DEUS_SUPREMO = 2

    @staticmethod
    def por_codigo(codigo: int) -> NivelAcesso:
        for n in NivelAcesso:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em NivelAcesso.")

class TipoPermissao(Enum):
    SOMENTE_LEITURA = 1,
    LEITURA_E_ESCRITA = 2,
    PROPRIETARIO = 3

    @staticmethod
    def por_codigo(codigo: int) -> TipoPermissao:
        for n in TipoPermissao:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em TipoPermissao.")

class TipoSegredo(Enum):
    PUBLICO = 1,
    ENCONTRAVEL = 2,
    CONFIDENCIAL = 3

    @staticmethod
    def por_codigo(codigo: int) -> TipoSegredo:
        for n in TipoSegredo:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em TipoSegredo.")

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
class DadosLogin:
    fk_nivel_acesso: NivelAcesso
    hash_com_sal: str

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class UsuarioNovo:
    login: str
    nivel_acesso: NivelAcesso
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
    usuarios: dict[str, TipoPermissao]

@dataclass_validate(strict = True)
@dataclass(frozen = True)
class SegredoComPK:
    pk: SegredoPK
    nome: str
    descricao: str
    tipo: TipoSegredo
    campos: dict[str, str]
    categorias: list[str]
    usuarios: dict[str, TipoPermissao]

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

    @abstractmethod
    def login(self, quem_faz: LoginUsuario) -> NivelAcesso:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @abstractmethod
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioNovo) -> None:
        pass

    @abstractmethod
    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        pass

    @abstractmethod
    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoUsuario:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @abstractmethod
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    @abstractmethod
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        pass

    @abstractmethod
    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisa:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisa:
        pass

    # Pode lançar CategoriaJaExisteException
    @abstractmethod
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @abstractmethod
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass