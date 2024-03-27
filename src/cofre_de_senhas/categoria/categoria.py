from typing import TypeAlias
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
from ..usuario.usuario import Usuario, ServicosImpl as ServicosUsuarioImpl


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

    @property
    def __chave(self) -> ChaveCategoria:
        return ChaveCategoria(self.pk_categoria)

    # Exportado para a classe Segredo.
    @property
    def pk(self) -> CategoriaPK:
        return CategoriaPK(self.pk_categoria)

    @property
    def _up(self) -> CategoriaComChave:
        return CategoriaComChave(self.__chave, self.nome)

    @property
    def _down(self) -> DadosCategoria:
        return DadosCategoria(self.pk_categoria, self.nome)

    # Métodos estáticos de fábrica.

    @staticmethod
    def _promote(dados: DadosCategoria) -> "Categoria":
        return Categoria(dados.pk_categoria, dados.nome)

    @staticmethod
    def _mapear_todos(dados: list[DadosCategoria]) -> dict[str, "Categoria"]:
        return {c.nome: Categoria._promote(c) for c in dados}


class ServicosImpl:

    def __init__(self, dao: CategoriaDAO, servicos_usuario: ServicosUsuarioImpl) -> None:
        self.__dao: CategoriaDAO = dao
        self.__servicos_usuario: ServicosUsuarioImpl = servicos_usuario

    def __renomear(self, c0: Categoria, novo_nome: str) -> Categoria | _VIE | _CJEE:
        t: int = len(novo_nome)
        if not (2 <= t <= 50):
            return ValorIncorretoException()
        c1: None | _CJEE = self.__nao_existente_por_nome(novo_nome)
        if c1 is not None:
            return c1
        return self.__salvar(replace(c0, nome = novo_nome))

    def __excluir(self, c1: Categoria) -> Categoria:
        self.__dao.deletar_por_pk(c1.pk)
        return c1

    def __salvar(self, c1: Categoria) -> Categoria:
        self.__dao.salvar_com_pk(c1._down)
        return c1

    def __encontrar_por_chave(self, chave: ChaveCategoria) -> Categoria | None:
        dados: DadosCategoria | None = self.__dao.buscar_por_pk(CategoriaPK(chave.valor))
        if dados is None:
            return None
        return Categoria._promote(dados)

    def __encontrar_existente_por_chave(self, chave: ChaveCategoria) -> Categoria | _CNEE:
        encontrado: Categoria | None = self.__encontrar_por_chave(chave)
        if encontrado is None:
            return CategoriaNaoExisteException()
        return encontrado

    def __encontrar_por_nome(self, nome: str) -> Categoria | None:
        dados: DadosCategoria | None = self.__dao.buscar_por_nome(NomeCategoriaUK(nome))
        if dados is None:
            return None
        return Categoria._promote(dados)

    def __encontrar_existente_por_nome(self, nome: str) -> Categoria | _CNEE:
        encontrado: Categoria | None = self.__encontrar_por_nome(nome)
        if encontrado is None:
            return CategoriaNaoExisteException()
        return encontrado

    def __nao_existente_por_nome(self, nome: str) -> None | _CJEE:
        talvez: Categoria | None = self.__encontrar_por_nome(nome)
        if talvez is not None:
            return CategoriaJaExisteException()
        return None

    def __listar_interno(self) -> list[Categoria]:
        return [Categoria._promote(c) for c in self.__dao.listar()]

    # Exportado para a classe Segredo.
    def listar_por_segredo(self, pk: SegredoPK) -> dict[str, Categoria]:
        return {c.nome: Categoria._promote(c) for c in self.__dao.listar_por_segredo(pk)}

    # Exportado para a classe Segredo.
    def listar_por_nomes(self, nomes: set[str]) -> dict[str, Categoria] | _CNEE:
        dl: list[NomeCategoriaUK] = NomeCategoriaUK.para_todos(list(nomes))
        dados: list[DadosCategoria] = self.__dao.listar_por_nomes(dl)
        r: dict[str, Categoria] = Categoria._mapear_todos(dados)

        if len(r) != len(nomes):
            for nome in nomes:
                if nome not in r:
                    return CategoriaNaoExisteException(nome)
            assert False, "A exceção CategoriaNaoExisteException deveria ter sido lançada."

        return r

    def __ligados(self, c: Categoria) -> int:
        return self.__dao.contar_segredos_por_pk(CategoriaPK(c.pk_categoria))

    def __buscar_por_nome(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = self.__encontrar_existente_por_nome(dados.nome)
        if not isinstance(c1, Categoria):
            return c1
        return c1._up

    def __buscar_por_chave(self, quem_faz: ChaveUsuario, chave: ChaveCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = self.__encontrar_existente_por_chave(chave)
        if not isinstance(c1, Categoria):
            return c1
        return c1._up

    def __criar(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _PNE | _CJEE | _VIE:
        u1: Usuario | _LEE | _UBE | _PNE = self.__servicos_usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        nome: str = dados.nome
        t: int = len(nome)
        if not (2 <= t <= 50):
            return ValorIncorretoException()
        c1: None | _CJEE = self.__nao_existente_por_nome(nome)
        if c1 is not None:
            return c1
        pk: CategoriaPK = self.__dao.criar(DadosCategoriaSemPK(nome))
        return Categoria(pk.pk_categoria, nome)._up

    def __renomear_por_nome(self, quem_faz: ChaveUsuario, dados: RenomeCategoria) -> None | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE:
        u1: Usuario | _LEE | _UBE | _PNE = self.__servicos_usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = self.__encontrar_existente_por_nome(dados.antigo)
        if not isinstance(c1, Categoria):
            return c1
        c2: Categoria | _VIE | _CJEE = self.__renomear(c1, dados.novo)
        if not isinstance(c2, Categoria):
            return c2
        return None

    def __excluir_por_nome(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> None | _UBE | _PNE | _CNEE | _LEE | _ESCE:
        u1: Usuario | _LEE | _UBE | _PNE = self.__servicos_usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        c1: Categoria | _CNEE = self.__encontrar_existente_por_nome(dados.nome)
        if not isinstance(c1, Categoria):
            return c1
        ligados: int = self.__ligados(c1)
        if ligados > 0:
            return ExclusaoSemCascataException()
        self.__excluir(c1)
        return None

    def __listar(self, quem_faz: ChaveUsuario) -> ResultadoListaDeCategorias | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return ResultadoListaDeCategorias([x._up for x in self.__listar_interno()])

    def buscar_por_nome(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        return self.__buscar_por_nome(quem_faz, dados)

    def buscar_por_chave(self, quem_faz: ChaveUsuario, chave: ChaveCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:
        return self.__buscar_por_chave(quem_faz, chave)

    def criar(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _PNE | _CJEE | _VIE:
        return self.__criar(quem_faz, dados)

    def renomear_por_nome(self, quem_faz: ChaveUsuario, dados: RenomeCategoria) -> None | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE:
        return self.__renomear_por_nome(quem_faz, dados)

    def excluir_por_nome(self, quem_faz: ChaveUsuario, dados: NomeCategoria) -> None | _UBE | _PNE | _CNEE | _LEE | _ESCE:
        return self.__excluir_por_nome(quem_faz, dados)

    def listar(self, quem_faz: ChaveUsuario) -> ResultadoListaDeCategorias | _LEE | _UBE:
        return self.__listar(quem_faz)
