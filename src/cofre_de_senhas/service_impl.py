import hashlib
from typing import override
from decorators.for_all import for_all_methods
from dataclasses import dataclass, replace
from connection.trans import TransactedConnection
from cofre_de_senhas.service import *
from cofre_de_senhas.dao import CofreDeSenhasDAO
from cofre_de_senhas.categoria.categoria import Categoria
from cofre_de_senhas.usuario.usuario import Usuario, SenhaAlterada
from cofre_de_senhas.segredo.segredo import Segredo
from decorators.tracer import Logger

_log: Logger = Logger.for_print_fn()

class Servicos:

    def __init__(self, gl: GerenciadorLogin, trans: TransactedConnection) -> None:
        self.__gl: GerenciadorLogin = gl
        self.__trans: TransactedConnection = trans

    @property
    def bd(self) -> ServicoBD:
        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna(_ServicoBDImpl):
            pass
        return Interna()

    @property
    def usuario(self) -> ServicoUsuario:
        gl: GerenciadorLogin = self.__gl
        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna(_ServicoUsuarioImpl):
            def __init__(self2) -> None:
                super().__init__(gl)
        return Interna()

    @property
    def categoria(self) -> ServicoCategoria:
        gl: GerenciadorLogin = self.__gl
        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna(_ServicoCategoriaImpl):
            def __init__(self2) -> None:
                super().__init__(gl)
        return Interna()

    @property
    def segredo(self) -> ServicoSegredo:
        gl: GerenciadorLogin = self.__gl
        @for_all_methods(_log.trace)
        @for_all_methods(self.__trans.transact)
        class Interna(_ServicoSegredoImpl):
            def __init__(self2) -> None:
                super().__init__(gl)
        return Interna()

class _ServicoBDImpl(ServicoBD):

    @override
    def criar_bd(self, dados: LoginComSenha) -> None:
        CofreDeSenhasDAO.instance().criar_bd()
        Usuario.servicos().criar_admin(dados)

# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoUsuarioImpl(ServicoUsuario):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl: GerenciadorLogin = gl

    # Pode lançar SenhaErradaException
    @override
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave:
        u: UsuarioComChave = Usuario.servicos().login(quem_faz)
        self.__gl.login(u)
        return u

    @override
    def logout(self) -> None:
        self.__gl.logout()

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @override
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave:
        return Usuario.servicos().criar(self.__gl.usuario_logado, dados)

    @override
    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None:
        Usuario.servicos().trocar_senha_por_chave(self.__gl.usuario_logado, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada:
        return Usuario.servicos().resetar_senha_por_login(self.__gl.usuario_logado, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None:
        Usuario.servicos().alterar_nivel_por_login(self.__gl.usuario_logado, dados)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave:
        return Usuario.servicos().buscar_por_login(self.__gl.usuario_logado, dados)

    # Pode lançar UsuarioNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave:
        return Usuario.servicos().buscar_por_chave(self.__gl.usuario_logado, chave)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @override
    def listar(self) -> ResultadoListaDeUsuarios:
        return Usuario.servicos().listar(self.__gl.usuario_logado)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoSegredoImpl(ServicoSegredo):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl: GerenciadorLogin = gl

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @override
    def criar(self, dados: SegredoSemChave) -> SegredoComChave:
        return Segredo.servicos().criar(self.__gl.usuario_logado, dados)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    @override
    def alterar_por_chave(self, dados: SegredoComChave) -> None:
        Segredo.servicos().alterar_por_chave(self.__gl.usuario_logado, dados)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    @override
    def excluir_por_chave(self, dados: ChaveSegredo) -> None:
        Segredo.servicos().excluir_por_chave(self.__gl.usuario_logado, dados)

    @override
    def listar(self) -> ResultadoPesquisaDeSegredos:
        return Segredo.servicos().listar(self.__gl.usuario_logado)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave:
        return Segredo.servicos().buscar(self.__gl.usuario_logado, chave)

    # Pode lançar SegredoNaoExisteException
    @override
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave:
        return Segredo.servicos().buscar_sem_logar(chave)

    # Pode lançar SegredoNaoExisteException
    @override
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        return Segredo.servicos().pesquisar(self.__gl.usuario_logado, dados)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class _ServicoCategoriaImpl(ServicoCategoria):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl: GerenciadorLogin = gl

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave:
        return Categoria.servicos().buscar_por_nome(self.__gl.usuario_logado, dados)

    # Pode lançar CategoriaNaoExisteException
    @override
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave:
        return Categoria.servicos().buscar_por_chave(self.__gl.usuario_logado, chave)

    # Pode lançar CategoriaJaExisteException
    @override
    def criar(self, dados: NomeCategoria) -> CategoriaComChave:
        return Categoria.servicos().criar(self.__gl.usuario_logado, dados)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @override
    def renomear_por_nome(self, dados: RenomeCategoria) -> None:
        Categoria.servicos().renomear_por_nome(self.__gl.usuario_logado, dados)

    # Pode lançar CategoriaNaoExisteException
    @override
    def excluir_por_nome(self, dados: NomeCategoria) -> None:
        Categoria.servicos().excluir_por_nome(self.__gl.usuario_logado, dados)

    @override
    def listar(self) -> ResultadoListaDeCategorias:
        return Categoria.servicos().listar(self.__gl.usuario_logado)