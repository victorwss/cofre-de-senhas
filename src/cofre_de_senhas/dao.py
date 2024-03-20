from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from connection.trans import TransactedConnection


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
    pfk_segredo: int
    pk_nome: str
    valor: str


@dataclass_validate
@dataclass(frozen = True)
class LoginUsuarioUK:
    valor: str

    @staticmethod
    def para_todos(logins: list[str]) -> list["LoginUsuarioUK"]:
        return [LoginUsuarioUK(v) for v in logins]


@dataclass_validate
@dataclass(frozen = True)
class NomeCategoriaUK:
    valor: str

    @staticmethod
    def para_todos(nomes: list[str]) -> list["NomeCategoriaUK"]:
        return [NomeCategoriaUK(v) for v in nomes]


@dataclass_validate
@dataclass(frozen = True)
class CategoriaDeSegredo:
    pk_segredo: int
    pk_categoria: int


@dataclass_validate
@dataclass(frozen = True)
class PermissaoDeSegredo:
    pfk_usuario: int
    pfk_segredo: int
    fk_tipo_permissao: int


@dataclass_validate
@dataclass(frozen = True)
class BuscaPermissaoPorLogin:
    pfk_segredo: int
    login: str


class DAO(ABC):

    def __init__(self, con: TransactedConnection) -> None:
        self.__con: TransactedConnection = con

    @property
    def _connection(self) -> TransactedConnection:
        return self.__con

    @property
    def _placeholder(self) -> str:
        return self.__con.placeholder

    @property
    def _database_type(self) -> str:
        return self.__con.database_type

    def _executar_sql(self, sql: str) -> None:
        if self._database_type == "MariaDB":
            for part in sql.split(";"):
                if part.strip() != "":
                    self._connection.execute(part)
        else:
            self._connection.executescript(sql)


class CofreDeSenhasDAO(DAO):

    @abstractmethod
    def criar_bd(self) -> None:
        pass


class SegredoDAO(DAO):

    # CRUD básico.

    @abstractmethod
    def buscar_por_pk(self, pk: SegredoPK) -> DadosSegredo | None:
        pass

    @abstractmethod
    def listar_por_pks(self, pks: list[SegredoPK]) -> list[DadosSegredo]:
        pass

    @abstractmethod
    def listar(self) -> list[DadosSegredo]:
        pass

    @abstractmethod
    def criar(self, dados: DadosSegredoSemPK) -> SegredoPK:
        pass

    @abstractmethod
    def salvar_com_pk(self, dados: DadosSegredo) -> bool:
        pass

    @abstractmethod
    def deletar_por_pk(self, pk: SegredoPK) -> bool:
        pass

    # Métodos auxiliares.

    @abstractmethod
    def listar_visiveis(self, login: LoginUsuarioUK) -> list[DadosSegredo]:
        pass

    @abstractmethod
    def limpar_segredo(self, pk: SegredoPK) -> None:
        pass

    # Categoria de segredo

    @abstractmethod
    def criar_categoria_segredo(self, c: CategoriaDeSegredo) -> bool:
        pass

    # Campos

    @abstractmethod
    def criar_campo_segredo(self, campo: CampoDeSegredo) -> bool:
        pass

    @abstractmethod
    def ler_campos_segredo(self, pk: SegredoPK) -> list[CampoDeSegredo]:
        pass

    # Permissões

    @abstractmethod
    def criar_permissao(self, permissao: PermissaoDeSegredo) -> bool:
        pass

    @abstractmethod
    def buscar_permissao(self, busca: BuscaPermissaoPorLogin) -> PermissaoDeSegredo | None:
        pass


class CategoriaDAO(DAO):

    # CRUD básico

    @abstractmethod
    def buscar_por_pk(self, pk_categoria: CategoriaPK) -> DadosCategoria | None:
        pass

    @abstractmethod
    def listar_por_pks(self, pks: list[CategoriaPK]) -> list[DadosCategoria]:
        pass

    @abstractmethod
    def listar(self) -> list[DadosCategoria]:
        pass

    @abstractmethod
    def listar_por_nomes(self, nomes: list[NomeCategoriaUK]) -> list[DadosCategoria]:
        pass

    @abstractmethod
    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        pass

    @abstractmethod
    def salvar_com_pk(self, dados: DadosCategoria) -> bool:
        pass

    @abstractmethod
    def deletar_por_pk(self, pk_categoria: CategoriaPK) -> bool:
        pass

    # Métodos auxiliares

    @abstractmethod
    def buscar_por_nome(self, nome: NomeCategoriaUK) -> DadosCategoria | None:
        pass

    # @abstractmethod
    # def deletar_por_nome(self, nome: NomeCategoriaUK) -> None:
    #     pass

    # Métodos com joins em outras tabelas

    @abstractmethod
    def listar_por_segredo(self, pk_segredo: SegredoPK) -> list[DadosCategoria]:
        pass

    @abstractmethod
    def contar_segredos_por_pk(self, dados: CategoriaPK) -> int:
        pass


class UsuarioDAO(DAO):

    # CRUD básico

    @abstractmethod
    def buscar_por_pk(self, pk_usuario: UsuarioPK) -> DadosUsuario | None:
        pass

    @abstractmethod
    def listar_por_pks(self, pks: list[UsuarioPK]) -> list[DadosUsuario]:
        pass

    @abstractmethod
    def listar(self) -> list[DadosUsuario]:
        pass

    @abstractmethod
    def listar_por_logins(self, logins: list[LoginUsuarioUK]) -> list[DadosUsuario]:
        pass

    @abstractmethod
    def criar(self, dados: DadosUsuarioSemPK) -> UsuarioPK:
        pass

    @abstractmethod
    def salvar_com_pk(self, dados: DadosUsuario) -> bool:
        pass

    @abstractmethod
    def deletar_por_pk(self, pk_usuario: UsuarioPK) -> bool:
        pass

    #  Métodos auxiliares

    @abstractmethod
    def buscar_por_login(self, login: LoginUsuarioUK) -> DadosUsuario | None:
        pass

    # @abstractmethod
    # def deletar_por_login(self, login: LoginUsuarioUK) -> None:
    #     pass

    # Métodos com joins em outras tabelas

    @abstractmethod
    def listar_por_permissao(self, pk: SegredoPK) -> list[DadosUsuarioComPermissao]:
        pass
