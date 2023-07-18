from typing import Self, TypeGuard
from validator import dataclass_validate
from dataclasses import dataclass, replace
from cofre_de_senhas.bd.raiz import cf
from cofre_de_senhas.dao import *
from cofre_de_senhas.service import *
from cofre_de_senhas.usuario.usuario import Usuario, Permissao
from cofre_de_senhas.categoria.categoria import Categoria
from cofre_de_senhas.segredo.segredo_dao_impl import SegredoDAOImpl

dao = SegredoDAOImpl(cf)

@dataclass_validate
@dataclass(frozen = True)
class Segredo:
    cabecalho: Segredo.Cabecalho
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

        def __excluir(self) -> Self:
            dao.deletar_por_pk(self.pk)
            return self

        # Exportado para a classe Usuario.
        @property
        def pk(self) -> SegredoPK:
            return SegredoPK(self.pk_segredo)

        @property
        def __up(self) -> CabecalhoSegredoComChave:
            return CabecalhoSegredoComChave(ChaveSegredo(self.pk_segredo), self.nome, self.descricao, self.tipo_segredo)

        @property
        def __down(self) -> DadosSegredo:
            return DadosSegredo(self.pk_segredo, self.nome, self.descricao, self.tipo_segredo.value)

        @staticmethod
        def __promote(dados: DadosSegredo) -> "Segredo.Cabecalho":
            return Segredo.Cabecalho(dados.pk_segredo, dados.nome, dados.descricao, TipoSegredo(dados.fk_tipo_segredo))

    def __salvar(self) -> Self:
        dao.salvar(self.__down)
        return self.__salvar_dados_internos()

    def __salvar_dados_internos(self) -> Self:
        assert self.usuarios is not None
        assert self.categorias is not None
        assert self.campos is not None

        spk: SegredoPK = self.__pk
        dao.limpar_segredo(spk)

        for descricao in self.campos.keys():
            valor: str = self.campos[descricao]
            dao.criar_campo_segredo(spk, descricao, valor)

        for permissao in self.usuarios.values():
            dao.criar_permissao(permissao.usuario.pk, spk, permissao.tipo.value)

        for categoria in self.categorias.values():
            dao.criar_categoria_segredo(spk, categoria.pk)

        return self

    def __alterar(self, dados: SegredoSemChave) -> Self:
        permissoes: dict[str, Permissao] = Segredo.__mapear_permissoes(dados.usuarios)
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)
        return replace(self, nome = dados.nome, descricao = dados.descricao, tipo_segredo = dados.tipo, campos = dados.campos, categorias = categorias, usuarios = permissoes).__salvar()

    #@property
    #def __chave(self) -> ChaveSegredo:
    #    return ChaveSegredo(self.pk_segredo)

    @property
    def __pk(self) -> SegredoPK:
        return self.cabecalho.pk

    @property
    def __up(self) -> CabecalhoSegredoComChave:
        return self.cabecalho.__up

    @property
    def __up_eager(self) -> SegredoComChave:
        permissoes: dict[str, TipoPermissao] = {} if self.usuarios is None else {k: self.usuarios[k].tipo for k in self.usuarios.keys()}
        return self.__up.com_corpo(self.campos, set(self.categorias.keys()), permissoes)

    @property
    def __down(self) -> DadosSegredo:
        return  self.cabecalho.__down

    def __permitir_escrita_para(self, acesso: Usuario) -> None:
        if acesso.is_admin: return
        valor_permissao: int | None = dao.buscar_permissao(self.__pk, acesso.login)
        if valor_permissao is None: raise PermissaoNegadaException()
        permissao: TipoPermissao = TipoPermissao(valor_permissao)
        if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException()

    # Métodos internos

    @staticmethod
    def __mapear_permissoes(usuarios: dict[str, TipoPermissao]) -> dict[str, Permissao]:
        todos_usuarios: dict[str, Usuario] = Usuario.listar_por_login(set(usuarios.keys()))
        permissoes: dict[str, Permissao] = {}

        for k in usuarios:
            if k not in todos_usuarios:
                raise UsuarioNaoExisteException()
            permissoes[k] = Permissao(todos_usuarios[k], usuarios[k])

        return permissoes

    # Métodos estáticos de fábrica.

    @staticmethod
    def __encontrar_por_chave(chave: ChaveSegredo) -> "Segredo | None":
        dados: DadosSegredo | None = dao.buscar_por_pk(SegredoPK(chave.valor))
        if dados is None: return None
        cabecalho: Segredo.Cabecalho = Segredo.Cabecalho.__promote(dados)
        spk: SegredoPK = cabecalho.pk
        campos: dict[str, str] = {c.pk_chave: c.valor for c in dao.ler_campos_segredo(spk)}
        usuarios: dict[str, Permissao] = Usuario.listar_por_permissao(cabecalho)
        categorias: dict[str, Categoria] = Categoria.listar_por_segredo(spk)
        return Segredo(cabecalho, usuarios, categorias, campos)

    @staticmethod
    def __encontrar_existente_por_chave(chave: ChaveSegredo) -> "Segredo":
        encontrado: Segredo | None = Segredo.__encontrar_por_chave(chave)
        if encontrado is None: raise SegredoNaoExisteException()
        return encontrado

    # Métodos estáticos de fábrica.

    @staticmethod
    def servicos() -> Segredo.Servico:
        return Segredo.Servico.instance()

    @staticmethod
    def __criar(quem_faz: ChaveUsuario, dados: SegredoSemChave) -> "Segredo":
        quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
        if not quem_eh.is_admin and dados.usuarios[quem_eh.login] not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException()

        permissoes: dict[str, Permissao] = Segredo.__mapear_permissoes(dados.usuarios)
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)

        rowid: SegredoPK = dao.criar(DadosSegredoSemPK(dados.nome, dados.descricao, dados.tipo.value))
        return Segredo(Segredo.Cabecalho(rowid.pk_segredo, dados.nome, dados.descricao, dados.tipo), permissoes, categorias, dados.campos).__salvar_dados_internos()

    @staticmethod
    def __listar_todos() -> list["Segredo.Cabecalho"]:
        return [Segredo.Cabecalho.__promote(s) for s in dao.listar()]

    @staticmethod
    def __listar_visiveis(quem_faz: Usuario) -> list["Segredo.Cabecalho"]:
        return [Segredo.Cabecalho.__promote(s) for s in dao.listar_visiveis(quem_faz.login)]

    @staticmethod
    def __listar(quem_faz: Usuario) -> list["Segredo.Cabecalho"]:
        if quem_faz.is_admin: return Segredo.__listar_todos()
        return Segredo.__listar_visiveis(quem_faz)

    class Servico:

        __me: "Segredo.Servico" = Segredo.Servico()

        def __init__(self) -> None:
            if Segredo.Servico.__me: raise Exception()

        @staticmethod
        def instance() -> "Segredo.Servico":
            return Segredo.Servico.__me

        def criar(self, quem_faz: ChaveUsuario, dados: SegredoSemChave) -> SegredoComChave:
            return Segredo.__criar(quem_faz, dados).__up_eager

        @staticmethod
        def alterar_por_chave(quem_faz: ChaveUsuario, dados: SegredoComChave) -> None:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            segredo: Segredo = Segredo.__encontrar_existente_por_chave(dados.chave) # Pode lançar SegredoNaoExisteException
            segredo.__permitir_escrita_para(quem_eh)
            segredo.__alterar(dados.sem_chave)

        @staticmethod
        def excluir_por_chave(quem_faz: ChaveUsuario, dados: ChaveSegredo) -> None:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            segredo: Segredo = Segredo.__encontrar_existente_por_chave(dados) # Pode lançar SegredoNaoExisteException
            segredo.__permitir_escrita_para(quem_eh)
            segredo.cabecalho.__excluir()

        @staticmethod
        def listar(quem_faz: ChaveUsuario) -> ResultadoPesquisaDeSegredos:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            return ResultadoPesquisaDeSegredos([x.__up for x in Segredo.__listar(quem_eh)])

        @staticmethod
        def buscar(quem_faz: ChaveUsuario, chave: ChaveSegredo) -> SegredoComChave:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            segredo: Segredo = Segredo.__encontrar_existente_por_chave(chave)
            if not quem_eh.is_admin and quem_eh.login not in segredo.usuarios.keys(): raise SegredoNaoExisteException()
            return segredo.__up_eager

        @staticmethod
        def pesquisar(quem_faz: ChaveUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
            quem_eh: Usuario = Usuario.verificar_acesso(quem_faz)
            raise NotImplementedError()