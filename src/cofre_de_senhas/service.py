from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from .erro import *
from enum import Enum

class NivelAcesso(Enum):
    DESATIVADO = 0
    NORMAL = 1
    CHAVEIRO_DEUS_SUPREMO = 2

class TipoPermissao(Enum):
    SOMENTE_LEITURA = 1
    LEITURA_E_ESCRITA = 2
    PROPRIETARIO = 3

class TipoSegredo(Enum):
    PUBLICO = 1
    ENCONTRAVEL = 2
    CONFIDENCIAL = 3

@dataclass_validate
@dataclass(frozen = True)
class ChaveUsuario:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class ResetLoginUsuario:
    login: str

@dataclass_validate
@dataclass(frozen = True)
class ChaveSegredo:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class SegredoSemChave:
    nome: str
    descricao: str
    tipo: TipoSegredo
    campos: dict[str, str]
    categorias: set[str]
    usuarios: dict[str, TipoPermissao]

    def com_chave(self, chave: ChaveSegredo) -> "SegredoComChave":
        return SegredoComChave(chave, self.nome, self.descricao, self.tipo, self.campos, self.categorias, self.usuarios)

@dataclass_validate
@dataclass(frozen = True)
class SegredoComChave:
    chave: ChaveSegredo
    nome: str
    descricao: str
    tipo: TipoSegredo
    campos: dict[str, str]
    categorias: set[str]
    usuarios: dict[str, TipoPermissao]

    @property
    def sem_chave(self) -> "SegredoSemChave":
        return SegredoSemChave(self.nome, self.descricao, self.tipo, self.campos, self.categorias, self.usuarios)

@dataclass_validate
@dataclass(frozen = True)
class NomeCategoria:
    nome: str

@dataclass_validate
@dataclass(frozen = True)
class RenomeCategoria:
    antigo: str
    novo: str

@dataclass_validate
@dataclass(frozen = True)
class LoginComSenha:
    login: str
    senha: str

    def com_nivel(self, nivel_acesso: NivelAcesso) -> "UsuarioNovo":
        return UsuarioNovo(self.login, nivel_acesso, self.senha)

@dataclass_validate
@dataclass(frozen = True)
class LoginUsuario:
    login: str

@dataclass_validate
@dataclass(frozen = True)
class UsuarioNovo:
    login: str
    nivel_acesso: NivelAcesso
    senha: str

@dataclass_validate
@dataclass(frozen = True)
class TrocaSenha:
    antiga: str
    nova: str

@dataclass_validate
@dataclass(frozen = True)
class SenhaAlterada:
    chave: ChaveUsuario
    login: str
    nova_senha: str

@dataclass_validate
@dataclass(frozen = True)
class UsuarioComNivel:
    login: str
    nivel_acesso: NivelAcesso

@dataclass_validate
@dataclass(frozen = True)
class UsuarioComChave:
    chave: ChaveUsuario
    login: str
    nivel_acesso: NivelAcesso

@dataclass_validate
@dataclass(frozen = True)
class ChaveCategoria:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class CabecalhoSegredoComChave:
    chave: ChaveSegredo
    nome: str
    descricao: str
    tipo: TipoSegredo

    def com_corpo(self, campos: dict[str, str], categorias: set[str], usuarios: dict[str, TipoPermissao]) -> SegredoComChave:
        return SegredoComChave(self.chave, self.nome, self.descricao, self.tipo, campos, categorias, usuarios)

@dataclass_validate
@dataclass(frozen = True)
class ResultadoPesquisaDeSegredos:
    segredos: list[CabecalhoSegredoComChave]

@dataclass_validate
@dataclass(frozen = True)
class CategoriaComChave:
    chave: ChaveCategoria
    nome: str

@dataclass_validate
@dataclass(frozen = True)
class ResultadoListaDeCategorias:
    lista: list[CategoriaComChave]

@dataclass_validate
@dataclass(frozen = True)
class ResultadoListaDeUsuarios:
    lista: list[UsuarioComChave]

@dataclass_validate
@dataclass(frozen = True)
class PesquisaSegredos:
    nome: str
    categorias: list[str]

class GerenciadorLogin(ABC):

    # Pode lançar SenhaErradaException
    @abstractmethod
    def login(self, chave: UsuarioComChave) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    # Pode lançar UsuarioNaoLogadoException.
    @property
    @abstractmethod
    def usuario_logado(self) -> ChaveUsuario:
        pass

class ServicoBD(ABC):

    @abstractmethod
    def criar_bd(self, dados: LoginComSenha) -> None:
        pass

# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class ServicoUsuario(ABC):

    # Pode lançar SenhaErradaException
    @abstractmethod
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @abstractmethod
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave:
        pass

    @abstractmethod
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None:
        pass

    @abstractmethod
    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None:
        pass

    # Pode lançar UsuarioNaoExisteException
    @abstractmethod
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave:
        pass

    # Pode lançar UsuarioNaoExisteException
    @abstractmethod
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def listar(self) -> ResultadoListaDeUsuarios:
        pass

class ServicoSegredo(ABC):

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @abstractmethod
    def criar(self, dados: SegredoSemChave) -> SegredoComChave:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    @abstractmethod
    def alterar_por_chave(self, dados: SegredoComChave) -> None:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def excluir_por_chave(self, dados: ChaveSegredo) -> None:
        pass

    @abstractmethod
    def listar(self) -> ResultadoPesquisaDeSegredos:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        pass

class ServicoCategoria(ABC):

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave:
        pass

    # Pode lançar CategoriaJaExisteException
    @abstractmethod
    def criar(self, dados: NomeCategoria) -> CategoriaComChave:
        pass

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @abstractmethod
    def renomear_por_nome(self, dados: RenomeCategoria) -> None:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def excluir_por_nome(self, dados: NomeCategoria) -> None:
        pass

    @abstractmethod
    def listar(self) -> ResultadoListaDeCategorias:
        pass