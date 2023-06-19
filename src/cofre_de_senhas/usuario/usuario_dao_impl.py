from connection.conn import TransactedConnection
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioSemPK, SegredoPK, DadosUsuarioComPermissao

class UsuarioDAOImpl(UsuarioDAO):

    def __init__(self, transacted_conn: TransactedConnection) -> None:
        self.__cf: TransactedConnection = transacted_conn

    # CRUD básico

    def buscar_por_pk(self, pk: UsuarioPK) -> DadosUsuario | None:
        self.__cf.execute("SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario = ?", [pk.pk_usuario])
        return self.__cf.fetchone_class(DadosUsuario)

    def buscar_por_pks(self, pks: list[UsuarioPK]) -> list[DadosUsuario]:
        wildcards: str = ", ".join(["?" for pk in pks])
        self.__cf.execute("SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario IN (" + wildcards + ")", [pk.pk_usuario for pk in pks])
        return self.__cf.fetchall_class(DadosUsuario)

    def listar(self) -> list[DadosUsuario]:
        self.__cf.execute("SELECT c.pk_usuario, c.login, c.fk_nivel_acesso, c.hash_com_sal FROM usuario c")
        return self.__cf.fetchall_class(DadosUsuario)

    def criar(self, dados: DadosUsuarioSemPK) -> UsuarioPK:
        self.__cf.execute("INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)", [dados.login, dados.fk_nivel_acesso, dados.hash_com_sal])
        return UsuarioPK(self.__cf.asserted_lastrowid)

    def salvar(self, dados: DadosUsuario) -> None:
        sql = "UPDATE usuario SET pk_usuario = ?, login = ?, fk_nivel_acesso = ?, hash_com_sal = ? WHERE pk_usuario = ?"
        self.__cf.execute(sql, [dados.pk_usuario, dados.login, dados.fk_nivel_acesso, dados.hash_com_sal, dados.pk_usuario])

    def deletar_por_pk(self, pk: UsuarioPK) -> None:
        self.__cf.execute("DELETE usuario WHERE pk_usuario = ?", [pk.pk_usuario])

    # Métodos auxiliares

    def buscar_por_login(self, login: str) -> DadosUsuario | None:
        self.__cf.execute("SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE login = ?", [login])
        return self.__cf.fetchone_class(DadosUsuario)

    #def deletar_por_login(self, login: str) -> None:
    #    self.__cf.execute("DELETE usuario WHERE login = ?", [login])

    # Métodos com joins em outras tabelas

    def listar_por_permissao(self, pk: SegredoPK) -> list[DadosUsuarioComPermissao]:
        self.__cf.execute("SELECT u.pk_usuario, u.login, u.fk_nivel_acesso, u.hash_com_sal, p.fk_tipo_permissao FROM usuario u INNER JOIN permissao p ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ?", [pk.pk_segredo])
        return self.__cf.fetchall_class(DadosUsuarioComPermissao)
