from typing import override
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioSemPK, SegredoPK, DadosUsuarioComPermissao, LoginUsuario

class UsuarioDAOImpl(UsuarioDAO):

    def __init__(self) -> None:
        UsuarioDAO.register(self)

    # CRUD básico

    @override
    def buscar_por_pk(self, pk: UsuarioPK) -> DadosUsuario | None:
        sql: str = "SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario = ?"
        Raiz.instance().execute(sql, [pk.pk_usuario])
        return Raiz.instance().fetchone_class(DadosUsuario)

    @override
    def listar_por_pks(self, pks: list[UsuarioPK]) -> list[DadosUsuario]:
        wildcards: str = ", ".join(["?" for pk in pks])
        sql: str = f"SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario IN ({wildcards}) ORDER BY pk_usuario"
        Raiz.instance().execute(sql, [pk.pk_usuario for pk in pks])
        return Raiz.instance().fetchall_class(DadosUsuario)

    @override
    def listar(self) -> list[DadosUsuario]:
        sql: str = "SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario ORDER BY pk_usuario"
        Raiz.instance().execute(sql)
        return Raiz.instance().fetchall_class(DadosUsuario)

    @override
    def listar_por_logins(self, logins: list[LoginUsuario]) -> list[DadosUsuario]:
        wildcards: str = ", ".join(["?" for login in logins])
        sql: str = f"SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE login IN ({wildcards}) ORDER BY pk_usuario"
        Raiz.instance().execute(sql, [login.valor for login in logins])
        return Raiz.instance().fetchall_class(DadosUsuario)

    @override
    def criar(self, dados: DadosUsuarioSemPK) -> UsuarioPK:
        sql: str = "INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)"
        Raiz.instance().execute(sql, [dados.login, dados.fk_nivel_acesso, dados.hash_com_sal])
        return UsuarioPK(Raiz.instance().asserted_lastrowid)

    @override
    def salvar_com_pk(self, dados: DadosUsuario) -> None:
        sql: str = "UPDATE usuario SET pk_usuario = ?, login = ?, fk_nivel_acesso = ?, hash_com_sal = ? WHERE pk_usuario = ?"
        Raiz.instance().execute(sql, [dados.pk_usuario, dados.login, dados.fk_nivel_acesso, dados.hash_com_sal, dados.pk_usuario])

    @override
    def deletar_por_pk(self, pk: UsuarioPK) -> None:
        sql: str = "DELETE FROM usuario WHERE pk_usuario = ?"
        Raiz.instance().execute(sql, [pk.pk_usuario])

    # Métodos auxiliares

    @override
    def buscar_por_login(self, login: LoginUsuario) -> DadosUsuario | None:
        sql: str = "SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE login = ?"
        Raiz.instance().execute(sql, [login.valor])
        return Raiz.instance().fetchone_class(DadosUsuario)

    #def deletar_por_login(self, login: str) -> None:
    #    sql: str = "DELETE usuario WHERE login = ?"
    #    Raiz.instance().execute(sql, [login])

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
        Raiz.instance().execute(sql, [pk.pk_segredo])
        return Raiz.instance().fetchall_class(DadosUsuarioComPermissao)