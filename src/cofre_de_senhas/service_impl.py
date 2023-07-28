import hashlib
from typing import Generic, Self, TypeGuard
from decorators.for_all import for_all_methods
from dataclasses import dataclass, replace
from cofre_de_senhas.service import *
from cofre_de_senhas.bd.raiz import Raiz, log
from cofre_de_senhas.dao import CofreDeSenhasDAO
from cofre_de_senhas.categoria.categoria import Categoria
from cofre_de_senhas.usuario.usuario import Usuario, SenhaAlterada
from cofre_de_senhas.segredo.segredo import Segredo

class ServicoLogin:

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl: GerenciadorLogin = gl

    @property
    def logado(self) -> ChaveUsuario:
        return self.__gl.usuario_logado

@for_all_methods(log.trace)
@for_all_methods(Raiz.transact)
class ServicoBDImpl(ServicoBD):

    def criar_bd(self, dados: LoginComSenha) -> None:
        CofreDeSenhasDAO.instance().criar_bd()
        Usuario.servicos().criar_admin(dados)

# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(Raiz.transact)
class ServicoUsuarioImpl(ServicoUsuario):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__login: ServicoLogin = ServicoLogin(gl)
        self.__gl: GerenciadorLogin = gl

    # Pode lançar SenhaErradaException
    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave:
        u: UsuarioComChave = Usuario.servicos().login(quem_faz)
        self.__gl.login(u)
        return u

    def logout(self) -> None:
        self.__gl.logout()

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar(self, dados: UsuarioNovo) -> UsuarioComChave:
        return Usuario.servicos().criar(self.__login.logado, dados)

    def trocar_senha_por_chave(self, dados: TrocaSenha) -> None:
        Usuario.servicos().trocar_senha_por_chave(self.__login.logado, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada:
        return Usuario.servicos().resetar_senha_por_login(self.__login.logado, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None:
        Usuario.servicos().alterar_nivel_por_login(self.__login.logado, dados)

    # Pode lançar UsuarioNaoExisteException
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave:
        return Usuario.servicos().buscar_por_login(self.__login.logado, dados)

    # Pode lançar UsuarioNaoExisteException
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave:
        return Usuario.servicos().buscar_por_chave(self.__login.logado, chave)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar(self) -> ResultadoListaDeUsuarios:
        return Usuario.servicos().listar(self.__login.logado)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(Raiz.transact)
class ServicoSegredoImpl(ServicoSegredo):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__login: ServicoLogin = ServicoLogin(gl)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar(self, dados: SegredoSemChave) -> SegredoComChave:
        return Segredo.servicos().criar(self.__login.logado, dados)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    def alterar_por_chave(self, dados: SegredoComChave) -> None:
        Segredo.servicos().alterar_por_chave(self.__login.logado, dados)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    def excluir_por_chave(self, dados: ChaveSegredo) -> None:
        Segredo.servicos().excluir_por_chave(self.__login.logado, dados)

    def listar(self) -> ResultadoPesquisaDeSegredos:
        return Segredo.servicos().listar(self.__login.logado)

    # Pode lançar SegredoNaoExisteException
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave:
        return Segredo.servicos().buscar(self.__login.logado, chave)

    # Pode lançar SegredoNaoExisteException
    def buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave:
        return Segredo.servicos().buscar_sem_logar(chave)

    # Pode lançar SegredoNaoExisteException
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        return Segredo.servicos().pesquisar(self.__login.logado, dados)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(Raiz.transact)
class ServicoCategoriaImpl(ServicoCategoria):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__login: ServicoLogin = ServicoLogin(gl)

    # Pode lançar CategoriaNaoExisteException
    def buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave:
        return Categoria.servicos().buscar_por_nome(self.__login.logado, dados)

    # Pode lançar CategoriaNaoExisteException
    def buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave:
        return Categoria.servicos().buscar_por_chave(self.__login.logado, chave)

    # Pode lançar CategoriaJaExisteException
    def criar(self, dados: NomeCategoria) -> CategoriaComChave:
        return Categoria.servicos().criar(self.__login.logado, dados)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_por_nome(self, dados: RenomeCategoria) -> None:
        Categoria.servicos().renomear_por_nome(self.__login.logado, dados)

    # Pode lançar CategoriaNaoExisteException
    def excluir_por_nome(self, dados: NomeCategoria) -> None:
        Categoria.servicos().excluir_por_nome(self.__login.logado, dados)

    def listar(self) -> ResultadoListaDeCategorias:
        return Categoria.servicos().listar(self.__login.logado)