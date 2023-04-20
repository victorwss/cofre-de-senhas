from typing import TypeVar
from connection.conn import TransactedConnection
from validator import dataclass_validate
from .dao import *

T = TypeVar("T")

def __assert_not_null(thing: T | None) -> T:
    assert thing is not None
    return thing

class CofreDeSenhasDAOImpl(CofreDeSenhasDAO):

    def __init__(self, transacted_conn: TransactedConnection) -> None:
        self.__cf: TransactedConnection = transacted_conn

    def sql_criar_bd(self) -> str:
        with open("create.sql", "r") as f:
            return f.read()

    def criar_bd(self) -> None:
        self.__cf.executescript(self.sql_criar_bd())

    def buscar_pk_usuario_por_login(self, login: str) -> int | None:
        self.__cf.execute("SELECT pk_usuario FROM usuario WHERE login = ?", [login])
        tupla = self.__cf.fetchone()
        if tupla is None: return None
        return int(tupla[0])

    def buscar_pk_segredo(self, pk: int) -> int | None:
        self.__cf.execute("SELECT pk_segredo FROM segredo WHERE pk_segredo = ?", [pk])
        tupla = self.__cf.fetchone()
        if tupla is None: return None
        return int(tupla[0])

    def login(self, login: str) -> DadosLogin | None:
        self.__cf.execute("SELECT fk_nivel_acesso, hash_com_sal FROM usuario WHERE login = ?", [login])
        return self.__cf.fetchone_class(DadosLogin)

    def criar_usuario(self, login: str, nivel_acesso: int, hash_com_sal: str) -> None:
        self.__cf.execute("INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)", [login, nivel_acesso, hash_com_sal])

    def trocar_senha(self, login: str, hash_com_sal: str) -> None:
        self.__cf.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, login])

    def alterar_nivel_de_acesso(self, login: str, nivel_acesso: int) -> None:
        self.__cf.execute("UPDATE usuario SET fk_nivel_acesso = ? WHERE login = ?", [nivel_acesso, login])

    def listar_usuarios(self) -> list[DadosNivel]:
        self.__cf.execute("SELECT login, fk_nivel_acesso FROM usuario")
        return self.__cf.fetchall_class(DadosNivel)

    def limpar_segredo(self, segredo: int) -> None:
        self.__cf.execute("DELETE FROM campo_segredo WHERE pfk_segredo = ?", [segredo])
        self.__cf.execute("DELETE FROM permissao WHERE pfk_segredo = ?", [segredo])
        self.__cf.execute("DELETE FROM categoria_segredo WHERE pfk_segredo = ?", [segredo])

    def criar_campo_segredo(self, segredo: int, descricao: str, valor: str) -> int:
        self.__cf.execute("INSERT INTO campo_segredo (pfk_segredo, pk_descricao, valor) VALUES (?, ?, ?)", [segredo, descricao, valor])
        return __assert_not_null(self.__cf.lastrowid)

    def criar_permissao(self, usuario: int, segredo: int, tipo_permissao: int) -> int:
        self.__cf.execute("INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (?, ?, ?)", [usuario, segredo, tipo_permissao])
        return __assert_not_null(self.__cf.lastrowid)

    def criar_categoria_segredo(self, segredo: int, categoria: int) -> int:
        self.__cf.execute("INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (?, ?)", [segredo, categoria])
        return __assert_not_null(self.__cf.lastrowid)

    def criar_segredo(self, nome: str, descricao: str, tipo_segredo: int) -> int:
        self.__cf.execute("INSERT INTO segredo(nome, descricao, fk_tipo_segredo) VALUES (?, ?, ?)", [nome, descricao, tipo_segredo])
        return __assert_not_null(self.__cf.lastrowid)

    def alterar_segredo(self, segredo: int, nome: str, descricao: str, tipo_segredo: int) -> None:
        self.__cf.execute("UPDATE segredo SET nome = ?, descricao = ?, fk_tipo_segredo = ? WHERE pk_segredo = ?", [nome, descricao, tipo_segredo, segredo])

    def listar_todos_segredos(self) -> list[CabecalhoDeSegredo]:
        self.__cf.execute("SELECT pk_segredo, pk_tipo_segredo, nome, descricao, fk_tipo_segredo FROM segredo")
        return self.__cf.fetchall_class(CabecalhoDeSegredo)

    def listar_segredos_visiveis(self, login: str) -> list[CabecalhoDeSegredo]:
        self.__cf.execute("SELECT s.pk_segredo, s.pk_tipo_segredo, s.nome, s.descricao, s.fk_tipo_segredo FROM segredo s INNER JOIN permissao p ON p.pfk_segredo = s.pk_segredo INNER JOIN usuario u ON p.pfk_usuario = u.pk_usuario WHERE u.login = ?", [login])
        return self.__cf.fetchall_class(CabecalhoDeSegredo)

    def buscar_permissao(self, segredo: int, login: str) -> int | None:
        self.__cf.execute("SELECT p.fk_tipo_permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ? AND u.login = ?", [segredo, login])
        tupla = self.__cf.fetchone()
        if tupla is None: return None
        return int(tupla[0])

    def deletar_segredo(self, segredo: int) -> None:
        self.__cf.execute("DELETE FROM segredo WHERE pk_segredo = ?", [segredo]) # Deleta nas outras tabelas graças ao ON DELETE CASCADE.

    def ler_cabecalho_segredo(self, pk_segredo: int) -> CabecalhoDeSegredo | None:
        self.__cf.execute("SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo = ?", [pk_segredo])
        return self.__cf.fetchone_class(CabecalhoDeSegredo)

    def ler_campos_segredo(self, pk_segredo: int) -> list[CampoDeSegredo]:
        self.__cf.execute("SELECT c.pk_chave AS chave, c.valor FROM campo_segredo WHERE pfk_segredo = ?", [pk_segredo])
        return self.__cf.fetchall_class(CampoDeSegredo)

    def ler_login_com_permissoes(self, pk_segredo: int) -> list[LoginComPermissao]:
        self.__cf.execute("SELECT u.login, p.fk_tipo_permissao AS permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ?", [pk_segredo])
        return self.__cf.fetchall_class(LoginComPermissao)

class CategoriaDAOImpl(CategoriaDAO):

    def __init__(self, transacted_conn: TransactedConnection) -> None:
        self.__cf: TransactedConnection = transacted_conn

    def buscar_por_pk(self, pk_categoria: int) -> DadosCategoria | None:
        self.__cf.execute("SELECT pk_categoria, nome FROM categoria WHERE pk_categoria = ?", [pk_categoria])
        return self.__cf.fetchone_class(DadosCategoria)

    def buscar_por_nome(self, nome: str) -> DadosCategoria | None:
        self.__cf.execute("SELECT pk_categoria, nome FROM categoria WHERE nome = ?", [nome])
        return self.__cf.fetchone_class(DadosCategoria)

    def listar(self) -> list[DadosCategoria]:
        self.__cf.execute("SELECT c.pk_categoria, c.nome FROM categoria c")
        return self.__cf.fetchall_class(DadosCategoria)

    def listar_por_segredo(self, pk_segredo: int) -> list[DadosCategoria]:
        self.__cf.execute("SELECT c.pk_categoria, c.nome FROM categoria c INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria WHERE cs.pfk_segredo = ?", [pk_segredo])
        return self.__cf.fetchall_class(DadosCategoria)

    def criar(self, dados: DadosCategoriaSemPK) -> int:
        self.__cf.execute("INSERT INTO categoria (nome) VALUES (?)", [dados.nome])
        return __assert_not_null(self.__cf.lastrowid)

    def salvar(self, dados: DadosCategoria) -> None:
        self.__cf.execute("UPDATE categoria SET pk_categoria = ?, nome = ? WHERE pk_categoria = ?", [dados.pk_categoria, dados.nome, dados.pk_categoria])

    def deletar_por_nome(self, nome: str) -> None:
        self.__cf.execute("DELETE categoria WHERE nome = ?", [nome])

    def deletar_por_pk(self, pk_categoria: int) -> None:
        self.__cf.execute("DELETE categoria WHERE pk_categoria = ?", [pk_categoria])
