from connection.conn import TransactedConnection
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK

class CategoriaDAOImpl(CategoriaDAO):

    def __init__(self, transacted_conn: TransactedConnection) -> None:
        self.__cf: TransactedConnection = transacted_conn

    # CRUD básico

    def buscar_por_pk(self, pk: CategoriaPK) -> DadosCategoria | None:
        self.__cf.execute("SELECT pk_categoria, nome FROM categoria WHERE pk_categoria = ?", [pk.pk_categoria])
        return self.__cf.fetchone_class(DadosCategoria)

    def listar(self) -> list[DadosCategoria]:
        self.__cf.execute("SELECT c.pk_categoria, c.nome FROM categoria c")
        return self.__cf.fetchall_class(DadosCategoria)

    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        self.__cf.execute("INSERT INTO categoria (nome) VALUES (?)", [dados.nome])
        return CategoriaPK(self.__cf.asserted_lastrowid)

    def salvar(self, dados: DadosCategoria) -> None:
        sql = "UPDATE categoria SET pk_categoria = ?, nome = ? WHERE pk_categoria = ?"
        self.__cf.execute(sql, [dados.pk_categoria, dados.nome, dados.pk_categoria])

    def deletar_por_pk(self, pk: CategoriaPK) -> None:
        self.__cf.execute("DELETE categoria WHERE pk_categoria = ?", [pk.pk_categoria])

    # Métodos auxiliares

    def buscar_por_nome(self, nome: str) -> DadosCategoria | None:
        self.__cf.execute("SELECT pk_categoria, nome FROM categoria WHERE nome = ?", [nome])
        return self.__cf.fetchone_class(DadosCategoria)

    #def deletar_por_nome(self, nome: str) -> None:
    #    self.__cf.execute("DELETE categoria WHERE nome = ?", [nome])

    # Métodos com joins em outras tabelas

    def listar_por_segredo(self, pk: SegredoPK) -> list[DadosCategoria]:
        sql = "SELECT c.pk_categoria, c.nome FROM categoria c INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria WHERE cs.pfk_segredo = ?"
        self.__cf.execute(sql, [pk.pk_segredo])
        return self.__cf.fetchall_class(DadosCategoria)