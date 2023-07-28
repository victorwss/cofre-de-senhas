from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.dao import SegredoDAO, SegredoPK, UsuarioPK, CategoriaPK, DadosSegredo, DadosSegredoSemPK, CampoDeSegredo, LoginComPermissao

class SegredoDAOImpl(SegredoDAO):

    def __init__(self) -> None:
        SegredoDAO.register(self)

    # CRUD básico

    def buscar_por_pk(self, pk: SegredoPK) -> DadosSegredo | None:
        Raiz.instance().execute("SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo = ?", [pk.pk_segredo])
        return Raiz.instance().fetchone_class(DadosSegredo)

    def listar(self) -> list[DadosSegredo]:
        Raiz.instance().execute("SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo")
        return Raiz.instance().fetchall_class(DadosSegredo)

    def criar(self, dados: DadosSegredoSemPK) -> SegredoPK:
        Raiz.instance().execute("INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES (?, ?, ?)", [dados.nome, dados.descricao, dados.fk_tipo_segredo])
        return SegredoPK(Raiz.instance().asserted_lastrowid)

    def salvar(self, dados: DadosSegredo) -> None:
        Raiz.instance().execute("UPDATE segredo SET nome = ?, descricao = ?, fk_tipo_segredo = ? WHERE pk_segredo = ?", [dados.nome, dados.descricao, dados.fk_tipo_segredo, dados.pk_segredo])

    def deletar_por_pk(self, pk: SegredoPK) -> None:
        # self.limpar_segredo(pk) # Desnecessário, pois deleta nas outras tabelas graças ao ON DELETE CASCADE.
        Raiz.instance().execute("DELETE FROM segredo WHERE pk_segredo = ?", [pk.pk_segredo])

    # Métodos auxiliares.

    def listar_visiveis(self, login: str) -> list[DadosSegredo]:
        Raiz.instance().execute("SELECT s.pk_segredo, s.nome, s.descricao, s.fk_tipo_segredo FROM segredo s INNER JOIN permissao p ON p.pfk_segredo = s.pk_segredo INNER JOIN usuario u ON p.pfk_usuario = u.pk_usuario WHERE u.login = ?", [login])
        return Raiz.instance().fetchall_class(DadosSegredo)

    def limpar_segredo(self, pk: SegredoPK) -> None:
        Raiz.instance().execute("DELETE FROM campo_segredo WHERE pfk_segredo = ?", [pk.pk_segredo])
        Raiz.instance().execute("DELETE FROM permissao WHERE pfk_segredo = ?", [pk.pk_segredo])
        Raiz.instance().execute("DELETE FROM categoria_segredo WHERE pfk_segredo = ?", [pk.pk_segredo])

    def buscar_por_pks(self, pks: list[SegredoPK]) -> list[DadosSegredo]:
        wildcards: str = ", ".join(["?" for pk in pks])
        Raiz.instance().execute(f"SELECT pk_segredo, nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo IN ({wildcards})", [pk.pk_segredo for pk in pks])
        return Raiz.instance().fetchall_class(DadosSegredo)

    #def buscar_por_nomes(self, nomes: list[nome]) -> list[DadosSegredo]:
    #    wildcards: str = ", ".join(["?" for pk in pks])
    #    Raiz.instance().execute(f"SELECT s.pk_segredo, s.nome, s.descricao, s.fk_tipo_segredo FROM segredo s INNER JOIN categoria_segredo cs ON s.pk_segredo = cs.pfk_segredo INNER JOIN categoria c ON c.categoria = cs.pfk_categoria WHERE nome IN ({wildcards})", nomes)
    #    return Raiz.instance().fetchall_class(DadosSegredo)

    # Categoria de segredo

    def criar_categoria_segredo(self, spk: SegredoPK, cpk: CategoriaPK) -> int:
        Raiz.instance().execute("INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (?, ?)", [spk.pk_segredo, cpk])
        return Raiz.instance().asserted_lastrowid

    # Campos

    def criar_campo_segredo(self, pk: SegredoPK, descricao: str, valor: str) -> int:
        Raiz.instance().execute("INSERT INTO campo_segredo (pfk_segredo, pk_descricao, valor) VALUES (?, ?, ?)", [pk.pk_segredo, descricao, valor])
        return Raiz.instance().asserted_lastrowid

    def ler_campos_segredo(self, pk: SegredoPK) -> list[CampoDeSegredo]:
        Raiz.instance().execute("SELECT pk_chave, valor FROM campo_segredo WHERE pfk_segredo = ?", [pk.pk_segredo])
        return Raiz.instance().fetchall_class(CampoDeSegredo)

    # Permissões

    def criar_permissao(self, upk: UsuarioPK, spk: SegredoPK, fk_tipo_permissao: int) -> int:
        Raiz.instance().execute("INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (?, ?, ?)", [upk, spk.pk_segredo, fk_tipo_permissao])
        return Raiz.instance().asserted_lastrowid

    def buscar_permissao(self, pk: SegredoPK, login: str) -> int | None:
        Raiz.instance().execute("SELECT p.fk_tipo_permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ? AND u.login = ?", [pk.pk_segredo, login])
        tupla = Raiz.instance().fetchone()
        if tupla is None: return None
        return int(tupla[0])

    def ler_login_com_permissoes(self, pk: SegredoPK) -> list[LoginComPermissao]:
        Raiz.instance().execute("SELECT u.login, p.fk_tipo_permissao AS permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ?", [pk.pk_segredo])
        return Raiz.instance().fetchall_class(LoginComPermissao)