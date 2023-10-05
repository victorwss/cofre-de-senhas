from typing import override
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoria

class CategoriaDAOImpl(CategoriaDAO):

    def __init__(self, raiz: Raiz) -> None:
        super().__init__(raiz)
        CategoriaDAO.register(self)

    # CRUD básico

    @override
    def buscar_por_pk(self, pk: CategoriaPK) -> DadosCategoria | None:
        sql: str = "SELECT pk_categoria, nome FROM categoria WHERE pk_categoria = ?"
        self._raiz.execute(sql, [pk.pk_categoria])
        return self._raiz.fetchone_class(DadosCategoria)

    @override
    def listar_por_pks(self, pks: list[CategoriaPK]) -> list[DadosCategoria]:
        wildcards: str = ", ".join(["?" for pk in pks])
        ns: list[int] = [pk.pk_categoria for pk in pks]
        sql = f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria IN ({wildcards}) ORDER BY pk_categoria"
        self._raiz.execute(sql, ns)
        return self._raiz.fetchall_class(DadosCategoria)

    @override
    def listar(self) -> list[DadosCategoria]:
        sql: str = "SELECT c.pk_categoria, c.nome FROM categoria c ORDER BY pk_categoria"
        self._raiz.execute(sql)
        return self._raiz.fetchall_class(DadosCategoria)

    @override
    def listar_por_nomes(self, nomes: list[NomeCategoria]) -> list[DadosCategoria]:
        wildcards: str = ", ".join(["?" for nome in nomes])
        ns: list[str] = [nome.valor for nome in nomes]
        sql: str = f"SELECT pk_categoria, nome FROM categoria WHERE nome IN ({wildcards}) ORDER BY pk_categoria"
        self._raiz.execute(sql, ns)
        return self._raiz.fetchall_class(DadosCategoria)

    @override
    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        sql: str = "INSERT INTO categoria (nome) VALUES (?)"
        self._raiz.execute(sql, [dados.nome])
        return CategoriaPK(self._raiz.asserted_lastrowid)

    @override
    def salvar_com_pk(self, dados: DadosCategoria) -> bool:
        sql: str = "UPDATE categoria SET pk_categoria = ?, nome = ? WHERE pk_categoria = ?"
        self._raiz.execute(sql, [dados.pk_categoria, dados.nome, dados.pk_categoria])
        return self._raiz.rowcount > 0

    @override
    def deletar_por_pk(self, pk: CategoriaPK) -> bool:
        sql: str = "DELETE FROM categoria WHERE pk_categoria = ?"
        self._raiz.execute(sql, [pk.pk_categoria])
        return self._raiz.rowcount > 0

    # Métodos auxiliares

    @override
    def buscar_por_nome(self, nome: NomeCategoria) -> DadosCategoria | None:
        self._raiz.execute("SELECT pk_categoria, nome FROM categoria WHERE nome = ?", [nome.valor])
        return self._raiz.fetchone_class(DadosCategoria)

    #def deletar_por_nome(self, nome: NomeCategoria) -> None:
    #    self._raiz.execute("DELETE categoria WHERE nome = ?", [nome.valor])

    # Métodos com joins em outras tabelas

    @override
    def listar_por_segredo(self, pk: SegredoPK) -> list[DadosCategoria]:
        sql: str = "" \
            + "SELECT c.pk_categoria, c.nome " \
            + "FROM categoria c " \
            + "INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria " \
            + "WHERE cs.pfk_segredo = ? " \
            + "ORDER BY c.pk_categoria"
        self._raiz.execute(sql, [pk.pk_segredo])
        return self._raiz.fetchall_class(DadosCategoria)