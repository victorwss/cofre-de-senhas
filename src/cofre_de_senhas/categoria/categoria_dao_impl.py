from typing import override
from dataclasses import dataclass
from connection.trans import TransactedConnection
from ..dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoriaUK


@dataclass
class _IntHolder:
    conta: int


class CategoriaDAOImpl(CategoriaDAO):

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)

    # CRUD básico

    @override
    def buscar_por_pk(self, pk: CategoriaPK) -> DadosCategoria | None:
        sql: str = f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria = {self._placeholder}"
        return self._connection.execute(sql, [pk.pk_categoria]).fetchone_class(DadosCategoria)

    @override
    def listar_por_pks(self, pks: list[CategoriaPK]) -> list[DadosCategoria]:
        wildcards: str = ", ".join([self._placeholder for pk in pks])
        ns: list[int] = [pk.pk_categoria for pk in pks]
        sql = f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria IN ({wildcards}) ORDER BY pk_categoria"
        return self._connection.execute(sql, ns).fetchall_class(DadosCategoria)

    @override
    def listar(self) -> list[DadosCategoria]:
        sql: str = "SELECT c.pk_categoria, c.nome FROM categoria c ORDER BY pk_categoria"
        return self._connection.execute(sql).fetchall_class(DadosCategoria)

    def __listar_por_nomes_sql(self, quantidade: int) -> str:
        wildcards: str = ", ".join([self._placeholder for i in range(0, quantidade)])
        if self._database_type in ["MySQL", "MariaDB"]:
            return f"SELECT pk_categoria, nome FROM categoria WHERE BINARY nome IN ({wildcards}) ORDER BY pk_categoria"
        return f"SELECT pk_categoria, nome FROM categoria WHERE nome IN ({wildcards}) ORDER BY pk_categoria"

    @override
    def listar_por_nomes(self, nomes: list[NomeCategoriaUK]) -> list[DadosCategoria]:
        ns: list[str] = [nome.valor for nome in nomes]
        sql: str = self.__listar_por_nomes_sql(len(ns))
        return self._connection.execute(sql, ns).fetchall_class(DadosCategoria)

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

    def __buscar_por_nome_sql(self) -> str:
        if self._database_type in ["MySQL", "MariaDB"]:
            return f"SELECT pk_categoria, nome FROM categoria WHERE BINARY nome = {self._placeholder}"
        return f"SELECT pk_categoria, nome FROM categoria WHERE nome = {self._placeholder}"

    @override
    def buscar_por_nome(self, nome: NomeCategoriaUK) -> DadosCategoria | None:
        sql: str = self.__buscar_por_nome_sql()
        return self._connection.execute(sql, [nome.valor]).fetchone_class(DadosCategoria)

    @override
    def contar_segredos_por_pk(self, c: CategoriaPK) -> int:
        sql: str = f"SELECT COUNT(cs.pfk_categoria) AS conta FROM categoria_segredo cs WHERE cs.pfk_categoria = {self._placeholder}"
        r: _IntHolder | None = self._connection.execute(sql, [c.pk_categoria]).fetchone_class(_IntHolder)
        return 0 if r is None else r.conta

    # def deletar_por_nome(self, nome: NomeCategoria) -> bool:
    #     sql: str = f"DELETE categoria WHERE BINARY nome = {self._placeholder}"
    #     self._connection.execute(sql, [nome.valor])
    #     return self._connection.rowcount > 0

    # Métodos com joins em outras tabelas

    @override
    def listar_por_segredo(self, pk: SegredoPK) -> list[DadosCategoria]:
        sql: str = " ".join([
            "SELECT c.pk_categoria, c.nome",
            "FROM categoria c",
            "INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria",
            f"WHERE cs.pfk_segredo = {self._placeholder}",
            "ORDER BY c.pk_categoria"
        ])
        return self._connection.execute(sql, [pk.pk_segredo]).fetchall_class(DadosCategoria)
