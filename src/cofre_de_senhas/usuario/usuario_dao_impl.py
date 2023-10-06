from typing import override
from connection.trans import TransactedConnection
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioSemPK, SegredoPK, DadosUsuarioComPermissao, LoginUsuario

class UsuarioDAOImpl(UsuarioDAO):

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)
        UsuarioDAO.register(self)

    # CRUD básico

    @override
    def buscar_por_pk(self, pk: UsuarioPK) -> DadosUsuario | None:
        sql: str = "SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario = ?"
        self._raiz.execute(sql, [pk.pk_usuario])
        return self._raiz.fetchone_class(DadosUsuario)

    @override
    def listar_por_pks(self, pks: list[UsuarioPK]) -> list[DadosUsuario]:
        wildcards: str = ", ".join(["?" for pk in pks])
        sql: str = f"SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario IN ({wildcards}) ORDER BY pk_usuario"
        self._raiz.execute(sql, [pk.pk_usuario for pk in pks])
        return self._raiz.fetchall_class(DadosUsuario)

    @override
    def listar(self) -> list[DadosUsuario]:
        sql: str = "SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario ORDER BY pk_usuario"
        self._raiz.execute(sql)
        return self._raiz.fetchall_class(DadosUsuario)

    @override
    def listar_por_logins(self, logins: list[LoginUsuario]) -> list[DadosUsuario]:
        wildcards: str = ", ".join(["?" for login in logins])
        sql: str = f"SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE login IN ({wildcards}) ORDER BY pk_usuario"
        self._raiz.execute(sql, [login.valor for login in logins])
        return self._raiz.fetchall_class(DadosUsuario)

    @override
    def criar(self, dados: DadosUsuarioSemPK) -> UsuarioPK:
        sql: str = "INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)"
        self._raiz.execute(sql, [dados.login, dados.fk_nivel_acesso, dados.hash_com_sal])
        return UsuarioPK(self._raiz.asserted_lastrowid)

    @override
    def salvar_com_pk(self, dados: DadosUsuario) -> bool:
        sql: str = "UPDATE usuario SET pk_usuario = ?, login = ?, fk_nivel_acesso = ?, hash_com_sal = ? WHERE pk_usuario = ?"
        self._raiz.execute(sql, [dados.pk_usuario, dados.login, dados.fk_nivel_acesso, dados.hash_com_sal, dados.pk_usuario])
        return self._raiz.rowcount > 0

    @override
    def deletar_por_pk(self, pk: UsuarioPK) -> bool:
        sql: str = "DELETE FROM usuario WHERE pk_usuario = ?"
        self._raiz.execute(sql, [pk.pk_usuario])
        return self._raiz.rowcount > 0

    # Métodos auxiliares

    @override
    def buscar_por_login(self, login: LoginUsuario) -> DadosUsuario | None:
        sql: str = "SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE login = ?"
        self._raiz.execute(sql, [login.valor])
        return self._raiz.fetchone_class(DadosUsuario)

    #def deletar_por_login(self, login: str) -> None:
    #    sql: str = "DELETE usuario WHERE login = ?"
    #    self._raiz.execute(sql, [login])

    # Métodos com joins em outras tabelas

    # TESTAR
    @override
    def listar_por_permissao(self, pk: SegredoPK) -> list[DadosUsuarioComPermissao]:
        sql: str = "" \
            + "SELECT u.pk_usuario, u.login, u.fk_nivel_acesso, u.hash_com_sal, p.fk_tipo_permissao " \
            + "FROM usuario u " \
            + "INNER JOIN permissao p ON u.pk_usuario = p.pfk_usuario " \
            + "WHERE p.pfk_segredo = ?" \
            + "ORDER BY u.pk_usuario"
        self._raiz.execute(sql, [pk.pk_segredo])
        return self._raiz.fetchall_class(DadosUsuarioComPermissao)