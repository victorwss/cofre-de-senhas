from typing import Generic
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, is_dataclass
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

@dataclass_validate
@dataclass(frozen = True)
class SegredoPK:
    pk_segredo: int

class SegredoDAO(ABC):

    @abstractmethod
    def buscar_pk_segredo(self, pk: int) -> int | None:
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
    def ler_cabecalho_segredo(self, pk_segredo: int) -> CabecalhoDeSegredo | None:
        ...

    @abstractmethod
    def ler_campos_segredo(self, pk_segredo: int) -> list[CampoDeSegredo]:
        ...

    @abstractmethod
    def ler_login_com_permissoes(self, pk_segredo: int) -> list[LoginComPermissao]:
        ...

@dataclass_validate
@dataclass(frozen = True)
class CategoriaPK:
    pk_categoria: int

@dataclass_validate
@dataclass(frozen = True)
class DadosCategoriaSemPK:
    nome: str

@dataclass_validate
@dataclass(frozen = True)
class DadosCategoria:
    pk_categoria: int
    nome: str

class CategoriaDAO:

    @abstractmethod
    def buscar_por_pk(self, pk_categoria: CategoriaPK) -> DadosCategoria | None:
        ...

    @abstractmethod
    def listar(self) -> list[DadosCategoria]:
        ...

    @abstractmethod
    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        ...

    @abstractmethod
    def salvar(self, dados: DadosCategoria) -> None:
        ...

    @abstractmethod
    def deletar_por_pk(self, pk_categoria: CategoriaPK) -> None:
        ...

    @abstractmethod
    def buscar_por_nome(self, nome: str) -> DadosCategoria | None:
        ...

    @abstractmethod
    def listar_por_segredo(self, pk_segredo: SegredoPK) -> list[DadosCategoria]:
        ...

    #@abstractmethod
    #def deletar_por_nome(self, nome: str) -> None:
    #    ...

@dataclass_validate
@dataclass(frozen = True)
class UsuarioPK:
    pk_usuario: int

@dataclass_validate
@dataclass(frozen = True)
class DadosUsuario:
    pk_usuario: int
    login: str
    fk_nivel_acesso: int
    hash_com_sal: str

@dataclass_validate
@dataclass(frozen = True)
class DadosUsuarioSemPK:
    login: str
    fk_nivel_acesso: int
    hash_com_sal: str

class UsuarioDAO:

    @abstractmethod
    def buscar_por_pk(self, pk_usuario: UsuarioPK) -> DadosUsuario | None:
        ...

    @abstractmethod
    def listar(self) -> list[DadosUsuario]:
        ...

    @abstractmethod
    def criar(self, dados: DadosUsuarioSemPK) -> UsuarioPK:
        ...

    @abstractmethod
    def salvar(self, dados: DadosUsuario) -> None:
        ...

    @abstractmethod
    def deletar_por_pk(self, pk_usuario: UsuarioPK) -> None:
        ...

    @abstractmethod
    def buscar_por_login(self, login: str) -> DadosUsuario | None:
        ...

    #@abstractmethod
    #def deletar_por_login(self, login: str) -> None:
    #    ...