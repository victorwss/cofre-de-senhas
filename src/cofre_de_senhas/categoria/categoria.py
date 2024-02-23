from typing import Self, TypeAlias
from validator import dataclass_validate
from dataclasses import dataclass, replace
from ..erro import (
    UsuarioBanidoException, PermissaoNegadaException, LoginExpiradoException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    ValorIncorretoException, ExclusaoSemCascataException
)
from ..dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoriaUK
from ..service import ChaveCategoria, CategoriaComChave, NomeCategoria, ChaveUsuario, RenomeCategoria, ResultadoListaDeCategorias
from ..usuario.usuario import Usuario


_UBE: TypeAlias = UsuarioBanidoException
_PNE: TypeAlias = PermissaoNegadaException
_UNEE: TypeAlias = UsuarioNaoExisteException
_UJEE: TypeAlias = UsuarioJaExisteException
_CNEE: TypeAlias = CategoriaNaoExisteException
_CJEE: TypeAlias = CategoriaJaExisteException
_VIE: TypeAlias = ValorIncorretoException
_LEE: TypeAlias = LoginExpiradoException
_ESCE: TypeAlias = ExclusaoSemCascataException


@dataclass_validate
@dataclass(frozen = True)
class Categoria:
    pk_categoria: int
    nome: str

    def __renomear(self, novo_nome: str) -> Self | _VIE | _CJEE:
        t: int = len(novo_nome)
        if t < 1 or t > 50:
            return ValorIncorretoException()
        c1: None | _CJEE = Categoria.__nao_existente_por_nome(novo_nome)
        if c1 is not None:
            return c1
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
    def __promote(dados: DadosCategoria) -> "Categoria":
        return Categoria(dados.pk_categoria, dados.nome)

    @staticmethod
    def __encontrar_por_chave(chave: ChaveCategoria) -> "Categoria | None":
        dados: DadosCategoria | None = CategoriaDAO.instance().buscar_por_pk(CategoriaPK(chave.valor))
        if dados is None:
            return None
        return Categoria.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_chave(chave: ChaveCategoria) -> "Categoria | _CNEE":
        encontrado: Categoria | None = Categoria.__encontrar_por_chave(chave)
        if encontrado is None:
            return CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def __encontrar_por_nome(nome: str) -> "Categoria | None":
        dados: DadosCategoria | None = CategoriaDAO.instance().buscar_por_nome(NomeCategoriaUK(nome))
        if dados is None:
            return None
        return Categoria.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_nome(nome: str) -> "Categoria | _CNEE":
        encontrado: Categoria | None = Categoria.__encontrar_por_nome(nome)
        if encontrado is None:
            return CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def __nao_existente_por_nome(nome: str) -> None | _CJEE:
        talvez: Categoria | None = Categoria.__encontrar_por_nome(nome)
        if talvez is not None:
            return CategoriaJaExisteException()
        return None

    @staticmethod
    def __listar_interno() -> list["Categoria"]:
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
    def listar_por_nomes(nomes: set[str]) -> dict[str, "Categoria"] | _CNEE:
        dl: list[NomeCategoriaUK] = NomeCategoriaUK.para_todos(nomes)
        dados: list[DadosCategoria] = CategoriaDAO.instance().listar_por_nomes(dl)
        r: dict[str, Categoria] = Categoria.__mapear_todos(dados)

        if len(r) != len(nomes):
            for nome in nomes:
                if nome not in r:
                    return CategoriaNaoExisteException(nome)

        return r

    def __ligados(self) -> int:
        return CategoriaDAO.instance().contar_segredos_por_pk(CategoriaPK(self.pk_categoria))

    @staticmethod
    def _buscar_por_nome(quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = Categoria.__encontrar_existente_por_nome(dados.nome)
        if not isinstance(c1, Categoria):
            return c1
        return c1.__up

    @staticmethod
    def _buscar_por_chave(quem_faz: ChaveUsuario, chave: ChaveCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = Categoria.__encontrar_existente_por_chave(chave)
        if not isinstance(c1, Categoria):
            return c1
        return c1.__up

    @staticmethod
    def _criar(quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _PNE | _CJEE | _VIE:
        u1: Usuario | _LEE | _UBE | _PNE = Usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        nome: str = dados.nome
        t: int = len(nome)
        if t < 1 or t > 50:
            return ValorIncorretoException()
        c1: None | _CJEE = Categoria.__nao_existente_por_nome(nome)
        if c1 is not None:
            return c1
        pk: CategoriaPK = CategoriaDAO.instance().criar(DadosCategoriaSemPK(nome))
        return Categoria(pk.pk_categoria, nome).__up

    @staticmethod
    def _renomear_por_nome(quem_faz: ChaveUsuario, dados: RenomeCategoria) -> None | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE:
        u1: Usuario | _LEE | _UBE | _PNE = Usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = Categoria.__encontrar_existente_por_nome(dados.antigo)
        if not isinstance(c1, Categoria):
            return c1
        c2: Categoria | _VIE | _CJEE = c1.__renomear(dados.novo)
        if not isinstance(c2, Categoria):
            return c2
        return None

    @staticmethod
    def _excluir_por_nome(quem_faz: ChaveUsuario, dados: NomeCategoria) -> None | _UBE | _PNE | _CNEE | _LEE | _ESCE:
        u1: Usuario | _LEE | _UBE | _PNE = Usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = Categoria.__encontrar_existente_por_nome(dados.nome)
        if not isinstance(c1, Categoria):
            return c1
        ligados: int = c1.__ligados()
        if ligados > 0:
            return ExclusaoSemCascataException()
        c1.__excluir()
        return None

    @staticmethod
    def _listar(quem_faz: ChaveUsuario) -> ResultadoListaDeCategorias | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return ResultadoListaDeCategorias([x.__up for x in Categoria.__listar_interno()])


class Servicos:

    def __init__(self) -> None:
        raise Exception()

    @staticmethod
    def buscar_por_nome(quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        return Categoria._buscar_por_nome(quem_faz, dados)

    @staticmethod
    def buscar_por_chave(quem_faz: ChaveUsuario, chave: ChaveCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        return Categoria._buscar_por_chave(quem_faz, chave)

    @staticmethod
    def criar(quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _PNE | _CJEE | _VIE:
        return Categoria._criar(quem_faz, dados)

    @staticmethod
    def renomear_por_nome(quem_faz: ChaveUsuario, dados: RenomeCategoria) -> None | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE:
        return Categoria._renomear_por_nome(quem_faz, dados)

    @staticmethod
    def excluir_por_nome(quem_faz: ChaveUsuario, dados: NomeCategoria) -> None | _UBE | _PNE | _CNEE | _LEE | _ESCE:
        return Categoria._excluir_por_nome(quem_faz, dados)

    @staticmethod
    def listar(quem_faz: ChaveUsuario) -> ResultadoListaDeCategorias | _LEE | _UBE:
        return Categoria._listar(quem_faz)
