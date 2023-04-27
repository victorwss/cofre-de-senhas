from typing import TypeVar
from connection.conn import TransactedConnection
from cofre_de_senhas.dao import SegredoDAO, SegredoPK, UsuarioPK, CategoriaPK, CabecalhoDeSegredo, CampoDeSegredo, LoginComPermissao
from cofre_de_senhas.cofre_enum import TipoSegredo, TipoPermissao

T = TypeVar("T")

def __assert_not_null(thing: T | None) -> T:
    assert thing is not None
    return thing

class SegredoDAOImpl(SegredoDAO):

    def __init__(self, transacted_conn: TransactedConnection) -> None:
        self.__cf: TransactedConnection = transacted_conn

    def buscar_pk_segredo(self, pk: SegredoPK) -> SegredoPK | None:
        self.__cf.execute("SELECT pk_segredo FROM segredo WHERE pk_segredo = ?", [pk.pk_segredo])
        tupla = self.__cf.fetchone()
        if tupla is None: return None
        return pk

    def limpar_segredo(self, pk: SegredoPK) -> None:
        self.__cf.execute("DELETE FROM campo_segredo WHERE pfk_segredo = ?", [pk.pk_segredo])
        self.__cf.execute("DELETE FROM permissao WHERE pfk_segredo = ?", [pk.pk_segredo])
        self.__cf.execute("DELETE FROM categoria_segredo WHERE pfk_segredo = ?", [pk.pk_segredo])

    def criar_campo_segredo(self, pk: SegredoPK, descricao: str, valor: str) -> int:
        self.__cf.execute("INSERT INTO campo_segredo (pfk_segredo, pk_descricao, valor) VALUES (?, ?, ?)", [pk.pk_segredo, descricao, valor])
        return __assert_not_null(self.__cf.lastrowid)

    def criar_permissao(self, upk: UsuarioPK, spk: SegredoPK, tipo_permissao: TipoPermissao) -> int:
        self.__cf.execute("INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (?, ?, ?)", [upk, spk.pk_segredo, tipo_permissao.value])
        return __assert_not_null(self.__cf.lastrowid)

    def criar_categoria_segredo(self, spk: SegredoPK, cpk: CategoriaPK) -> int:
        self.__cf.execute("INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (?, ?)", [spk.pk_segredo, cpk])
        return __assert_not_null(self.__cf.lastrowid)

    def criar_segredo(self, nome: str, descricao: str, tipo_segredo: TipoSegredo) -> SegredoPK:
        self.__cf.execute("INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES (?, ?, ?)", [nome, descricao, tipo_segredo.value])
        return SegredoPK(__assert_not_null(self.__cf.lastrowid))

    def alterar_segredo(self, pk: SegredoPK, nome: str, descricao: str, tipo_segredo: TipoSegredo) -> None:
        self.__cf.execute("UPDATE segredo SET nome = ?, descricao = ?, fk_tipo_segredo = ? WHERE pk_segredo = ?", [nome, descricao, tipo_segredo.value, pk.pk_segredo])

    def listar_todos_segredos(self) -> list[CabecalhoDeSegredo]:
        self.__cf.execute("SELECT pk_segredo, pk_tipo_segredo, nome, descricao, fk_tipo_segredo FROM segredo")
        return self.__cf.fetchall_class(CabecalhoDeSegredo)

    def listar_segredos_visiveis(self, login: str) -> list[CabecalhoDeSegredo]:
        self.__cf.execute("SELECT s.pk_segredo, s.pk_tipo_segredo, s.nome, s.descricao, s.fk_tipo_segredo FROM segredo s INNER JOIN permissao p ON p.pfk_segredo = s.pk_segredo INNER JOIN usuario u ON p.pfk_usuario = u.pk_usuario WHERE u.login = ?", [login])
        return self.__cf.fetchall_class(CabecalhoDeSegredo)

    def buscar_permissao(self, pk: SegredoPK, login: str) -> int | None:
        self.__cf.execute("SELECT p.fk_tipo_permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ? AND u.login = ?", [pk.pk_segredo, login])
        tupla = self.__cf.fetchone()
        if tupla is None: return None
        return int(tupla[0])

    def deletar_segredo(self, pk: SegredoPK) -> None:
        self.__cf.execute("DELETE FROM segredo WHERE pk_segredo = ?", [pk.pk_segredo]) # Deleta nas outras tabelas graças ao ON DELETE CASCADE.

    def ler_cabecalho_segredo(self, pk: SegredoPK) -> CabecalhoDeSegredo | None:
        self.__cf.execute("SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo = ?", [pk.pk_segredo])
        return self.__cf.fetchone_class(CabecalhoDeSegredo)

    def ler_campos_segredo(self, pk: SegredoPK) -> list[CampoDeSegredo]:
        self.__cf.execute("SELECT pk_chave, valor FROM campo_segredo WHERE pfk_segredo = ?", [pk.pk_segredo])
        return self.__cf.fetchall_class(CampoDeSegredo)

    def ler_login_com_permissoes(self, pk: SegredoPK) -> list[LoginComPermissao]:
        self.__cf.execute("SELECT u.login, p.fk_tipo_permissao AS permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ?", [pk.pk_segredo])
        return self.__cf.fetchall_class(LoginComPermissao)