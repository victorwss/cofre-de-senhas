from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from connection.trans import TransactedConnection
from threadlocal import ThreadLocal


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
class LoginUsuario:
    valor: str

    @staticmethod
    def para_todos(logins: set[str]) -> list["LoginUsuario"]:
        return [LoginUsuario(v) for v in logins]


@dataclass_validate
@dataclass(frozen = True)
class NomeCategoria:
    valor: str

    @staticmethod
    def para_todos(nomes: set[str]) -> list["NomeCategoria"]:
        return [NomeCategoria(v) for v in nomes]


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


class CofreDeSenhasDAO(DAO):

    __instance: ThreadLocal["CofreDeSenhasDAO | None"] = ThreadLocal(None)

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)
        CofreDeSenhasDAO.__instance.value = self

    @abstractmethod
    def criar_bd(self) -> None:
        pass

    @staticmethod
    def instance() -> "CofreDeSenhasDAO":
        u: CofreDeSenhasDAO | None = CofreDeSenhasDAO.__instance.value
        if u is None:
            raise BaseException()
        return u


class SegredoDAO(DAO):

    __instance: ThreadLocal["SegredoDAO | None"] = ThreadLocal(None)

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)
        SegredoDAO.__instance.value = self

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
    def listar_visiveis(self, login: LoginUsuario) -> list[DadosSegredo]:
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

    @staticmethod
    def instance() -> "SegredoDAO":
        u: SegredoDAO | None = SegredoDAO.__instance.value
        if u is None:
            raise BaseException()
        return u


class CategoriaDAO(DAO):

    __instance: ThreadLocal["CategoriaDAO | None"] = ThreadLocal(None)

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)
        CategoriaDAO.__instance.value = self

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
    def listar_por_nomes(self, nomes: list[NomeCategoria]) -> list[DadosCategoria]:
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
    def buscar_por_nome(self, nome: NomeCategoria) -> DadosCategoria | None:
        pass

    # @abstractmethod
    # def deletar_por_nome(self, nome: NomeCategoria) -> None:
    #     pass

    # Métodos com joins em outras tabelas

    @abstractmethod
    def listar_por_segredo(self, pk_segredo: SegredoPK) -> list[DadosCategoria]:
        pass

    @staticmethod
    def instance() -> "CategoriaDAO":
        u: CategoriaDAO | None = CategoriaDAO.__instance.value
        if u is None:
            raise BaseException()
        return u


class UsuarioDAO(DAO):

    __instance: ThreadLocal["UsuarioDAO | None"] = ThreadLocal(None)

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)
        UsuarioDAO.__instance.value = self

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
    def listar_por_logins(self, logins: list[LoginUsuario]) -> list[DadosUsuario]:
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
    def buscar_por_login(self, login: LoginUsuario) -> DadosUsuario | None:
        pass

    # @abstractmethod
    # def deletar_por_login(self, login: LoginUsuario) -> None:
    #     pass

    # Métodos com joins em outras tabelas

    @abstractmethod
    def listar_por_permissao(self, pk: SegredoPK) -> list[DadosUsuarioComPermissao]:
        pass

    @staticmethod
    def instance() -> "UsuarioDAO":
        u: UsuarioDAO | None = UsuarioDAO.__instance.value
        if u is None:
            raise BaseException()
        return u
