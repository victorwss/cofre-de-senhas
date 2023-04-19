from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate

@dataclass_validate
@dataclass(frozen = True)
class CabecalhoDeSegredo:
    pk_segredo: int
    nome: str
    descricao: str
    fk_tipo_segredo: int

@dataclass_validate
@dataclass(frozen = True)
class CampoDeSegredo:
    chave: str
    valor: str

@dataclass_validate
@dataclass(frozen = True)
class NomeDeCategoria:
    nome: str

@dataclass_validate
@dataclass(frozen = True)
class LoginComPermissao:
    login: str
    permissao: int

@dataclass_validate
@dataclass(frozen = True)
class DadosLogin:
    fk_nivel_acesso: int
    hash_com_sal: str

@dataclass_validate
@dataclass(frozen = True)
class DadosNivel:
    login: str
    fk_nivel_acesso: int

class CofreDeSenhasDAO(ABC):

    @abstractmethod
    def criar_bd(self) -> None:
        ...

    @abstractmethod
    def buscar_pk_usuario_por_login(self, login: str) -> int | None:
        ...

    @abstractmethod
    def buscar_pk_segredo(self, pk: int) -> int | None:
        ...

    @abstractmethod
    def buscar_pk_categoria_por_nome(self, nome: str) -> int | None:
        ...

    @abstractmethod
    def login(self, login: str) -> DadosLogin | None:
        ...

    @abstractmethod
    def criar_usuario(self, login: str, nivel_acesso: int, hash_com_sal: str) -> None:
        ...

    @abstractmethod
    def trocar_senha(self, login: str, hash_com_sal: str) -> None:
        ...

    @abstractmethod
    def alterar_nivel_de_acesso(self, login: str, nivel_acesso: int) -> None:
        ...

    @abstractmethod
    def listar_usuarios(self) -> list[DadosNivel]:
        ...

    @abstractmethod
    def limpar_segredo(self, segredo: int) -> None:
        ...

    @abstractmethod
    def criar_campo_segredo(self, segredo: int, descricao: str, valor: str) -> int:
        ...

    @abstractmethod
    def criar_permissao(self, usuario: int, segredo: int, tipo_permissao: int) -> int:
        ...

    @abstractmethod
    def criar_categoria_segredo(self, segredo: int, categoria: int) -> int:
        ...

    @abstractmethod
    def criar_segredo(self, nome: str, descricao: str, tipo_segredo: int) -> int:
        ...

    @abstractmethod
    def alterar_segredo(self, segredo: int, nome: str, descricao: str, tipo_segredo: int) -> None:
        ...

    @abstractmethod
    def listar_todos_segredos(self) -> list[CabecalhoDeSegredo]:
        ...

    @abstractmethod
    def listar_segredos_visiveis(self, login: str) -> list[CabecalhoDeSegredo]:
        ...

    @abstractmethod
    def buscar_permissao(self, segredo: int, login: str) -> int | None:
        ...

    @abstractmethod
    def deletar_segredo(self, segredo: int) -> None:
        ...

    @abstractmethod
    def criar_categoria(self, nome: str) -> int:
        ...

    @abstractmethod
    def renomear_categoria(self, antigo: str, novo: str) -> None:
        ...

    @abstractmethod
    def deletar_categoria(self, nome: str) -> None:
        ...

    @abstractmethod
    def ler_cabecalho_segredo(self, pk_segredo: int) -> CabecalhoDeSegredo | None:
        ...

    @abstractmethod
    def ler_campos_segredo(self, pk_segredo: int) -> list[CampoDeSegredo]:
        ...

    @abstractmethod
    def ler_nomes_categorias(self, pk_segredo: int) -> list[NomeDeCategoria]:
        ...

    @abstractmethod
    def ler_login_com_permissoes(self, pk_segredo: int) -> list[LoginComPermissao]:
        ...