import hashlib
from typing import Generic, Self, TypeGuard
from decorators.for_all import for_all_methods
from dataclasses import dataclass, replace
from cofre_de_senhas.service import *
from cofre_de_senhas.bd.raiz import cf, log
from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
from cofre_de_senhas.categoria.categoria import Categoria
from cofre_de_senhas.usuario.usuario import Usuario, SenhaAlterada
from cofre_de_senhas.segredo.segredo import Segredo
from cofre_de_senhas.cofre_enum import NivelAcesso

class ServicoLogin:

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl = gl

    @property
    def logado(self) -> ChaveUsuario:
        return self.__gl.usuario_logado

@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class ServicoBDImpl(ServicoBD):

    def __init__(self) -> None:
        self.__dao = CofreDeSenhasDAOImpl(cf)

    def criar_bd(self, dados: LoginComSenha) -> None:
        self.__dao.criar_bd()
        Usuario.servicos().criar_admin(dados)

# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
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

    def trocar_senha(self, dados: NovaSenha) -> None:
        Usuario.servicos().redefinir_senha(self.__login.logado, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, dados: ResetLoginUsuario) -> str:
        return Usuario.servicos().resetar_senha_por_login(self.__login.logado, dados)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, dados: UsuarioComNivel) -> None:
        Usuario.servicos().alterar_nivel(self.__login.logado, dados)

    # Pode lançar UsuarioNaoExisteException
    def buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave:
        return Usuario.servicos().buscar_por_login(self.__login.logado, dados)

    # Pode lançar UsuarioNaoExisteException
    def buscar_por_chave(self, chave: ChaveUsuario) -> UsuarioComChave:
        return Usuario.servicos().buscar_existente_por_chave(self.__login.logado, chave)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar(self) -> ResultadoListaDeUsuarios:
        return Usuario.servicos().listar(self.__login.logado)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class ServicoSegredoImpl(ServicoSegredo):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__login: ServicoLogin = ServicoLogin(gl)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar(self, dados: SegredoSemChave) -> SegredoComChave:
        return Segredo.servicos().criar(self.__login.logado, dados)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    def alterar(self, dados: SegredoComChave) -> None:
        Segredo.servicos().alterar(self.__login.logado, dados)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    def excluir(self, dados: ChaveSegredo) -> None:
        Segredo.servicos().excluir(self.__login.logado, dados)

    def listar(self) -> ResultadoPesquisaDeSegredos:
        return Segredo.servicos().listar(self.__login.logado)

    # Pode lançar SegredoNaoExisteException
    def buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave:
        return Segredo.servicos().buscar(self.__login.logado, chave)

    # Pode lançar SegredoNaoExisteException
    def pesquisar(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        return Segredo.servicos().pesquisar(self.__login.logado, dados)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
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
    def renomear(self, dados: RenomeCategoria) -> None:
        Categoria.servicos().renomear(self.__login.logado, dados)

    # Pode lançar CategoriaNaoExisteException
    def excluir(self, dados: NomeCategoria) -> None:
        Categoria.servicos().excluir(self.__login.logado, dados)

    def listar(self) -> ResultadoListaDeCategorias:
        return Categoria.servicos().listar(self.__login.logado)