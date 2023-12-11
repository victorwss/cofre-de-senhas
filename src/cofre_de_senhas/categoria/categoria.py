from typing import Self, TypeGuard
from validator import dataclass_validate
from dataclasses import dataclass, replace
from ..erro import *
from ..dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoria as NomeCategoriaDAO
from ..service import *
from ..usuario.usuario import Usuario, Permissao


@dataclass_validate
@dataclass(frozen = True)
class Categoria:
    pk_categoria: int
    nome: str

    def __renomear(self, novo_nome: str) -> Self:
        Categoria.__nao_existente_por_nome(novo_nome)
        return replace(self, nome = novo_nome).__salvar()

    def __excluir(self) -> Self:
        CategoriaDAO.instance().deletar_por_pk(self.pk)
        return self

    def __salvar(self) -> Self:
        CategoriaDAO.instance().salvar_com_pk(self.__down)
        return self

    @property
    def __chave(self) -> ChaveCategoria:
        return ChaveCategoria(self.pk_categoria)

    # Exportado para a classe Segredo.
    @property
    def pk(self) -> CategoriaPK:
        return CategoriaPK(self.pk_categoria)

    @property
    def __up(self) -> CategoriaComChave:
        return CategoriaComChave(self.__chave, self.nome)

    @property
    def __down(self) -> DadosCategoria:
        return DadosCategoria(self.pk_categoria, self.nome)

    # Métodos estáticos de fábrica.

    @staticmethod
    def servicos() -> "Categoria.Servico":
        return Categoria.Servico.instance()

    @staticmethod
    def __promote(dados: DadosCategoria) -> "Categoria":
        return Categoria(dados.pk_categoria, dados.nome)

    @staticmethod
    def __encontrar_por_chave(chave: ChaveCategoria) -> "Categoria | None":
        dados: DadosCategoria | None = CategoriaDAO.instance().buscar_por_pk(CategoriaPK(chave.valor))
        if dados is None: return None
        return Categoria.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_chave(chave: ChaveCategoria) -> "Categoria":
        encontrado: Categoria | None = Categoria.__encontrar_por_chave(chave)
        if encontrado is None: raise CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def __encontrar_por_nome(nome: str) -> "Categoria | None":
        dados: DadosCategoria | None = CategoriaDAO.instance().buscar_por_nome(NomeCategoriaDAO(nome))
        if dados is None: return None
        return Categoria.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_nome(nome: str) -> "Categoria":
        encontrado: Categoria | None = Categoria.__encontrar_por_nome(nome)
        if encontrado is None: raise CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def __nao_existente_por_nome(nome: str) -> None:
        talvez: Categoria | None = Categoria.__encontrar_por_nome(nome)
        if talvez is not None: raise CategoriaJaExisteException()

    @staticmethod
    def __criar(nome: str) -> "Categoria":
        Categoria.__nao_existente_por_nome(nome)
        pk: CategoriaPK = CategoriaDAO.instance().criar(DadosCategoriaSemPK(nome))
        return Categoria(pk.pk_categoria, nome)

    @staticmethod
    def __listar() -> list["Categoria"]:
        return [Categoria.__promote(c) for c in CategoriaDAO.instance().listar()]

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_segredo(pk: SegredoPK) -> dict[str, "Categoria"]:
        return {c.nome: Categoria.__promote(c) for c in CategoriaDAO.instance().listar_por_segredo(pk)}

    @staticmethod
    def __mapear_todos(dados: list[DadosCategoria]) -> dict[str, "Categoria"]:
        return {c.nome: Categoria.__promote(c) for c in dados}

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_nomes(nomes: set[str]) -> dict[str, "Categoria"]:
        dl: list[NomeCategoriaDAO] = NomeCategoriaDAO.para_todos(nomes)
        dados: list[DadosCategoria] = CategoriaDAO.instance().listar_por_nomes(dl)
        r: dict[str, Categoria] = Categoria.__mapear_todos(dados)

        if len(r) != len(nomes):
            for nome in nomes:
                if nome not in r: raise CategoriaNaoExisteException(nome)

        return r


    class Servico:

        __me: "Categoria.Servico | None" = None

        def __init__(self) -> None:
            if Categoria.Servico.__me: raise Exception()

        @staticmethod
        def instance() -> "Categoria.Servico":
            if not Categoria.Servico.__me:
                Categoria.Servico.__me = Categoria.Servico()
            return Categoria.Servico.__me

        def buscar_por_nome(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            return Categoria.__encontrar_existente_por_nome(dados.nome).__up

        def buscar_por_chave(self, quem_faz: ChaveUsuario, chave: ChaveCategoria) -> CategoriaComChave:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            return Categoria.__encontrar_existente_por_chave(chave).__up

        def criar(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave:
            quem_eh: Usuario = Usuario.verificar_acesso_admin(quem_faz)
            return Categoria.__criar(dados.nome).__up

        def renomear_por_nome(self, quem_faz: ChaveUsuario, dados: RenomeCategoria) -> None:
            quem_eh: Usuario = Usuario.verificar_acesso_admin(quem_faz)
            Categoria.__encontrar_existente_por_nome(dados.antigo).__renomear(dados.novo)

        def excluir_por_nome(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> None:
            quem_eh: Usuario = Usuario.verificar_acesso_admin(quem_faz)
            Categoria.__encontrar_existente_por_nome(dados.nome).__excluir()

        def listar(self, quem_faz: ChaveUsuario) -> ResultadoListaDeCategorias:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            return ResultadoListaDeCategorias([x.__up for x in Categoria.__listar()])