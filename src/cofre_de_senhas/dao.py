from typing import Generic
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, is_dataclass
from validator import dataclass_validate

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
class DadosUsuarioComPermissao:
    pk_usuario: int
    login: str
    fk_nivel_acesso: int
    hash_com_sal: str
    fk_tipo_permissao: int

    @property
    def sem_permissoes(self) -> DadosUsuario:
        return DadosUsuario(self.pk_usuario, self.login, self.fk_nivel_acesso, self.hash_com_sal)

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
class DadosSegredoSemPK:
    nome: str
    descricao: str
    fk_tipo_segredo: int

@dataclass_validate
@dataclass(frozen = True)
class DadosSegredo:
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
        pass

class SegredoDAO(ABC):

    # CRUD básico.

    @abstractmethod
    def buscar_por_pk(self, pk: SegredoPK) -> DadosSegredo | None:
        pass

    @abstractmethod
    def listar(self) -> list[DadosSegredo]:
        pass

    @abstractmethod
    def criar(self, dados: DadosSegredoSemPK) -> SegredoPK:
        pass

    @abstractmethod
    def salvar(self, dados: DadosSegredo) -> None:
        pass

    @abstractmethod
    def deletar_por_pk(self, pk: SegredoPK) -> None:
        pass

    # Métodos auxiliares.

    @abstractmethod
    def listar_visiveis(self, login: str) -> list[DadosSegredo]:
        pass

    @abstractmethod
    def limpar_segredo(self, pk: SegredoPK) -> None:
        pass

    # Categoria de segredo

    @abstractmethod
    def criar_categoria_segredo(self, spk: SegredoPK, cpk: CategoriaPK) -> int:
        pass

    # Campos

    @abstractmethod
    def criar_campo_segredo(self, pk: SegredoPK, descricao: str, valor: str) -> int:
        pass

    @abstractmethod
    def ler_campos_segredo(self, pk: SegredoPK) -> list[CampoDeSegredo]:
        pass

    # Permissões

    @abstractmethod
    def criar_permissao(self, upk: UsuarioPK, spk: SegredoPK, fk_tipo_permissao: int) -> int:
        pass

    @abstractmethod
    def buscar_permissao(self, pk: SegredoPK, login: str) -> int | None:
        pass

    @abstractmethod
    def ler_login_com_permissoes(self, pk: SegredoPK) -> list[LoginComPermissao]:
        pass

class CategoriaDAO:

    # CRUD básico

    @abstractmethod
    def buscar_por_pk(self, pk_categoria: CategoriaPK) -> DadosCategoria | None:
        pass

    @abstractmethod
    def listar(self) -> list[DadosCategoria]:
        pass

    @abstractmethod
    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        pass

    @abstractmethod
    def salvar(self, dados: DadosCategoria) -> None:
        pass

    @abstractmethod
    def deletar_por_pk(self, pk_categoria: CategoriaPK) -> None:
        pass

    # Métodos auxiliares

    @abstractmethod
    def buscar_por_nome(self, nome: str) -> DadosCategoria | None:
        pass

    #@abstractmethod
    #def deletar_por_nome(self, nome: str) -> None:
    #    pass

    # Métodos com joins em outras tabelas

    @abstractmethod
    def listar_por_segredo(self, pk_segredo: SegredoPK) -> list[DadosCategoria]:
        pass

class UsuarioDAO:

    # CRUD básico

    @abstractmethod
    def buscar_por_pk(self, pk_usuario: UsuarioPK) -> DadosUsuario | None:
        pass

    @abstractmethod
    def listar(self) -> list[DadosUsuario]:
        pass

    @abstractmethod
    def criar(self, dados: DadosUsuarioSemPK) -> UsuarioPK:
        pass

    @abstractmethod
    def salvar(self, dados: DadosUsuario) -> None:
        pass

    @abstractmethod
    def deletar_por_pk(self, pk_usuario: UsuarioPK) -> None:
        pass

    # Métodos auxiliares

    @abstractmethod
    def buscar_por_login(self, login: str) -> DadosUsuario | None:
        pass

    #@abstractmethod
    #def deletar_por_login(self, login: str) -> None:
    #    pass

    # Métodos com joins em outras tabelas

    @abstractmethod
    def listar_por_permissao(self, pk: SegredoPK) -> list[DadosUsuarioComPermissao]:
        pass