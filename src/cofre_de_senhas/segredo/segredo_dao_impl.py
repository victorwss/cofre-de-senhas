from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.dao import SegredoDAO, SegredoPK, UsuarioPK, CategoriaPK, DadosSegredo, DadosSegredoSemPK, CampoDeSegredo, LoginComPermissao, LoginUsuario, CategoriaDeSegredo, PermissaoDeSegredo, BuscaPermissaoPorLogin

class SegredoDAOImpl(SegredoDAO):

    def __init__(self) -> None:
        SegredoDAO.register(self)

    # CRUD básico

    def buscar_por_pk(self, pk: SegredoPK) -> DadosSegredo | None:
        sql: str = "SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo = ?"
        Raiz.instance().execute(sql, [pk.pk_segredo])
        return Raiz.instance().fetchone_class(DadosSegredo)

    def listar(self) -> list[DadosSegredo]:
        sql: str = "SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo"
        Raiz.instance().execute(sql)
        return Raiz.instance().fetchall_class(DadosSegredo)

    def criar(self, dados: DadosSegredoSemPK) -> SegredoPK:
        sql: str = "INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES (?, ?, ?)"
        Raiz.instance().execute(sql, [dados.nome, dados.descricao, dados.fk_tipo_segredo])
        return SegredoPK(Raiz.instance().asserted_lastrowid)

    def salvar_com_pk(self, dados: DadosSegredo) -> None:
        sql: str = "UPDATE segredo SET pk_segredo = ?, nome = ?, descricao = ?, fk_tipo_segredo = ? WHERE pk_segredo = ?"
        Raiz.instance().execute(sql, [dados.pk_segredo, dados.nome, dados.descricao, dados.fk_tipo_segredo, dados.pk_segredo])

    def deletar_por_pk(self, pk: SegredoPK) -> None:
        # self.limpar_segredo(pk) # Desnecessário, pois deleta nas outras tabelas graças ao ON DELETE CASCADE.
        sql: str = "DELETE FROM segredo WHERE pk_segredo = ?"
        Raiz.instance().execute(sql, [pk.pk_segredo])

    # Métodos auxiliares.

    def listar_visiveis(self, login: LoginUsuario) -> list[DadosSegredo]:
        sql: str = "" \
            + "SELECT s.pk_segredo, s.nome, s.descricao, s.fk_tipo_segredo " \
            + "FROM segredo s " \
            + "INNER JOIN permissao p ON p.pfk_segredo = s.pk_segredo " \
            + "INNER JOIN usuario u ON p.pfk_usuario = u.pk_usuario " \
            + "WHERE u.login = ? AND u.fk_nivel_acesso IN (1, 2)" \
            + "UNION " \
            + "SELECT p.pk_segredo, p.nome, p.descricao, p.fk_tipo_segredo " \
            + "FROM segredo p " \
            + "WHERE p.fk_tipo_segredo IN (1, 2) " \
            + "ORDER BY pk_segredo"
        Raiz.instance().execute(sql, [login.valor])
        return Raiz.instance().fetchall_class(DadosSegredo)

    # TESTAR
    def limpar_segredo(self, pk: SegredoPK) -> None:
        sql1: str = "DELETE FROM campo_segredo WHERE pfk_segredo = ?"
        sql2: str = "DELETE FROM permissao WHERE pfk_segredo = ?"
        sql3: str = "DELETE FROM categoria_segredo WHERE pfk_segredo = ?"
        Raiz.instance().execute(sql1, [pk.pk_segredo])
        Raiz.instance().execute(sql2, [pk.pk_segredo])
        Raiz.instance().execute(sql3, [pk.pk_segredo])

    def listar_por_pks(self, pks: list[SegredoPK]) -> list[DadosSegredo]:
        wildcards: str = ", ".join(["?" for pk in pks])
        sql: str = f"SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo IN ({wildcards})"
        Raiz.instance().execute(sql, [pk.pk_segredo for pk in pks])
        return Raiz.instance().fetchall_class(DadosSegredo)

    #def buscar_por_nomes(self, nomes: list[nome]) -> list[DadosSegredo]:
    #    wildcards: str = ", ".join(["?" for pk in pks])
    #    sql: str = "" \
    #        + "SELECT s.pk_segredo, s.nome, s.descricao, s.fk_tipo_segredo " \
    #        + "FROM segredo s " \
    #        + "INNER JOIN categoria_segredo cs ON s.pk_segredo = cs.pfk_segredo " \
    #        + "INNER JOIN categoria c ON c.categoria = cs.pfk_categoria " \
    #        + f"WHERE nome IN ({wildcards})"
    #    Raiz.instance().execute(sql, nomes)
    #    return Raiz.instance().fetchall_class(DadosSegredo)

    # Categoria de segredo

    # TESTAR
    def criar_categoria_segredo(self, c: CategoriaDeSegredo) -> None:
        sql: str = "INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (?, ?)"
        Raiz.instance().execute(sql, [c.pk_segredo, c.pk_categoria])

    # Campos

    # TESTAR
    def criar_campo_segredo(self, campo: CampoDeSegredo) -> None:
        sql: str = "INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (?, ?, ?)"
        Raiz.instance().execute(sql, [campo.pk_segredo, campo.pk_nome, campo.valor])

    # TESTAR
    def ler_campos_segredo(self, pk: SegredoPK) -> list[CampoDeSegredo]:
        sql: str = "SELECT pfk_segredo, pk_nome, valor FROM campo_segredo WHERE pfk_segredo = ?"
        Raiz.instance().execute(sql, [pk.pk_segredo])
        return Raiz.instance().fetchall_class(CampoDeSegredo)

    # Permissões

    # TESTAR
    def criar_permissao(self, permissao: PermissaoDeSegredo) -> None:
        sql: str = "INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (?, ?, ?)"
        Raiz.instance().execute(sql, [permissao.pfk_usuario, permissao.pfk_segredo, permissao.fk_tipo_permissao])

    # TESTAR
    def buscar_permissao(self, busca: BuscaPermissaoPorLogin) -> PermissaoDeSegredo | None:
        sql: str = "" \
            + "SELECT p.pfk_usuario, p.pfk_segredo, p.fk_tipo_permissao " \
            + "FROM permissao p " \
            + "INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario " \
            + "WHERE p.pfk_segredo = ? AND u.login = ?"
        Raiz.instance().execute(sql, [busca.pfk_segredo, busca.login])
        return Raiz.instance().fetchone_class(PermissaoDeSegredo)

    # TESTAR
    def ler_login_com_permissoes(self, pk: SegredoPK) -> list[LoginComPermissao]:
        sql: str = "" \
            + "SELECT u.login, p.fk_tipo_permissao AS permissao " \
            + "FROM permissao p " \
            + "INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario " \
            + "WHERE p.pfk_segredo = ?"
        Raiz.instance().execute(sql, [pk.pk_segredo])
        return Raiz.instance().fetchall_class(LoginComPermissao)