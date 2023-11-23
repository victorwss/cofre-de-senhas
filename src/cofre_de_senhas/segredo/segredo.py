from typing import Self, TypeGuard
from validator import dataclass_validate
from dataclasses import dataclass, replace
from ..dao import \
    SegredoDAO, SegredoPK, DadosSegredo, DadosSegredoSemPK, \
    LoginUsuario as LoginUsuarioDAO, BuscaPermissaoPorLogin, \
    CategoriaDeSegredo, CampoDeSegredo, PermissaoDeSegredo
from ..service import *
from ..usuario.usuario import Usuario, Permissao
from ..categoria.categoria import Categoria

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

        def _excluir(self) -> Self:
            SegredoDAO.instance().deletar_por_pk(self.pk)
            return self

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

    def _alterar(self, dados: SegredoSemChave) -> Self:
        permissoes: dict[str, Permissao] = Segredo.__mapear_permissoes(dados.usuarios)
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)
        c: Segredo.Cabecalho = replace(self.cabecalho, nome = dados.nome, descricao = dados.descricao, tipo_segredo = dados.tipo)
        return replace(self, cabecalho = c, campos = dados.campos, categorias = categorias, usuarios = permissoes).__salvar()

    #@property
    #def __chave(self) -> ChaveSegredo:
    #    return ChaveSegredo(self.pk_segredo)

    @property
    def __pk(self) -> SegredoPK:
        return self.cabecalho.pk

    @property
    def _up(self) -> CabecalhoSegredoComChave:
        return self.cabecalho._up

    @property
    def _up_eager(self) -> SegredoComChave:
        permissoes: dict[str, TipoPermissao] = {} if self.usuarios is None else {k: self.usuarios[k].tipo for k in self.usuarios.keys()}
        return self._up.com_corpo(self.campos, set(self.categorias.keys()), permissoes)

    @property
    def __down(self) -> DadosSegredo:
        return  self.cabecalho._down

    def _permitir_escrita_para(self, acesso: Usuario) -> None:
        if acesso.is_admin: return
        busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(self.__pk.pk_segredo, acesso.login)
        permissao_encontrada: PermissaoDeSegredo | None = SegredoDAO.instance().buscar_permissao(busca)
        if permissao_encontrada is None: raise PermissaoNegadaException()
        permissao: TipoPermissao = TipoPermissao(permissao_encontrada.fk_tipo_permissao)
        if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException()

    # Métodos internos

    @staticmethod
    def __mapear_permissoes(usuarios: dict[str, TipoPermissao]) -> dict[str, Permissao]:
        todos_usuarios: dict[str, Usuario] = Usuario.listar_por_logins(set(usuarios.keys()))
        permissoes: dict[str, Permissao] = {}

        for k in usuarios:
            if k not in todos_usuarios:
                raise UsuarioNaoExisteException()
            permissoes[k] = Permissao(todos_usuarios[k], usuarios[k])

        return permissoes

    # Métodos estáticos de fábrica.

    @staticmethod
    def __encontrar_por_chave(chave: ChaveSegredo) -> "Segredo | None":
        dados: DadosSegredo | None = SegredoDAO.instance().buscar_por_pk(SegredoPK(chave.valor))
        if dados is None: return None
        cabecalho: Segredo.Cabecalho = Segredo.Cabecalho._promote(dados)
        spk: SegredoPK = cabecalho.pk
        campos: dict[str, str] = {c.pk_nome: c.valor for c in SegredoDAO.instance().ler_campos_segredo(spk)}
        usuarios: dict[str, Permissao] = Usuario.listar_por_permissao(cabecalho)
        categorias: dict[str, Categoria] = Categoria.listar_por_segredo(spk)
        return Segredo(cabecalho, usuarios, categorias, campos)

    @staticmethod
    def _encontrar_existente_por_chave(chave: ChaveSegredo) -> "Segredo":
        encontrado: Segredo | None = Segredo.__encontrar_por_chave(chave)
        if encontrado is None: raise SegredoNaoExisteException()
        return encontrado

    # Métodos estáticos de fábrica.

    @staticmethod
    def servicos() -> "Segredo.Servico":
        return Segredo.Servico.instance()

    @staticmethod
    def _criar(quem_faz: ChaveUsuario, dados: SegredoSemChave) -> "Segredo":
        quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
        if not quem_eh.is_admin and dados.usuarios[quem_eh.login] not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException()

        permissoes: dict[str, Permissao] = Segredo.__mapear_permissoes(dados.usuarios)
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)

        rowid: SegredoPK = SegredoDAO.instance().criar(DadosSegredoSemPK(dados.nome, dados.descricao, dados.tipo.value))
        return Segredo(Segredo.Cabecalho(rowid.pk_segredo, dados.nome, dados.descricao, dados.tipo), permissoes, categorias, dados.campos).__salvar_dados_internos()

    @staticmethod
    def __listar_todos() -> list["Segredo.Cabecalho"]:
        return [Segredo.Cabecalho._promote(s) for s in SegredoDAO.instance().listar()]

    @staticmethod
    def __listar_visiveis(quem_faz: Usuario) -> list["Segredo.Cabecalho"]:
        return [Segredo.Cabecalho._promote(s) for s in SegredoDAO.instance().listar_visiveis(LoginUsuarioDAO(quem_faz.login))]

    @staticmethod
    def _listar(quem_faz: Usuario) -> list["Segredo.Cabecalho"]:
        if quem_faz.is_admin: return Segredo.__listar_todos()
        return Segredo.__listar_visiveis(quem_faz)

    class Servico:

        __me: "Segredo.Servico | None" = None

        def __init__(self) -> None:
            if Segredo.Servico.__me: raise Exception()

        @staticmethod
        def instance() -> "Segredo.Servico":
            if not Segredo.Servico.__me:
                Segredo.Servico.__me = Segredo.Servico()
            return Segredo.Servico.__me

        def criar(self, quem_faz: ChaveUsuario, dados: SegredoSemChave) -> SegredoComChave:
            return Segredo._criar(quem_faz, dados)._up_eager

        @staticmethod
        def alterar_por_chave(quem_faz: ChaveUsuario, dados: SegredoComChave) -> None:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            segredo: Segredo = Segredo._encontrar_existente_por_chave(dados.chave) # Pode lançar SegredoNaoExisteException
            segredo._permitir_escrita_para(quem_eh)
            segredo._alterar(dados.sem_chave)

        @staticmethod
        def excluir_por_chave(quem_faz: ChaveUsuario, dados: ChaveSegredo) -> None:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            segredo: Segredo = Segredo._encontrar_existente_por_chave(dados) # Pode lançar SegredoNaoExisteException
            segredo._permitir_escrita_para(quem_eh)
            segredo.cabecalho._excluir()

        @staticmethod
        def listar(quem_faz: ChaveUsuario) -> ResultadoPesquisaDeSegredos:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            return ResultadoPesquisaDeSegredos([x._up for x in Segredo._listar(quem_eh)])

        @staticmethod
        def buscar(quem_faz: ChaveUsuario, chave: ChaveSegredo) -> SegredoComChave:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            segredo: Segredo = Segredo._encontrar_existente_por_chave(chave) # Pode lançar SegredoNaoExisteException
            if not quem_eh.is_admin and quem_eh.login not in segredo.usuarios.keys(): raise SegredoNaoExisteException()
            return segredo._up_eager

        @staticmethod
        def buscar_sem_logar(chave: ChaveSegredo) -> SegredoComChave:
            return Segredo._encontrar_existente_por_chave(chave)._up_eager # Pode lançar SegredoNaoExisteException

        @staticmethod
        def pesquisar(quem_faz: ChaveUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            raise NotImplementedError()