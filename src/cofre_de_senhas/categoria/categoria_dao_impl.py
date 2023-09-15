from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoria

class CategoriaDAOImpl(CategoriaDAO):

    def __init__(self) -> None:
        CategoriaDAO.register(self)

    # CRUD básico

    def buscar_por_pk(self, pk: CategoriaPK) -> DadosCategoria | None:
        sql: str = "SELECT pk_categoria, nome FROM categoria WHERE pk_categoria = ?"
        Raiz.instance().execute(sql, [pk.pk_categoria])
        return Raiz.instance().fetchone_class(DadosCategoria)

    def listar_por_pks(self, pks: list[CategoriaPK]) -> list[DadosCategoria]:
        wildcards: str = ", ".join(["?" for pk in pks])
        ns: list[int] = [pk.pk_categoria for pk in pks]
        sql = f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria IN ({wildcards}) ORDER BY pk_categoria"
        Raiz.instance().execute(sql, ns)
        return Raiz.instance().fetchall_class(DadosCategoria)

    def listar(self) -> list[DadosCategoria]:
        sql: str = "SELECT c.pk_categoria, c.nome FROM categoria c ORDER BY pk_categoria"
        Raiz.instance().execute(sql)
        return Raiz.instance().fetchall_class(DadosCategoria)

    def listar_por_nomes(self, nomes: list[NomeCategoria]) -> list[DadosCategoria]:
        wildcards: str = ", ".join(["?" for nome in nomes])
        ns: list[str] = [nome.valor for nome in nomes]
        sql: str = f"SELECT pk_categoria, nome FROM categoria WHERE nome IN ({wildcards}) ORDER BY pk_categoria"
        Raiz.instance().execute(sql, ns)
        return Raiz.instance().fetchall_class(DadosCategoria)

    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        sql: str = "INSERT INTO categoria (nome) VALUES (?)"
        Raiz.instance().execute(sql, [dados.nome])
        return CategoriaPK(Raiz.instance().asserted_lastrowid)

    def salvar_com_pk(self, dados: DadosCategoria) -> None:
        sql: str = "UPDATE categoria SET pk_categoria = ?, nome = ? WHERE pk_categoria = ?"
        Raiz.instance().execute(sql, [dados.pk_categoria, dados.nome, dados.pk_categoria])

    def deletar_por_pk(self, pk: CategoriaPK) -> None:
        sql: str = "DELETE FROM categoria WHERE pk_categoria = ?"
        Raiz.instance().execute(sql, [pk.pk_categoria])

    # Métodos auxiliares

    def buscar_por_nome(self, nome: NomeCategoria) -> DadosCategoria | None:
        Raiz.instance().execute("SELECT pk_categoria, nome FROM categoria WHERE nome = ?", [nome.valor])
        return Raiz.instance().fetchone_class(DadosCategoria)

    #def deletar_por_nome(self, nome: NomeCategoria) -> None:
    #    Raiz.instance().execute("DELETE categoria WHERE nome = ?", [nome.valor])

    # Métodos com joins em outras tabelas

    # TESTAR
    def listar_por_segredo(self, pk: SegredoPK) -> list[DadosCategoria]:
        sql: str = "" \
            + "SELECT c.pk_categoria, c.nome " \
            + "FROM categoria c " \
            + "INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria " \
            + "WHERE cs.pfk_segredo = ? " \
            + "ORDER BY c.pk_categoria"
        Raiz.instance().execute(sql, [pk.pk_segredo])
        return Raiz.instance().fetchall_class(DadosCategoria)