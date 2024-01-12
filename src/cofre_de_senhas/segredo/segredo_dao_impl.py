from typing import override
from connection.trans import TransactedConnection
from ..dao import (
    SegredoDAO, SegredoPK, DadosSegredo, DadosSegredoSemPK, CampoDeSegredo,
    LoginUsuarioUK, CategoriaDeSegredo, PermissaoDeSegredo, BuscaPermissaoPorLogin
)


class SegredoDAOImpl(SegredoDAO):

    def __init__(self, con: TransactedConnection) -> None:
        super().__init__(con)

    # CRUD básico

    @override
    def buscar_por_pk(self, pk: SegredoPK) -> DadosSegredo | None:
        sql: str = f"SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo = {self._placeholder}"
        return self._connection.execute(sql, [pk.pk_segredo]).fetchone_class(DadosSegredo)

    @override
    def listar(self) -> list[DadosSegredo]:
        sql: str = "SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo ORDER BY pk_segredo"
        return self._connection.execute(sql).fetchall_class(DadosSegredo)

    @override
    def criar(self, dados: DadosSegredoSemPK) -> SegredoPK:
        sql: str = f"INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES ({self._placeholder}, {self._placeholder}, {self._placeholder})"
        self._connection.execute(sql, [dados.nome, dados.descricao, dados.fk_tipo_segredo])
        return SegredoPK(self._connection.asserted_lastrowid)

    @override
    def salvar_com_pk(self, dados: DadosSegredo) -> bool:
        sql: str = " ".join([
            "UPDATE segredo SET",
            f"pk_segredo = {self._placeholder},",
            f"nome = {self._placeholder},",
            f"descricao = {self._placeholder},",
            f"fk_tipo_segredo = {self._placeholder}",
            f"WHERE pk_segredo = {self._placeholder}"
        ])
        self._connection.execute(sql, [dados.pk_segredo, dados.nome, dados.descricao, dados.fk_tipo_segredo, dados.pk_segredo])
        return self._connection.rowcount > 0

    @override
    def deletar_por_pk(self, pk: SegredoPK) -> bool:
        # self.limpar_segredo(pk) # Desnecessário, pois deleta nas outras tabelas graças ao ON DELETE CASCADE.
        sql: str = f"DELETE FROM segredo WHERE pk_segredo = {self._placeholder}"
        self._connection.execute(sql, [pk.pk_segredo])
        return self._connection.rowcount > 0

    # Métodos auxiliares.

    @override
    def listar_visiveis(self, login: LoginUsuarioUK) -> list[DadosSegredo]:
        sql: str = " ".join([
            "SELECT s.pk_segredo, s.nome, s.descricao, s.fk_tipo_segredo",
            "FROM segredo s",
            "INNER JOIN permissao p ON p.pfk_segredo = s.pk_segredo",
            "INNER JOIN usuario u ON p.pfk_usuario = u.pk_usuario",
            f"WHERE u.login = {self._placeholder} AND u.fk_nivel_acesso IN (1, 2)",
            "UNION",
            "SELECT p.pk_segredo, p.nome, p.descricao, p.fk_tipo_segredo",
            "FROM segredo p",
            "WHERE p.fk_tipo_segredo IN (1, 2)",
            "ORDER BY pk_segredo"
        ])
        return self._connection.execute(sql, [login.valor]).fetchall_class(DadosSegredo)

    # TESTAR
    @override
    def limpar_segredo(self, pk: SegredoPK) -> None:
        sql1: str = f"DELETE FROM campo_segredo WHERE pfk_segredo = {self._placeholder}"
        sql2: str = f"DELETE FROM permissao WHERE pfk_segredo = {self._placeholder}"
        sql3: str = f"DELETE FROM categoria_segredo WHERE pfk_segredo = {self._placeholder}"
        self._connection.execute(sql1, [pk.pk_segredo]).execute(sql2, [pk.pk_segredo]).execute(sql3, [pk.pk_segredo])

    @override
    def listar_por_pks(self, pks: list[SegredoPK]) -> list[DadosSegredo]:
        wildcards: str = ", ".join([self._placeholder for pk in pks])
        sql: str = f"SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo IN ({wildcards}) ORDER BY pk_segredo"
        return self._connection.execute(sql, [pk.pk_segredo for pk in pks]).fetchall_class(DadosSegredo)

    # def buscar_por_nomes(self, nomes: list[nome]) -> list[DadosSegredo]:
    #     wildcards: str = ", ".join([self._placeholder for pk in pks])
    #     sql: str = " ".join([
    #         "SELECT s.pk_segredo, s.nome, s.descricao, s.fk_tipo_segredo",
    #         "FROM segredo s",
    #         "INNER JOIN categoria_segredo cs ON s.pk_segredo = cs.pfk_segredo",
    #         "INNER JOIN categoria c ON c.categoria = cs.pfk_categoria",
    #         f"WHERE nome IN ({wildcards})"
    #     ])
    #     self._connection.execute(sql, nomes)
    #     return self._connection.fetchall_class(DadosSegredo)

    # Categoria de segredo

    @override
    def criar_categoria_segredo(self, c: CategoriaDeSegredo) -> bool:
        sql: str = f"INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES ({self._placeholder}, {self._placeholder})"
        self._connection.execute(sql, [c.pk_segredo, c.pk_categoria])
        return self._connection.rowcount > 0

    # Campos

    @override
    def criar_campo_segredo(self, campo: CampoDeSegredo) -> bool:
        sql: str = f"INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES ({self._placeholder}, {self._placeholder}, {self._placeholder})"
        self._connection.execute(sql, [campo.pfk_segredo, campo.pk_nome, campo.valor])
        return self._connection.rowcount > 0

    @override
    def ler_campos_segredo(self, pk: SegredoPK) -> list[CampoDeSegredo]:
        sql: str = f"SELECT pfk_segredo, pk_nome, valor FROM campo_segredo WHERE pfk_segredo = {self._placeholder} ORDER BY pk_nome"
        return self._connection.execute(sql, [pk.pk_segredo]).fetchall_class(CampoDeSegredo)

    # Permissões

    @override
    def criar_permissao(self, permissao: PermissaoDeSegredo) -> bool:
        sql: str = f"INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES ({self._placeholder}, {self._placeholder}, {self._placeholder})"
        self._connection.execute(sql, [permissao.pfk_usuario, permissao.pfk_segredo, permissao.fk_tipo_permissao])
        return self._connection.rowcount > 0

    @override
    def buscar_permissao(self, busca: BuscaPermissaoPorLogin) -> PermissaoDeSegredo | None:
        sql: str = " ".join([
            "SELECT p.pfk_usuario, p.pfk_segredo, p.fk_tipo_permissao",
            "FROM permissao p",
            "INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario",
            f"WHERE p.pfk_segredo = {self._placeholder} AND u.login = {self._placeholder}"
        ])
        return self._connection.execute(sql, [busca.pfk_segredo, busca.login]).fetchone_class(PermissaoDeSegredo)
