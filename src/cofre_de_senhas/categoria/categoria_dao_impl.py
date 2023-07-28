from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK

class CategoriaDAOImpl(CategoriaDAO):

    def __init__(self) -> None:
        CategoriaDAO.register(self)

    # CRUD básico

    def buscar_por_pk(self, pk: CategoriaPK) -> DadosCategoria | None:
        Raiz.instance().execute("SELECT pk_categoria, nome FROM categoria WHERE pk_categoria = ?", [pk.pk_categoria])
        return Raiz.instance().fetchone_class(DadosCategoria)

    def buscar_por_pks(self, pks: list[CategoriaPK]) -> list[DadosCategoria]:
        wildcards: str = ", ".join(["?" for pk in pks])
        Raiz.instance().execute(f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria IN ({wildcards})", [pk.pk_categoria for pk in pks])
        return Raiz.instance().fetchall_class(DadosCategoria)

    def listar(self) -> list[DadosCategoria]:
        Raiz.instance().execute("SELECT c.pk_categoria, c.nome FROM categoria c")
        return Raiz.instance().fetchall_class(DadosCategoria)

    def listar_por_nomes(self, nomes: list[str]) -> list[DadosCategoria]:
        wildcards: str = ", ".join(["?" for nome in nomes])
        Raiz.instance().execute(f"SELECT pk_categoria, nome FROM categoria WHERE pk_categoria IN ({wildcards})", nomes)
        return Raiz.instance().fetchall_class(DadosCategoria)

    def criar(self, dados: DadosCategoriaSemPK) -> CategoriaPK:
        Raiz.instance().execute("INSERT INTO categoria (nome) VALUES (?)", [dados.nome])
        return CategoriaPK(Raiz.instance().asserted_lastrowid)

    def salvar(self, dados: DadosCategoria) -> None:
        sql = "UPDATE categoria SET pk_categoria = ?, nome = ? WHERE pk_categoria = ?"
        Raiz.instance().execute(sql, [dados.pk_categoria, dados.nome, dados.pk_categoria])

    def deletar_por_pk(self, pk: CategoriaPK) -> None:
        Raiz.instance().execute("DELETE categoria WHERE pk_categoria = ?", [pk.pk_categoria])

    # Métodos auxiliares

    def buscar_por_nome(self, nome: str) -> DadosCategoria | None:
        Raiz.instance().execute("SELECT pk_categoria, nome FROM categoria WHERE nome = ?", [nome])
        return Raiz.instance().fetchone_class(DadosCategoria)

    #def deletar_por_nome(self, nome: str) -> None:
    #    Raiz.instance().execute("DELETE categoria WHERE nome = ?", [nome])

    # Métodos com joins em outras tabelas

    def listar_por_segredo(self, pk: SegredoPK) -> list[DadosCategoria]:
        sql = "SELECT c.pk_categoria, c.nome FROM categoria c INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria WHERE cs.pfk_segredo = ?"
        Raiz.instance().execute(sql, [pk.pk_segredo])
        return Raiz.instance().fetchall_class(DadosCategoria)