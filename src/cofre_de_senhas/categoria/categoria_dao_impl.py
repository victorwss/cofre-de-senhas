from typing import override
from connection.trans import TransactedConnection
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoria

class CategoriaDAOImpl(CategoriaDAO):

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)

    # CRUD básico

    @override
    def buscar_por_pk(self, pk: CategoriaPK) -> DadosCategoria | None:
        sql: str = f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria = {self._placeholder}"
        self._connection.execute(sql, [pk.pk_categoria])
        return self._connection.fetchone_class(DadosCategoria)

    @override
    def listar_por_pks(self, pks: list[CategoriaPK]) -> list[DadosCategoria]:
        wildcards: str = ", ".join([self._placeholder for pk in pks])
        ns: list[int] = [pk.pk_categoria for pk in pks]
        sql = f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria IN ({wildcards}) ORDER BY pk_categoria"
        self._connection.execute(sql, ns)
        return self._connection.fetchall_class(DadosCategoria)

    @override
    def listar(self) -> list[DadosCategoria]:
        sql: str = "SELECT c.pk_categoria, c.nome FROM categoria c ORDER BY pk_categoria"
        self._connection.execute(sql)
        return self._connection.fetchall_class(DadosCategoria)

    @override
    def listar_por_nomes(self, nomes: list[NomeCategoria]) -> list[DadosCategoria]:
        wildcards: str = ", ".join([self._placeholder for nome in nomes])
        ns: list[str] = [nome.valor for nome in nomes]
        sql: str = f"SELECT pk_categoria, nome FROM categoria WHERE nome IN ({wildcards}) ORDER BY pk_categoria"
        self._connection.execute(sql, ns)
        return self._connection.fetchall_class(DadosCategoria)

    @override
    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        sql: str = f"INSERT INTO categoria (nome) VALUES ({self._placeholder})"
        self._connection.execute(sql, [dados.nome])
        return CategoriaPK(self._connection.asserted_lastrowid)

    @override
    def salvar_com_pk(self, dados: DadosCategoria) -> bool:
        sql: str = f"UPDATE categoria SET pk_categoria = {self._placeholder}, nome = {self._placeholder} WHERE pk_categoria = {self._placeholder}"
        self._connection.execute(sql, [dados.pk_categoria, dados.nome, dados.pk_categoria])
        return self._connection.rowcount > 0

    @override
    def deletar_por_pk(self, pk: CategoriaPK) -> bool:
        sql: str = f"DELETE FROM categoria WHERE pk_categoria = {self._placeholder}"
        self._connection.execute(sql, [pk.pk_categoria])
        return self._connection.rowcount > 0

    # Métodos auxiliares

    @override
    def buscar_por_nome(self, nome: NomeCategoria) -> DadosCategoria | None:
        sql: str = f"SELECT pk_categoria, nome FROM categoria WHERE nome = {self._placeholder}"
        self._connection.execute(sql, [nome.valor])
        return self._connection.fetchone_class(DadosCategoria)

    #def deletar_por_nome(self, nome: NomeCategoria) -> bool:
    #    sql: str = f"DELETE categoria WHERE nome = {self._placeholder}"
    #    self._connection.execute(sql, [nome.valor])
    #    return self._connection.rowcount > 0

    # Métodos com joins em outras tabelas

    @override
    def listar_por_segredo(self, pk: SegredoPK) -> list[DadosCategoria]:
        sql: str = "" \
            + "SELECT c.pk_categoria, c.nome " \
            + "FROM categoria c " \
            + "INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria " \
            + f"WHERE cs.pfk_segredo = {self._placeholder} " \
            + "ORDER BY c.pk_categoria"
        self._connection.execute(sql, [pk.pk_segredo])
        return self._connection.fetchall_class(DadosCategoria)