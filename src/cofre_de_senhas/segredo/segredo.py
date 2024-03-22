from typing import TypeAlias
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
from ..usuario.usuario import Usuario, Permissao, ServicosImpl as ServicosUsuarioImpl
from ..categoria.categoria import Categoria, ServicosImpl as ServicosCategoriaImpl


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

    # @property
    # def __chave(self) -> ChaveSegredo:
    #     return ChaveSegredo(self.pk_segredo)

    @property
    def _pk(self) -> SegredoPK:
        return self.cabecalho.pk

    @property
    def __up(self) -> CabecalhoSegredoComChave:
        return self.cabecalho._up

    @property
    def _up_eager(self) -> SegredoComChave:
        permissoes: dict[str, TipoPermissao] = {} if self.usuarios is None else {k: self.usuarios[k].tipo for k in self.usuarios.keys()}
        return self.__up.com_corpo(self.campos, sorted(list(self.categorias.keys())), permissoes)

    @property
    def _down(self) -> DadosSegredo:
        return self.cabecalho._down


class ServicosImpl:

    def __init__(self, dao: SegredoDAO, servicos_usuario: ServicosUsuarioImpl, servicos_categoria: ServicosCategoriaImpl) -> None:
        self.__dao: SegredoDAO = dao
        self.__servicos_usuario: ServicosUsuarioImpl = servicos_usuario
        self.__servicos_categoria: ServicosCategoriaImpl = servicos_categoria

    def __salvar(self, s: Segredo) -> Segredo:
        self.__dao.salvar_com_pk(s._down)
        return self.__salvar_dados_internos(s)

    def __limpar(self, s: Segredo) -> None:
        spk: SegredoPK = s._pk
        self.__dao.limpar_segredo(spk)

    def __criar_campos(self, s: Segredo) -> None:
        spk: SegredoPK = s._pk
        for descricao in s.campos.keys():
            valor: str = s.campos[descricao]
            self.__dao.criar_campo_segredo(CampoDeSegredo(spk.pk_segredo, descricao, valor))

    def __criar_permissoes(self, s: Segredo) -> None:
        spk: SegredoPK = s._pk
        for permissao in s.usuarios.values():
            self.__dao.criar_permissao(PermissaoDeSegredo(permissao.usuario.pk.pk_usuario, spk.pk_segredo, permissao.tipo.value))

    def __criar_categorias(self, s: Segredo) -> None:
        spk: SegredoPK = s._pk
        for categoria in s.categorias.values():
            self.__dao.criar_categoria_segredo(CategoriaDeSegredo(spk.pk_segredo, categoria.pk.pk_categoria))

    def __salvar_dados_internos(self, s: Segredo) -> Segredo:
        assert s.usuarios is not None, "Deveriam haver usuários no segredo."
        assert s.categorias is not None, "Deveriam haver categorias no segredo."
        assert s.campos is not None, "Deveriam haver campos no segredo."

        self.__limpar(s)
        self.__criar_campos(s)
        self.__criar_permissoes(s)
        self.__criar_categorias(s)

        return s

    def __alterar(self, quem_faz: ChaveUsuario, dados: SegredoComChave) -> None | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE | _VIE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        s1: Segredo | _SNEE = self.__encontrar_existente_por_chave(dados.chave)
        if not isinstance(s1, Segredo):
            return s1
        p1: None | _PNE | _SNEE = self.__permitir_escrita_para(s1, u1, False)
        if p1 is not None:
            return p1

        up: SegredoComChave = s1._up_eager
        antes: dict[str, TipoPermissao] = up.usuarios
        depois: dict[str, TipoPermissao] = dados.usuarios
        era_proprietario: bool = self.__tem_permissao(u1, up.sem_chave, True)
        sera_proprietario: bool = self.__tem_permissao(u1, dados.sem_chave, True)

        cts: set[str] = set(dados.categorias)
        if len(cts) != len(dados.categorias) or (era_proprietario and not sera_proprietario):
            return ValorIncorretoException()

        if not era_proprietario and antes != depois:
            return PermissaoNegadaException()

        permissoes: dict[str, Permissao] | _UNEE = self.__mapear_permissoes(dados.usuarios)
        if isinstance(permissoes, _UNEE):
            return permissoes
        categorias: dict[str, Categoria] | _CNEE = self.__servicos_categoria.listar_por_nomes(cts)
        if isinstance(categorias, _CNEE):
            return categorias
        c: Segredo.Cabecalho = replace(s1.cabecalho, nome = dados.nome, descricao = dados.descricao, tipo_segredo = dados.tipo)
        self.__salvar(replace(s1, cabecalho = c, campos = dados.campos, categorias = categorias, usuarios = permissoes))
        return None

    def __permitir_escrita_para(self, s: Segredo, acesso: Usuario, somente_proprietario: bool) -> None | _PNE | _SNEE:
        if acesso.is_admin:
            return None

        busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(s._pk.pk_segredo, acesso.login)
        permissao_encontrada: PermissaoDeSegredo | None = self.__dao.buscar_permissao(busca)
        if permissao_encontrada is None:
            if s.cabecalho.tipo_segredo == TipoSegredo.CONFIDENCIAL:
                return SegredoNaoExisteException()
            return PermissaoNegadaException()

        permissao: TipoPermissao = TipoPermissao(permissao_encontrada.fk_tipo_permissao)

        aceitaveis: list[TipoPermissao] = [TipoPermissao.PROPRIETARIO]
        if not somente_proprietario:
            aceitaveis.append(TipoPermissao.LEITURA_E_ESCRITA)
        if permissao not in aceitaveis:
            return PermissaoNegadaException()

        return None

    def __mapear_permissoes(self, usuarios: dict[str, TipoPermissao]) -> dict[str, Permissao] | _UNEE:
        todos_usuarios: dict[str, Usuario] | _UNEE = self.__servicos_usuario.listar_por_logins(set(usuarios.keys()))
        if isinstance(todos_usuarios, _UNEE):
            return todos_usuarios

        permissoes: dict[str, Permissao] = {}

        for k in usuarios:
            if k not in todos_usuarios:
                return UsuarioNaoExisteException()
            permissoes[k] = Permissao(todos_usuarios[k], usuarios[k])

        return permissoes

    def __encontrar_por_chave(self, chave: ChaveSegredo) -> Segredo | None:
        dados: DadosSegredo | None = self.__dao.buscar_por_pk(SegredoPK(chave.valor))
        if dados is None:
            return None
        cabecalho: Segredo.Cabecalho = Segredo.Cabecalho._promote(dados)
        spk: SegredoPK = cabecalho.pk
        campos: dict[str, str] = {c.pk_nome: c.valor for c in self.__dao.ler_campos_segredo(spk)}
        usuarios: dict[str, Permissao] = self.__servicos_usuario.listar_por_permissao(cabecalho)
        categorias: dict[str, Categoria] = self.__servicos_categoria.listar_por_segredo(spk)
        return Segredo(cabecalho, usuarios, categorias, campos)

    def __encontrar_existente_por_chave(self, chave: ChaveSegredo) -> Segredo | _SNEE:
        encontrado: Segredo | None = self.__encontrar_por_chave(chave)
        if encontrado is None:
            return SegredoNaoExisteException()
        return encontrado

    def __tem_permissao(self, u1: Usuario, dados: SegredoSemChave, proprietario: bool) -> bool:
        possibilidades: list[TipoPermissao] = [TipoPermissao.PROPRIETARIO]
        if not proprietario:
            possibilidades.append(TipoPermissao.LEITURA_E_ESCRITA)
            possibilidades.append(TipoPermissao.SOMENTE_LEITURA)
        return u1.is_admin or (u1.login in dados.usuarios and dados.usuarios[u1.login] in possibilidades)

    def __criar(self, quem_faz: ChaveUsuario, dados: SegredoSemChave) -> SegredoComChave | _UNEE | _CNEE | _UBE | _LEE | _VIE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1

        cts: set[str] = set(dados.categorias)
        if len(cts) != len(dados.categorias) or not self.__tem_permissao(u1, dados, True):
            return ValorIncorretoException()

        permissoes: dict[str, Permissao] | _UNEE = self.__mapear_permissoes(dados.usuarios)
        if isinstance(permissoes, _UNEE):
            return permissoes
        categorias: dict[str, Categoria] | _CNEE = self.__servicos_categoria.listar_por_nomes(cts)
        if isinstance(categorias, _CNEE):
            return categorias

        rowid: SegredoPK = self.__dao.criar(DadosSegredoSemPK(dados.nome, dados.descricao, dados.tipo.value))
        cabecalho: Segredo.Cabecalho = Segredo.Cabecalho(rowid.pk_segredo, dados.nome, dados.descricao, dados.tipo)
        return self.__salvar_dados_internos(Segredo(cabecalho, permissoes, categorias, dados.campos))._up_eager

    def __listar_todos(self) -> list[Segredo.Cabecalho]:
        return [Segredo.Cabecalho._promote(s) for s in self.__dao.listar()]

    def __listar_visiveis(self, quem_faz: Usuario) -> list[Segredo.Cabecalho]:
        return [Segredo.Cabecalho._promote(s) for s in self.__dao.listar_visiveis(LoginUsuarioUK(quem_faz.login))]

    def __listar(self, quem_faz: ChaveUsuario) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return ResultadoPesquisaDeSegredos([x._up for x in self.__listar_interno(u1)])

    def __listar_interno(self, quem_faz: Usuario) -> list[Segredo.Cabecalho]:
        if quem_faz.is_admin:
            return self.__listar_todos()
        return self.__listar_visiveis(quem_faz)

    def __buscar(self, quem_faz: ChaveUsuario, chave: ChaveSegredo) -> SegredoComChave | _LEE | _UBE | _SNEE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1

        com_chave: SegredoComChave | _SNEE = self.__buscar_por_chave_sem_logar(chave)
        if not isinstance(com_chave, SegredoComChave):
            return com_chave

        pode_ver: bool = self.__tem_permissao(u1, com_chave.sem_chave, False)

        if com_chave.tipo == TipoSegredo.CONFIDENCIAL and not pode_ver:
            return SegredoNaoExisteException()
        if com_chave.tipo == TipoSegredo.ENCONTRAVEL and not pode_ver:
            return com_chave.limpar_campos
        return com_chave

    def __buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        s1: Segredo | _SNEE = self.__encontrar_existente_por_chave(chave)
        if not isinstance(s1, Segredo):
            return s1
        return s1._up_eager

    def __excluir_por_chave(self, quem_faz: ChaveUsuario, dados: ChaveSegredo) -> None | _LEE | _UBE | _PNE | _SNEE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        s1: Segredo | _SNEE = self.__encontrar_existente_por_chave(dados)
        if not isinstance(s1, Segredo):
            return s1
        p1: None | _PNE | _SNEE = self.__permitir_escrita_para(s1, u1, True)
        if p1 is not None:
            return p1
        self.__dao.deletar_por_pk(s1.cabecalho.pk)
        return None

    def __pesquisar(self, quem_faz: ChaveUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = self.__servicos_usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        raise NotImplementedError()

    def criar(self, quem_faz: ChaveUsuario, dados: SegredoSemChave) -> SegredoComChave | _UNEE | _CNEE | _UBE | _LEE | _VIE:
        return self.__criar(quem_faz, dados)

    def alterar_por_chave(self, quem_faz: ChaveUsuario, dados: SegredoComChave) -> None | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE | _VIE:
        return self.__alterar(quem_faz, dados)

    def excluir_por_chave(self, quem_faz: ChaveUsuario, dados: ChaveSegredo) -> None | _LEE | _UBE | _PNE | _SNEE:
        return self.__excluir_por_chave(quem_faz, dados)

    def listar(self, quem_faz: ChaveUsuario) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        return self.__listar(quem_faz)

    def buscar(self, quem_faz: ChaveUsuario, chave: ChaveSegredo) -> SegredoComChave | _LEE | _UBE | _SNEE:
        return self.__buscar(quem_faz, chave)

    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE:
        return self.__buscar_por_chave_sem_logar(chave)

    def pesquisar(self, quem_faz: ChaveUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos | _LEE | _UBE:
        return self.__pesquisar(quem_faz, dados)
