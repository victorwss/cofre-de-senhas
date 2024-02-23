from typing import Self, TypeAlias
from validator import dataclass_validate
from dataclasses import dataclass, replace
from ..dao import (
    SegredoDAO, SegredoPK, DadosSegredo, DadosSegredoSemPK,
    LoginUsuarioUK, BuscaPermissaoPorLogin,
    CategoriaDeSegredo, CampoDeSegredo, PermissaoDeSegredo
)
from ..erro import (
    UsuarioBanidoException, PermissaoNegadaException, LoginExpiradoException,
    UsuarioNaoExisteException,
    SegredoNaoExisteException,
    CategoriaNaoExisteException,
    ValorIncorretoException
)
from ..service import (
    TipoPermissao, TipoSegredo, ChaveUsuario,
    SegredoComChave, SegredoSemChave, CabecalhoSegredoComChave, ChaveSegredo,
    PesquisaSegredos, ResultadoPesquisaDeSegredos
)
from ..usuario.usuario import Usuario, Permissao
from ..categoria.categoria import Categoria


_UBE: TypeAlias = UsuarioBanidoException
_PNE: TypeAlias = PermissaoNegadaException
_UNEE: TypeAlias = UsuarioNaoExisteException
_SNEE: TypeAlias = SegredoNaoExisteException
_CNEE: TypeAlias = CategoriaNaoExisteException
_LEE: TypeAlias = LoginExpiradoException
_VIE: TypeAlias = ValorIncorretoException


@dataclass_validate
@dataclass(frozen = True)
class Segredo:
    cabecalho: "Segredo.Cabecalho"
    usuarios: dict[str, Permissao]
    categorias: dict[str, Categoria]
    campos: dict[str, str]

    @dataclass_validate
    @dataclass(frozen = True)
    class Cabecalho:
        pk_segredo: int
        nome: str
        descricao: str
        tipo_segredo: TipoSegredo

        # Exportado para a classe Usuario.
        @property
        def pk(self) -> SegredoPK:
            return SegredoPK(self.pk_segredo)

        @property
        def _up(self) -> CabecalhoSegredoComChave:
            return CabecalhoSegredoComChave(ChaveSegredo(self.pk_segredo), self.nome, self.descricao, self.tipo_segredo)

        @property
        def _down(self) -> DadosSegredo:
            return DadosSegredo(self.pk_segredo, self.nome, self.descricao, self.tipo_segredo.value)

        @staticmethod
        def _promote(dados: DadosSegredo) -> "Segredo.Cabecalho":
            return Segredo.Cabecalho(dados.pk_segredo, dados.nome, dados.descricao, TipoSegredo(dados.fk_tipo_segredo))

    def __salvar(self) -> Self:
        SegredoDAO.instance().salvar_com_pk(self.__down)
        return self.__salvar_dados_internos()

    def __limpar(self) -> None:
        spk: SegredoPK = self.__pk
        SegredoDAO.instance().limpar_segredo(spk)

    def __criar_campos(self) -> None:
        spk: SegredoPK = self.__pk
        for descricao in self.campos.keys():
            valor: str = self.campos[descricao]
            SegredoDAO.instance().criar_campo_segredo(CampoDeSegredo(spk.pk_segredo, descricao, valor))

    def __criar_permissoes(self) -> None:
        spk: SegredoPK = self.__pk
        for permissao in self.usuarios.values():
            SegredoDAO.instance().criar_permissao(PermissaoDeSegredo(permissao.usuario.pk.pk_usuario, spk.pk_segredo, permissao.tipo.value))

    def __criar_categorias(self) -> None:
        spk: SegredoPK = self.__pk
        for categoria in self.categorias.values():
            SegredoDAO.instance().criar_categoria_segredo(CategoriaDeSegredo(spk.pk_segredo, categoria.pk.pk_categoria))

    def __salvar_dados_internos(self) -> Self:
        assert self.usuarios is not None
        assert self.categorias is not None
        assert self.campos is not None

        self.__limpar()
        self.__criar_campos()
        self.__criar_permissoes()
        self.__criar_categorias()

        return self

    @staticmethod
    def _alterar(quem_faz: ChaveUsuario, dados: SegredoComChave) -> None | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE | _VIE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        s1: Segredo | _SNEE = Segredo.__encontrar_existente_por_chave(dados.chave)
        if not isinstance(s1, Segredo):
            return s1
        p1: None | _PNE | _SNEE = s1.__permitir_escrita_para(u1, False)
        if p1 is not None:
            return p1

        up: SegredoComChave = s1.__up_eager
        antes: dict[str, TipoPermissao] = up.usuarios
        depois: dict[str, TipoPermissao] = dados.usuarios
        era_proprietario: bool = Segredo.__tem_permissao(u1, up.sem_chave, True)
        sera_proprietario: bool = Segredo.__tem_permissao(u1, dados.sem_chave, True)

        if era_proprietario and not sera_proprietario:
            return ValorIncorretoException()

        if not era_proprietario and antes != depois:
            return PermissaoNegadaException()

        permissoes: dict[str, Permissao] | _UNEE = Segredo.__mapear_permissoes(dados.usuarios)
        if isinstance(permissoes, _UNEE):
            return permissoes
        categorias: dict[str, Categoria] | _CNEE = Categoria.listar_por_nomes(dados.categorias)
        if isinstance(categorias, _CNEE):
            return categorias
        c: Segredo.Cabecalho = replace(s1.cabecalho, nome = dados.nome, descricao = dados.descricao, tipo_segredo = dados.tipo)
        replace(s1, cabecalho = c, campos = dados.campos, categorias = categorias, usuarios = permissoes).__salvar()
        return None

    # @property
    # def __chave(self) -> ChaveSegredo:
    #     return ChaveSegredo(self.pk_segredo)

    @property
    def __pk(self) -> SegredoPK:
        return self.cabecalho.pk

    @property
    def __up(self) -> CabecalhoSegredoComChave:
        return self.cabecalho._up

    @property
    def __up_eager(self) -> SegredoComChave:
        permissoes: dict[str, TipoPermissao] = {} if self.usuarios is None else {k: self.usuarios[k].tipo for k in self.usuarios.keys()}
        return self.__up.com_corpo(self.campos, set(self.categorias.keys()), permissoes)

    @property
    def __down(self) -> DadosSegredo:
        return self.cabecalho._down

    def __permitir_escrita_para(self, acesso: Usuario, somente_proprietario: bool) -> None | _PNE | _SNEE:
        if acesso.is_admin:
            return None

        busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(self.__pk.pk_segredo, acesso.login)
        permissao_encontrada: PermissaoDeSegredo | None = SegredoDAO.instance().buscar_permissao(busca)
        if permissao_encontrada is None:
            if self.cabecalho.tipo_segredo == TipoSegredo.CONFIDENCIAL:
                return SegredoNaoExisteException()
            return PermissaoNegadaException()

        permissao: TipoPermissao = TipoPermissao(permissao_encontrada.fk_tipo_permissao)

        aceitaveis: list[TipoPermissao] = [TipoPermissao.PROPRIETARIO]
        if not somente_proprietario:
            aceitaveis.append(TipoPermissao.LEITURA_E_ESCRITA)
        if permissao not in aceitaveis:
            return PermissaoNegadaException()

        return None

    # Métodos internos

    @staticmethod
    def __mapear_permissoes(usuarios: dict[str, TipoPermissao]) -> dict[str, Permissao] | _UNEE:
        todos_usuarios: dict[str, Usuario] | _UNEE = Usuario.listar_por_logins(set(usuarios.keys()))
        if isinstance(todos_usuarios, _UNEE):
            return todos_usuarios

        permissoes: dict[str, Permissao] = {}

        for k in usuarios:
            if k not in todos_usuarios:
                return UsuarioNaoExisteException()
            permissoes[k] = Permissao(todos_usuarios[k], usuarios[k])

        return permissoes

    # Métodos estáticos de fábrica.

    @staticmethod
    def __encontrar_por_chave(chave: ChaveSegredo) -> "Segredo | None":
        dados: DadosSegredo | None = SegredoDAO.instance().buscar_por_pk(SegredoPK(chave.valor))
        if dados is None:
            return None
        cabecalho: Segredo.Cabecalho = Segredo.Cabecalho._promote(dados)
        spk: SegredoPK = cabecalho.pk
        campos: dict[str, str] = {c.pk_nome: c.valor for c in SegredoDAO.instance().ler_campos_segredo(spk)}
        usuarios: dict[str, Permissao] = Usuario.listar_por_permissao(cabecalho)
        categorias: dict[str, Categoria] = Categoria.listar_por_segredo(spk)
        return Segredo(cabecalho, usuarios, categorias, campos)

    @staticmethod
    def __encontrar_existente_por_chave(chave: ChaveSegredo) -> "Segredo | _SNEE":
        encontrado: Segredo | None = Segredo.__encontrar_por_chave(chave)
        if encontrado is None:
            return SegredoNaoExisteException()
        return encontrado

    # Métodos estáticos de fábrica.

    @staticmethod
    def __tem_permissao(u1: Usuario, dados: SegredoSemChave, proprietario: bool) -> bool:
        possibilidades: list[TipoPermissao] = [TipoPermissao.PROPRIETARIO]
        if not proprietario:
            possibilidades.append(TipoPermissao.LEITURA_E_ESCRITA)
            possibilidades.append(TipoPermissao.SOMENTE_LEITURA)
        return u1.is_admin or (u1.login in dados.usuarios and dados.usuarios[u1.login] in possibilidades)

    @staticmethod
    def _criar(quem_faz: ChaveUsuario, dados: SegredoSemChave) -> SegredoComChave | _UNEE | _CNEE | _UBE | _LEE | _VIE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        if not Segredo.__tem_permissao(u1, dados, True):
            return ValorIncorretoException()

        permissoes: dict[str, Permissao] | _UNEE = Segredo.__mapear_permissoes(dados.usuarios)
        if isinstance(permissoes, _UNEE):
            return permissoes
        categorias: dict[str, Categoria] | _CNEE = Categoria.listar_por_nomes(dados.categorias)
        if isinstance(categorias, _CNEE):
            return categorias

        rowid: SegredoPK = SegredoDAO.instance().criar(DadosSegredoSemPK(dados.nome, dados.descricao, dados.tipo.value))
        cabecalho: Segredo.Cabecalho = Segredo.Cabecalho(rowid.pk_segredo, dados.nome, dados.descricao, dados.tipo)
        return Segredo(cabecalho, permissoes, categorias, dados.campos).__salvar_dados_internos().__up_eager

    @staticmethod
    def __listar_todos() -> list["Segredo.Cabecalho"]:
        return [Segredo.Cabecalho._promote(s) for s in SegredoDAO.instance().listar()]

    @staticmethod
    def __listar_visiveis(quem_faz: Usuario) -> list["Segredo.Cabecalho"]:
        return [Segredo.Cabecalho._promote(s) for s in SegredoDAO.instance().listar_visiveis(LoginUsuarioUK(quem_faz.login))]

    @staticmethod
    def _listar(quem_faz: ChaveUsuario) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return ResultadoPesquisaDeSegredos([x._up for x in Segredo.__listar_interno(u1)])

    @staticmethod
    def __listar_interno(quem_faz: Usuario) -> list["Segredo.Cabecalho"]:
        if quem_faz.is_admin:
            return Segredo.__listar_todos()
        return Segredo.__listar_visiveis(quem_faz)

    @staticmethod
    def _buscar(quem_faz: ChaveUsuario, chave: ChaveSegredo) -> SegredoComChave | _LEE | _UBE | _SNEE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1

        com_chave: SegredoComChave | _SNEE = Segredo._buscar_sem_logar(chave)
        if not isinstance(com_chave, SegredoComChave):
            return com_chave

        pode_ver: bool = Segredo.__tem_permissao(u1, com_chave.sem_chave, False)

        if com_chave.tipo == TipoSegredo.CONFIDENCIAL and not pode_ver:
            return SegredoNaoExisteException()
        if com_chave.tipo == TipoSegredo.ENCONTRAVEL and not pode_ver:
            return com_chave.limpar_campos
        return com_chave

    @staticmethod
    def _buscar_sem_logar(chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        s1: Segredo | _SNEE = Segredo.__encontrar_existente_por_chave(chave)
        if not isinstance(s1, Segredo):
            return s1
        return s1.__up_eager

    @staticmethod
    def _excluir_por_chave(quem_faz: ChaveUsuario, dados: ChaveSegredo) -> None | _LEE | _UBE | _PNE | _SNEE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        s1: Segredo | _SNEE = Segredo.__encontrar_existente_por_chave(dados)
        if not isinstance(s1, Segredo):
            return s1
        p1: None | _PNE | _SNEE = s1.__permitir_escrita_para(u1, True)
        if p1 is not None:
            return p1
        SegredoDAO.instance().deletar_por_pk(s1.cabecalho.pk)
        return None

    @staticmethod
    def _pesquisar(quem_faz: ChaveUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        raise NotImplementedError()


class Servicos:

    def __init__(self) -> None:
        raise Exception()

    @staticmethod
    def criar(quem_faz: ChaveUsuario, dados: SegredoSemChave) -> SegredoComChave | _UNEE | _CNEE | _UBE | _LEE | _VIE:
        return Segredo._criar(quem_faz, dados)

    @staticmethod
    def alterar_por_chave(quem_faz: ChaveUsuario, dados: SegredoComChave) -> None | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE | _VIE:
        return Segredo._alterar(quem_faz, dados)

    @staticmethod
    def excluir_por_chave(quem_faz: ChaveUsuario, dados: ChaveSegredo) -> None | _LEE | _UBE | _PNE | _SNEE:
        return Segredo._excluir_por_chave(quem_faz, dados)

    @staticmethod
    def listar(quem_faz: ChaveUsuario) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        return Segredo._listar(quem_faz)

    @staticmethod
    def buscar(quem_faz: ChaveUsuario, chave: ChaveSegredo) -> SegredoComChave | _LEE | _UBE | _SNEE:
        return Segredo._buscar(quem_faz, chave)

    @staticmethod
    def buscar_sem_logar(chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        return Segredo._buscar_sem_logar(chave)

    @staticmethod
    def pesquisar(quem_faz: ChaveUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        return Segredo._pesquisar(quem_faz, dados)
