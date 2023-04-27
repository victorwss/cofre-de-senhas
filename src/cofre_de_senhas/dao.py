from typing import Generic
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, is_dataclass
from validator import dataclass_validate
from cofre_de_senhas.cofre_enum import TipoSegredo, NivelAcesso, TipoPermissao

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

@dataclass_validate
@dataclass(frozen = True)
class SegredoPK:
    pk_segredo: int

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
    pk_chave: str
    valor: str

@dataclass_validate
@dataclass(frozen = True)
class LoginComPermissao:
    login: str
    permissao: int

class CofreDeSenhasDAO(ABC):

    @abstractmethod
    def criar_bd(self) -> None:
        ...

class SegredoDAO(ABC):

    @abstractmethod
    def buscar_pk_segredo(self, pk: SegredoPK) -> SegredoPK | None:
        ...

    @abstractmethod
    def limpar_segredo(self, pk: SegredoPK) -> None:
        ...

    @abstractmethod
    def criar_campo_segredo(self, pk: SegredoPK, descricao: str, valor: str) -> int:
        ...

    @abstractmethod
    def criar_permissao(self, upk: UsuarioPK, spk: SegredoPK, tipo_permissao: TipoPermissao) -> int:
        ...

    @abstractmethod
    def criar_categoria_segredo(self, spk: SegredoPK, cpk: CategoriaPK) -> int:
        ...

    @abstractmethod
    def criar_segredo(self, nome: str, descricao: str, tipo_segredo: TipoSegredo) -> SegredoPK:
        ...

    @abstractmethod
    def alterar_segredo(self, pk: SegredoPK, nome: str, descricao: str, tipo_segredo: TipoSegredo) -> None:
        ...

    @abstractmethod
    def listar_todos_segredos(self) -> list[CabecalhoDeSegredo]:
        ...

    @abstractmethod
    def listar_segredos_visiveis(self, login: str) -> list[CabecalhoDeSegredo]:
        ...

    @abstractmethod
    def buscar_permissao(self, pk: SegredoPK, login: str) -> int | None:
        ...

    @abstractmethod
    def deletar_segredo(self, pk: SegredoPK) -> None:
        ...

    @abstractmethod
    def ler_cabecalho_segredo(self, pk: SegredoPK) -> CabecalhoDeSegredo | None:
        ...

    @abstractmethod
    def ler_campos_segredo(self, pk: SegredoPK) -> list[CampoDeSegredo]:
        ...

    @abstractmethod
    def ler_login_com_permissoes(self, pk: SegredoPK) -> list[LoginComPermissao]:
        ...

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