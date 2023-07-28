from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioSemPK, SegredoPK, DadosUsuarioComPermissao

class UsuarioDAOImpl(UsuarioDAO):

    def __init__(self) -> None:
        UsuarioDAO.register(self)

    # CRUD básico

    def buscar_por_pk(self, pk: UsuarioPK) -> DadosUsuario | None:
        Raiz.instance().execute("SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario = ?", [pk.pk_usuario])
        return Raiz.instance().fetchone_class(DadosUsuario)

    def buscar_por_pks(self, pks: list[UsuarioPK]) -> list[DadosUsuario]:
        wildcards: str = ", ".join(["?" for pk in pks])
        Raiz.instance().execute(f"SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE pk_usuario IN ({wildcards})", [pk.pk_usuario for pk in pks])
        return Raiz.instance().fetchall_class(DadosUsuario)

    def listar(self) -> list[DadosUsuario]:
        Raiz.instance().execute("SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario c")
        return Raiz.instance().fetchall_class(DadosUsuario)

    def listar_por_logins(self, logins: list[str]) -> list[DadosUsuario]:
        wildcards: str = ", ".join(["?" for login in logins])
        Raiz.instance().execute(f"SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario c WHERE login IN ({wildcards})", logins)
        return Raiz.instance().fetchall_class(DadosUsuario)

    def criar(self, dados: DadosUsuarioSemPK) -> UsuarioPK:
        Raiz.instance().execute("INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)", [dados.login, dados.fk_nivel_acesso, dados.hash_com_sal])
        return UsuarioPK(Raiz.instance().asserted_lastrowid)

    def salvar(self, dados: DadosUsuario) -> None:
        sql = "UPDATE usuario SET pk_usuario = ?, login = ?, fk_nivel_acesso = ?, hash_com_sal = ? WHERE pk_usuario = ?"
        Raiz.instance().execute(sql, [dados.pk_usuario, dados.login, dados.fk_nivel_acesso, dados.hash_com_sal, dados.pk_usuario])

    def deletar_por_pk(self, pk: UsuarioPK) -> None:
        Raiz.instance().execute("DELETE usuario WHERE pk_usuario = ?", [pk.pk_usuario])

    # Métodos auxiliares

    def buscar_por_login(self, login: str) -> DadosUsuario | None:
        Raiz.instance().execute("SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE login = ?", [login])
        return Raiz.instance().fetchone_class(DadosUsuario)

    #def deletar_por_login(self, login: str) -> None:
    #    Raiz.instance().execute("DELETE usuario WHERE login = ?", [login])

    # Métodos com joins em outras tabelas

    def listar_por_permissao(self, pk: SegredoPK) -> list[DadosUsuarioComPermissao]:
        Raiz.instance().execute("SELECT u.pk_usuario, u.login, u.fk_nivel_acesso, u.hash_com_sal, p.fk_tipo_permissao FROM usuario u INNER JOIN permissao p ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ?", [pk.pk_segredo])
        return Raiz.instance().fetchall_class(DadosUsuarioComPermissao)
