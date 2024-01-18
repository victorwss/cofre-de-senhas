from typing import TypeAlias
from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from enum import Enum
from .erro import (
    UsuarioNaoLogadoException, UsuarioBanidoException, PermissaoNegadaException, SenhaErradaException, LoginExpiradoException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    SegredoNaoExisteException,
    ValorIncorretoException, ExclusaoSemCascataException
)


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


_UNLE: TypeAlias = UsuarioNaoLogadoException
_UBE: TypeAlias = UsuarioBanidoException
_PNE: TypeAlias = PermissaoNegadaException
_UNEE: TypeAlias = UsuarioNaoExisteException
_UJEE: TypeAlias = UsuarioJaExisteException
_CNEE: TypeAlias = CategoriaNaoExisteException
_CJEE: TypeAlias = CategoriaJaExisteException
_SNEE: TypeAlias = SegredoNaoExisteException
_SEE: TypeAlias = SenhaErradaException
_VIE: TypeAlias = ValorIncorretoException
_LEE: TypeAlias = LoginExpiradoException
_ESCE: TypeAlias = ExclusaoSemCascataException


class GerenciadorLogin(ABC):

    @abstractmethod
    def login(self, chave: UsuarioComChave) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    @property
    @abstractmethod
    def usuario_logado(self) -> ChaveUsuario | _UNLE:
        pass


class ServicoBD(ABC):

    @abstractmethod
    def criar_bd(self, dados: LoginComSenha) -> None:
        pass


class ServicoUsuario(ABC):

    @abstractmethod
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE | _LEE:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    @abstractmethod
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave | _UNLE | _UBE | _PNE | _UJEE | _LEE:
        pass

    @abstractmethod
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None | _UNLE | _UBE | _SEE | _LEE:
        pass

    @abstractmethod
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        pass

    @abstractmethod
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None | _UNLE | _UBE | _PNE | _UNEE | _LEE:
        pass

    @abstractmethod
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        pass

    @abstractmethod
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:
        pass

    @abstractmethod
    def listar(self) -> ResultadoListaDeUsuarios | _UNLE | _UBE | _LEE:
        pass


class ServicoSegredo(ABC):

    @abstractmethod
    def criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE | _PNE | _LEE:
        pass

    @abstractmethod
    def alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE:
        pass

    @abstractmethod
    def excluir_por_chave(self, dados: ChaveSegredo) -> None | _UNLE | _UBE | _SNEE | _PNE | _LEE:
        pass

    @abstractmethod
    def listar(self) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _LEE:
        pass

    @abstractmethod
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE | _LEE:
        pass

    @abstractmethod
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        pass

    @abstractmethod
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _SNEE | _LEE:
        pass


class ServicoCategoria(ABC):

    @abstractmethod
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        pass

    @abstractmethod
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE:
        pass

    @abstractmethod
    def criar(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _LEE | _UBE | _PNE | _CJEE | _VIE:
        pass

    @abstractmethod
    def renomear_por_nome(self, dados: RenomeCategoria) -> None | _UNLE | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE:
        pass

    @abstractmethod
    def excluir_por_nome(self, dados: NomeCategoria) -> None | _UNLE | _UBE | _PNE | _CNEE | _LEE | _ESCE:
        pass

    @abstractmethod
    def listar(self) -> ResultadoListaDeCategorias | _UNLE | _UBE | _LEE:
        pass
