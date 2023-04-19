import sqlite3
import hashlib
from connection.conn import TransactedConnection
from connection.sqlite3conn import Sqlite3ConnectionWrapper
from .model import *
from .service import *
from .dao import *
from .dao_impl import CofreDeSenhasDAOImpl
from decorators.tracer import Logger
from decorators.for_all import for_all_methods

def string_random() -> str:
    import random
    import string
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(10))

def criar_hash(senha: str) -> str:
    sal = string_random()
    return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest()

def comparar_hash(senha: str, hash: str) -> bool:
    sal = hash[0:10]
    return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest() == hash

log = Logger.for_print_fn()
cf = TransactedConnection(lambda: Sqlite3ConnectionWrapper(sqlite3.connect("banco.db")))
dao = CofreDeSenhasDAOImpl(cf)

# Todos os métodos podem lançar SenhaErradaException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class CofreDeSenhasImpl(CofreDeSenhas):

    def login(self, quem_faz: LoginUsuario) -> NivelAcesso:
        cadastrado: DadosLogin | None = dao.login(quem_faz.login)
        if cadastrado is None or not comparar_hash(quem_faz.senha, cadastrado.hash_com_sal): raise SenhaErradaException()
        nivel: NivelAcesso = NivelAcesso(cadastrado.fk_nivel_acesso)
        if nivel == NivelAcesso.BANIDO: raise UsuarioBanidoException()
        return nivel

    def login_admin(self, quem_faz: LoginUsuario) -> None:
        acesso: NivelAcesso = self.login(quem_faz)
        if acesso != NivelAcesso.CHAVEIRO_DEUS_SUPREMO: raise PermissaoNegadaException()

    def __confirmar_que_usuario_ja_existe(self, quem: str) -> int:
        u: int | None = dao.buscar_pk_usuario_por_login(quem)
        if u is None: raise UsuarioNaoExisteException()
        return u

    def __confirmar_que_usuario_nao_existe(self, quem: str) -> None:
        u: int | None = dao.buscar_pk_usuario_por_login(quem)
        if u is not None: raise UsuarioJaExisteException()

    def __confirmar_que_categoria_ja_existe(self, nome: str) -> int:
        u: int | None = dao.buscar_pk_categoria_por_nome(nome)
        if u is None: raise CategoriaNaoExisteException()
        return u

    def __confirmar_que_categoria_nao_existe(self, nome: str) -> None:
        u: int | None = dao.buscar_pk_categoria_por_nome(nome)
        if u is not None: raise CategoriaJaExisteException()

    def __confirmar_que_segredo_ja_existe(self, pk: SegredoPK) -> int:
        u: int | None = dao.buscar_pk_segredo(pk.valor)
        if u is None: raise SegredoNaoExisteException()
        return u

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioNovo) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_usuario_nao_existe(dados.login)
        dao.criar_usuario(dados.login, dados.nivel_acesso.value, criar_hash(dados.senha))

    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        self.login(quem_faz)
        dao.trocar_senha(quem_faz.login, criar_hash(dados.senha))

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        self.login_admin(quem_faz)
        self.__confirmar_que_usuario_ja_existe(dados.login)
        nova_senha = string_random()
        dao.trocar_senha(dados.login, criar_hash(nova_senha))
        return nova_senha

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_usuario_ja_existe(dados.login)
        dao.alterar_nivel_de_acesso(dados.login, dados.nivel_acesso.value)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoListaDeUsuarios:
        def converter(entra: DadosNivel) -> UsuarioComNivel:
            return UsuarioComNivel(entra.login, NivelAcesso(entra.fk_nivel_acesso))
        self.login(quem_faz)
        return ResultadoListaDeUsuarios(lista = [converter(x) for x in dao.listar_usuarios()])

    def __mapear_usuarios(self, logins: set[str]) -> dict[str, int]:
        pk_usuarios: dict[str, int] = {}
        for login in logins:
            pk_usuarios[login] = self.__confirmar_que_usuario_ja_existe(login)
        return pk_usuarios

    def __mapear_categorias(self, nomes: set[str]) -> dict[str, int]:
        pk_categorias: dict[str, int] = {}
        for nome in nomes:
            pk_categorias[nome] = self.__confirmar_que_categoria_ja_existe(nome)
        return pk_categorias

    def __alterar_dados_segredo(self, dados: SegredoComPK, pk_usuarios: dict[str, int], pk_categorias: dict[str, int]) -> None:

        dao.limpar_segredo(dados.pk.valor)

        for descricao in dados.campos.keys():
            valor = dados.campos[descricao]
            dao.criar_campo_segredo(dados.pk.valor, descricao, valor)

        for login in dados.usuarios.keys():
            pk_usuario = pk_usuarios[login]
            permissao = dados.usuarios[login]
            dao.criar_permissao(pk_usuario, dados.pk.valor, permissao.value)

        for nome in dados.categorias:
            pk_categoria = pk_categorias[nome]
            dao.criar_categoria_segredo(dados.pk.valor, pk_categoria)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        self.login(quem_faz)

        if dados.usuarios[quem_faz.login] != TipoPermissao.PROPRIETARIO: raise PermissaoNegadaException

        pk_usuarios: dict[str, int] = self.__mapear_usuarios({*dados.usuarios})
        pk_categorias: dict[str, int] = self.__mapear_categorias(dados.categorias)

        rowid: int = dao.criar_segredo(dados.nome, dados.descricao, dados.tipo.value)
        assert rowid is not None

        self.__alterar_dados_segredo(dados.com_pk(SegredoPK(rowid)), pk_usuarios, pk_categorias)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        self.login(quem_faz)

        self.__confirmar_que_segredo_ja_existe(dados.pk) # Pode lançar SegredoNaoExisteException
        pk_usuarios: dict[str, int] = self.__mapear_usuarios({*dados.usuarios})
        pk_categorias: dict[str, int] = self.__mapear_categorias(dados.categorias)

        dao.alterar_segredo(dados.pk.valor, dados.nome, dados.descricao, dados.tipo.value)

        self.__alterar_dados_segredo(dados, pk_usuarios, pk_categorias)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        nivel = self.login(quem_faz)

        self.__confirmar_que_segredo_ja_existe(dados) # Pode lançar SegredoNaoExisteException

        if nivel == NivelAcesso.NORMAL:
            tipo_permissao: int | None = dao.buscar_permissao(dados.valor, quem_faz.login)
            if tipo_permissao is None: raise PermissaoNegadaException
            permissao: TipoPermissao = TipoPermissao.por_codigo(tipo_permissao)
            if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException
        elif nivel == NivelAcesso.CHAVEIRO_DEUS_SUPREMO:
            pass
        else:
            assert False

        dao.deletar_segredo(dados.valor)

    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisaDeSegredos:
        def converter(entra: CabecalhoDeSegredo) -> CabecalhoSegredoComPK:
            return CabecalhoSegredoComPK(SegredoPK(entra.pk_segredo), entra.nome, entra.descricao, TipoSegredo.por_codigo(entra.fk_tipo_segredo))

        nivel = self.login(quem_faz)
        if nivel == NivelAcesso.CHAVEIRO_DEUS_SUPREMO:
            segredos = dao.listar_todos_segredos()
        else:
            segredos = dao.listar_segredos_visiveis(quem_faz.login)
        return ResultadoPesquisaDeSegredos([converter(x) for x in segredos])

    # Pode lançar SegredoNaoExisteException
    def buscar_segredo(self, quem_faz: LoginUsuario, pk: SegredoPK) -> SegredoComPK:
        acesso: NivelAcesso = self.login(quem_faz)
        valor_pk = pk.valor

        cabecalho: CabecalhoDeSegredo | None = dao.ler_cabecalho_segredo(valor_pk)
        if cabecalho is None: raise SegredoNaoExisteException()

        tipo: TipoSegredo = TipoSegredo.por_codigo(cabecalho.fk_tipo_segredo)

        campos: dict[str, str] = {elemento.chave: elemento.valor for elemento in dao.ler_campos_segredo(valor_pk)}
        categorias: set[str] = {elemento.nome for elemento in dao.ler_nomes_categorias(valor_pk)}
        usuarios: dict[str, TipoPermissao] = {elemento.login: TipoPermissao.por_codigo(elemento.permissao) for elemento in dao.ler_login_com_permissoes(valor_pk)}

        if acesso != NivelAcesso.CHAVEIRO_DEUS_SUPREMO and quem_faz.login not in usuarios: raise SegredoNaoExisteException()

        return SegredoComPK(pk, cabecalho.nome, cabecalho.descricao, tipo, campos, categorias, usuarios)

    # Pode lançar CategoriaNaoExisteException
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaJaExisteException
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_categoria_nao_existe(dados.nome)
        dao.criar_categoria(dados.nome)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_categoria_ja_existe(dados.antigo)
        self.__confirmar_que_categoria_nao_existe(dados.novo)
        dao.renomear_categoria(dados.antigo, dados.novo)

    # Pode lançar CategoriaNaoExisteException
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_categoria_ja_existe(dados.nome)
        dao.deletar_categoria(dados.nome)