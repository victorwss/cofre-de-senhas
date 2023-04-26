import sqlite3
import hashlib
from typing import Generic, Self, TypeGuard
from connection.conn import TransactedConnection
from connection.sqlite3conn import Sqlite3ConnectionWrapper
from .model import *
from .service import *
from .dao import *
from .dao_impl import *
from decorators.tracer import Logger
from decorators.for_all import for_all_methods
from dataclasses import dataclass, replace

log = Logger.for_print_fn()
cf = TransactedConnection(lambda: Sqlite3ConnectionWrapper(sqlite3.connect("banco.db")))
dao = CofreDeSenhasDAOImpl(cf)
cdao = CategoriaDAOImpl(cf)
udao = UsuarioDAOImpl(cf)
sdao = SegredoDAOImpl(cf)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class CofreDeSenhasImpl(CofreDeSenhas):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl = gl

    # Pode lançar SenhaErradaException
    def login(self, quem_faz: LoginUsuario) -> None:
        self.__gl.login(Usuario.fazer_login(quem_faz).chave)

    def logout(self) -> None:
        self.__gl.logout()

    @property
    def __usuario_logado(self) -> Usuario:
        return Usuario.encontrar_existente_por_chave(self.__gl.usuario_logado).permitir_acesso()

    @property
    def __admin_logado(self) -> Usuario:
        return self.__usuario_logado.permitir_admin()

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar_usuario(self, dados: UsuarioNovo) -> None:
        self.__admin_logado
        Usuario.criar(dados.login, dados.nivel_acesso, dados.senha)

    def trocar_senha(self, dados: NovaSenha) -> None:
        self.__usuario_logado.trocar_senha(dados.senha)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, dados: ResetLoginUsuario) -> str:
        self.__admin_logado
        return Usuario.encontrar_existente_por_login(dados.login).resetar_senha().nova_senha

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, dados: UsuarioComNivel) -> None:
        self.__admin_logado
        Usuario.encontrar_existente_por_login(dados.login).alterar_nivel_de_acesso(dados.nivel_acesso.value)

    # Pode lançar UsuarioNaoExisteException
    def buscar_usuario_por_login(self, login: str) -> UsuarioComChave:
        self.__usuario_logado
        return Usuario.encontrar_existente_por_login(login).up

    # Pode lançar UsuarioNaoExisteException
    def buscar_usuario_por_chave(self, chave: UsuarioChave) -> UsuarioComChave:
        self.__usuario_logado
        return Usuario.encontrar_existente_por_chave(chave).up

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar_usuarios(self) -> ResultadoListaDeUsuarios:
        self.__usuario_logado
        return ResultadoListaDeUsuarios(lista = [x.up for x in Usuario.listar()])

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar_segredo(self, dados: SegredoSemChave) -> None:
        quem_faz: Usuario = self.__usuario_logado
        Segredo.criar_segredo(quem_faz, dados)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    def alterar_segredo(self, dados: SegredoComChave) -> None:
        self.__usuario_logado
        Segredo.alterar_segredo(dados)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    def excluir_segredo(self, dados: SegredoChave) -> None:
        quem_faz: Usuario = self.__usuario_logado
        Segredo.excluir_segredo(quem_faz, dados)

    def listar_segredos(self) -> ResultadoPesquisaDeSegredos:
        def converter(entra: CabecalhoDeSegredo) -> CabecalhoSegredoComChave:
            return CabecalhoSegredoComChave(SegredoChave(entra.pk_segredo), entra.nome, entra.descricao, TipoSegredo.por_codigo(entra.fk_tipo_segredo))
        quem_faz: Usuario = self.__usuario_logado
        return ResultadoPesquisaDeSegredos([converter(x) for x in Segredo.listar_segredos(quem_faz)])

    # Pode lançar SegredoNaoExisteException
    def buscar_segredo_por_chave(self, chave: SegredoChave) -> SegredoComChave:
        quem_faz: Usuario = self.__usuario_logado
        return Segredo.buscar_segredo(quem_faz, chave)

    # Pode lançar CategoriaNaoExisteException
    def pesquisar_segredos(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        quem_faz: Usuario = self.__usuario_logado
        return Segredo.pesquisar_segredos(quem_faz, dados)

    # Pode lançar CategoriaNaoExisteException
    def buscar_categoria_por_nome(self, nome: str) -> CategoriaComChave:
        self.__usuario_logado
        return Categoria.encontrar_existente_por_nome(nome).up

    # Pode lançar CategoriaNaoExisteException
    def buscar_categoria_por_chave(self, chave: CategoriaChave) -> CategoriaComChave:
        self.__usuario_logado
        return Categoria.encontrar_existente_por_chave(chave).up

    # Pode lançar CategoriaJaExisteException
    def criar_categoria(self, dados: NomeCategoria) -> None:
        self.__admin_logado
        Categoria.criar(dados.nome)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_categoria(self, dados: RenomeCategoria) -> None:
        self.__admin_logado
        Categoria.encontrar_existente_por_nome(dados.antigo).renomear(dados.novo)

    # Pode lançar CategoriaNaoExisteException
    def excluir_categoria(self, dados: NomeCategoria) -> None:
        self.__admin_logado
        Categoria.encontrar_existente_por_nome(dados.nome).excluir()

    def listar_categorias(self) -> ResultadoListaDeCategorias:
        self.__usuario_logado
        return ResultadoListaDeCategorias([x.up for x in Categoria.listar()])

@dataclass(frozen = True)
class Segredo:
    pk_segredo: int
    nome: str
    descricao: str
    tipo_segredo: TipoSegredo

    @staticmethod
    def __confirmar_que_segredo_ja_existe(chave: SegredoChave) -> int:
        u: int | None = sdao.buscar_pk_segredo(chave.valor)
        if u is None: raise SegredoNaoExisteException()
        return u

    @staticmethod
    def __alterar_dados_segredo(dados: SegredoComChave, usuarios: dict[str, Usuario], categorias: dict[str, Categoria]) -> None:

        sdao.limpar_segredo(dados.chave.valor)

        for descricao in dados.campos.keys():
            valor = dados.campos[descricao]
            sdao.criar_campo_segredo(dados.chave.valor, descricao, valor)

        for login in dados.usuarios.keys():
            pk_usuario = usuarios[login].pk_usuario
            permissao = dados.usuarios[login]
            sdao.criar_permissao(pk_usuario, dados.chave.valor, permissao.value)

        for nome in dados.categorias:
            pk_categoria = categorias[nome].pk_categoria
            sdao.criar_categoria_segredo(dados.chave.valor, pk_categoria)

    @staticmethod
    def criar_segredo(quem_faz: Usuario, dados: SegredoSemChave) -> None:
        if not quem_faz.is_admin and dados.usuarios[quem_faz.login] != TipoPermissao.PROPRIETARIO: raise PermissaoNegadaException

        usuarios: dict[str, Usuario] = Usuario.listar_por_login({*dados.usuarios})
        categorias: dict[str, Categoria] = Categoria.listar_por_nome(dados.categorias)

        rowid: int = sdao.criar_segredo(dados.nome, dados.descricao, dados.tipo.value)
        assert rowid is not None

        Segredo.__alterar_dados_segredo(dados.com_chave(SegredoChave(rowid)), usuarios, categorias)

    @staticmethod
    def alterar_segredo(dados: SegredoComChave) -> None:
        Segredo.__confirmar_que_segredo_ja_existe(dados.chave) # Pode lançar SegredoNaoExisteException
        usuarios: dict[str, Usuario] = Usuario.listar_por_login({*dados.usuarios})
        categorias: dict[str, Categoria] = Categoria.listar_por_nome(dados.categorias)

        sdao.alterar_segredo(dados.chave.valor, dados.nome, dados.descricao, dados.tipo.value)

        Segredo.__alterar_dados_segredo(dados, usuarios, categorias)

    @staticmethod
    def excluir_segredo(quem_faz: Usuario, dados: SegredoChave) -> None:
        Segredo.__confirmar_que_segredo_ja_existe(dados) # Pode lançar SegredoNaoExisteException

        if not quem_faz.is_admin:
            tipo_permissao: int | None = sdao.buscar_permissao(dados.valor, quem_faz.login)
            if tipo_permissao is None: raise PermissaoNegadaException
            permissao: TipoPermissao = TipoPermissao.por_codigo(tipo_permissao)
            if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException

        sdao.deletar_segredo(dados.valor)

    @staticmethod
    def listar_segredos(quem_faz: Usuario) -> list[CabecalhoDeSegredo]:
        if quem_faz.is_admin:
            return sdao.listar_todos_segredos()
        else:
            return sdao.listar_segredos_visiveis(quem_faz.login)

    @staticmethod
    def buscar_segredo(quem_faz: Usuario, chave: SegredoChave) -> SegredoComChave:
        pk: int = chave.valor

        cabecalho: CabecalhoDeSegredo | None = sdao.ler_cabecalho_segredo(pk)
        if cabecalho is None: raise SegredoNaoExisteException()

        tipo: TipoSegredo = TipoSegredo.por_codigo(cabecalho.fk_tipo_segredo)

        campos: dict[str, str] = {elemento.chave: elemento.valor for elemento in sdao.ler_campos_segredo(pk)}
        categorias: set[str] = {elemento.nome for elemento in cdao.listar_por_segredo(SegredoPK(pk))}
        usuarios: dict[str, TipoPermissao] = {elemento.login: TipoPermissao.por_codigo(elemento.permissao) for elemento in sdao.ler_login_com_permissoes(pk)}

        if not quem_faz.is_admin and quem_faz.login not in usuarios: raise SegredoNaoExisteException()

        return SegredoComChave(chave, cabecalho.nome, cabecalho.descricao, tipo, campos, categorias, usuarios)

    @staticmethod
    def pesquisar_segredos(quem_faz: Usuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        raise NotImplementedError()

@dataclass(frozen = True)
class SenhaAlterada:
    usuario: "Usuario"
    nova_senha: str

@dataclass(frozen = True)
class Usuario:
    pk_usuario: int
    login: str
    nivel_acesso: NivelAcesso
    hash_com_sal: str

    def trocar_senha(self, nova_senha: str) -> Usuario:
        return replace(self, hash_com_sal = Usuario.__criar_hash(nova_senha)).__salvar()

    def resetar_senha(self) -> SenhaAlterada:
        nova_senha: str = Usuario.__string_random()
        return SenhaAlterada(self.trocar_senha(nova_senha), nova_senha)

    def alterar_nivel_de_acesso(self, novo_nivel_acesso: NivelAcesso) -> Usuario:
        return replace(self, nivel_acesso = novo_nivel_acesso).__salvar()

    def excluir(self) -> Self:
        udao.deletar_por_pk(UsuarioPK(self.pk_usuario))
        return self

    @property
    def is_admin(self) -> bool:
        return self.nivel_acesso == NivelAcesso.CHAVEIRO_DEUS_SUPREMO

    @property
    def is_permitido(self) -> bool:
        return self.nivel_acesso != NivelAcesso.BANIDO

    def permitir_admin(self) -> Self:
        if not self.is_admin: raise PermissaoNegadaException()
        return self

    def permitir_acesso(self) -> Self:
        if not self.is_permitido: raise PermissaoNegadaException()
        return self

    def __salvar(self) -> Self:
        udao.salvar(self.__down)
        return self

    @property
    def chave(self) -> UsuarioChave:
        return UsuarioChave(self.pk_usuario)

    @property
    def up(self) -> UsuarioComChave:
        return UsuarioComChave(self.chave, self.login, self.nivel_acesso)

    @property
    def __down(self) -> DadosUsuario:
        return DadosUsuario(self.pk_usuario, self.login, self.nivel_acesso.value, self.hash_com_sal)

    @staticmethod
    def __promote(dados: DadosUsuario) -> Usuario:
        return Usuario(dados.pk_usuario, dados.login, NivelAcesso.por_codigo(dados.fk_nivel_acesso), dados.hash_com_sal)

    @staticmethod
    def __string_random() -> str:
        import random
        import string
        letters = string.ascii_letters
        return "".join(random.choice(letters) for i in range(10))

    @staticmethod
    def __criar_hash(senha: str) -> str:
        sal = Usuario.__string_random()
        return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest()

    def __comparar_hash(self, senha: str) -> bool:
        sal = self.hash_com_sal[0:10]
        return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest() == self.hash_com_sal

    @staticmethod
    def fazer_login(quem_faz: LoginUsuario) -> Usuario:
        dados: DadosUsuario | None = udao.buscar_por_login(quem_faz.login)
        if dados is None: raise SenhaErradaException()
        cadastrado: Usuario = Usuario.__promote(dados)
        if not cadastrado.__comparar_hash(quem_faz.senha): raise SenhaErradaException()
        return cadastrado.permitir_acesso()

    @staticmethod
    def encontrar_por_chave(chave: UsuarioChave) -> Usuario | None:
        dados: DadosUsuario | None = udao.buscar_por_pk(UsuarioPK(chave.valor))
        if dados is None: return None
        return Usuario.__promote(dados)

    @staticmethod
    def encontrar_existente_por_chave(chave: UsuarioChave) -> Usuario:
        encontrado: Usuario | None = Usuario.encontrar_por_chave(chave)
        if encontrado is None: raise UsuarioNaoExisteException()
        return encontrado

    @staticmethod
    def encontrar_por_login(login: str) -> Usuario | None:
        dados: DadosUsuario | None = udao.buscar_por_login(login)
        if dados is None: return None
        return Usuario.__promote(dados)

    @staticmethod
    def encontrar_existente_por_login(login: str) -> Usuario:
        encontrado: Usuario | None = Usuario.encontrar_por_login(login)
        if encontrado is None: raise UsuarioNaoExisteException()
        return encontrado

    @staticmethod
    def nao_existente_por_login(login: str) -> None:
        talvez: Usuario | None = Usuario.encontrar_por_login(login)
        if talvez is not None: raise UsuarioJaExisteException()

    @staticmethod
    def criar(login: str, nivel: NivelAcesso, senha: str) -> Usuario:
        Usuario.nao_existente_por_login(login)
        hash_com_sal: str = Usuario.__criar_hash(senha)
        pk: UsuarioPK = udao.criar(DadosUsuarioSemPK(login, nivel.value, hash_com_sal))
        return Usuario(pk.pk_usuario, login, nivel, hash_com_sal)

    @staticmethod
    def listar() -> list[Usuario]:
        return [Usuario.__promote(u) for u in udao.listar()]

    @staticmethod
    def listar_por_login(logins: set[str]) -> dict[str, Usuario]:
        def filtragem(p: str) -> TypeGuard[tuple[str, Usuario]]:
            return p in logins
        usuarios: dict[str, Usuario] = {usuario.login: usuario for usuario in Usuario.listar()}
        return dict(filter(filtragem, usuarios))

@dataclass(frozen = True)
class Categoria:

    pk_categoria: int
    nome: str

    def renomear(self, novo_nome: str) -> Categoria:
        Categoria.nao_existente_por_nome(novo_nome)
        return replace(self, nome = novo_nome).__salvar()

    def excluir(self) -> Self:
        cdao.deletar_por_pk(CategoriaPK(self.pk_categoria))
        return self

    def __salvar(self) -> Self:
        cdao.salvar(self.__down)
        return self

    @property
    def chave(self) -> CategoriaChave:
        return CategoriaChave(self.pk_categoria)

    @property
    def up(self) -> CategoriaComChave:
        return CategoriaComChave(self.chave, self.nome)

    @property
    def __down(self) -> DadosCategoria:
        return DadosCategoria(self.pk_categoria, self.nome)

    @staticmethod
    def __promote(dados: DadosCategoria) -> Categoria:
        return Categoria(dados.pk_categoria, dados.nome)

    @staticmethod
    def encontrar_por_chave(chave: CategoriaChave) -> Categoria | None:
        dados: DadosCategoria | None = cdao.buscar_por_pk(CategoriaPK(chave.valor))
        if dados is None: return None
        return Categoria.__promote(dados)

    @staticmethod
    def encontrar_existente_por_chave(chave: CategoriaChave) -> Categoria:
        encontrado: Categoria | None = Categoria.encontrar_por_chave(chave)
        if encontrado is None: raise CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def encontrar_por_nome(nome: str) -> Categoria | None:
        dados: DadosCategoria | None = cdao.buscar_por_nome(nome)
        if dados is None: return None
        return Categoria.__promote(dados)

    @staticmethod
    def encontrar_existente_por_nome(nome: str) -> Categoria:
        encontrado: Categoria | None = Categoria.encontrar_por_nome(nome)
        if encontrado is None: raise CategoriaNaoExisteException()
        return encontrado

    @staticmethod
    def nao_existente_por_nome(nome: str) -> None:
        talvez: Categoria | None = Categoria.encontrar_por_nome(nome)
        if talvez is not None: raise CategoriaJaExisteException()

    @staticmethod
    def criar(nome: str) -> Categoria:
        Categoria.nao_existente_por_nome(nome)
        pk: CategoriaPK = cdao.criar(DadosCategoriaSemPK(nome))
        return Categoria(pk.pk_categoria, nome)

    @staticmethod
    def listar() -> list[Categoria]:
        return [Categoria.__promote(c) for c in cdao.listar()]

    @staticmethod
    def listar_por_nome(nomes: set[str]) -> dict[str, Categoria]:
        def filtragem(p: str) -> TypeGuard[tuple[str, Categoria]]:
            return p in nomes
        categorias: dict[str, Categoria] = {categoria.nome: categoria for categoria in Categoria.listar()}
        return dict(filter(filtragem, categorias))