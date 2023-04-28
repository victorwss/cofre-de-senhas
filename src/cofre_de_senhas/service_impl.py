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

class ServicoLogin:

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__gl = gl

    @property
    def usuario_logado(self) -> Usuario:
        return Usuario.encontrar_existente_por_chave(self.__gl.usuario_logado).permitir_acesso()

    @property
    def admin_logado(self) -> Usuario:
        return self.usuario_logado.permitir_admin()

@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class ServicoBDImpl(ServicoBD):

    def __init__(self) -> None:
        self.__dao = CofreDeSenhasDAOImpl(cf)

    def criar_bd(self) -> None:
        self.__dao.criar_bd()

# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class ServicoUsuarioImpl(ServicoUsuario):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__login: ServicoLogin = ServicoLogin(gl)
        self.__gl: GerenciadorLogin = gl

    # Pode lançar SenhaErradaException
    def login(self, quem_faz: LoginUsuario) -> None:
        self.__gl.login(Usuario.fazer_login(quem_faz).chave)

    def logout(self) -> None:
        self.__gl.logout()

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar_usuario(self, dados: UsuarioNovo) -> None:
        self.__login.admin_logado
        Usuario.criar(dados.login, dados.nivel_acesso, dados.senha)

    def trocar_senha(self, dados: NovaSenha) -> None:
        self.__login.usuario_logado.trocar_senha(dados.senha)

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, dados: ResetLoginUsuario) -> str:
        self.__login.admin_logado
        return Usuario.encontrar_existente_por_login(dados.login).resetar_senha().nova_senha

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, dados: UsuarioComNivel) -> None:
        self.__login.admin_logado
        Usuario.encontrar_existente_por_login(dados.login).alterar_nivel_de_acesso(dados.nivel_acesso)

    # Pode lançar UsuarioNaoExisteException
    def buscar_usuario_por_login(self, login: str) -> UsuarioComChave:
        self.__login.usuario_logado
        return Usuario.encontrar_existente_por_login(login).up

    # Pode lançar UsuarioNaoExisteException
    def buscar_usuario_por_chave(self, chave: UsuarioChave) -> UsuarioComChave:
        self.__login.usuario_logado
        return Usuario.encontrar_existente_por_chave(chave).up

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar_usuarios(self) -> ResultadoListaDeUsuarios:
        self.__login.usuario_logado
        return ResultadoListaDeUsuarios([x.up for x in Usuario.listar()])

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class ServicoSegredoImpl(ServicoSegredo):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__login: ServicoLogin = ServicoLogin(gl)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar_segredo(self, dados: SegredoSemChave) -> None:
        quem_faz: Usuario = self.__login.usuario_logado
        Segredo.criar(quem_faz, dados)

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    def alterar_segredo(self, dados: SegredoComChave) -> None:
        self.__login.usuario_logado
        Segredo.alterar_segredo(dados)
        #Categoria.encontrar_existente_por_nome(dados.antigo).renomear(dados.novo)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    def excluir_segredo(self, dados: SegredoChave) -> None:
        quem_faz: Usuario = self.__login.usuario_logado
        Segredo.excluir_segredo(quem_faz, dados)

    def listar_segredos(self) -> ResultadoPesquisaDeSegredos:
        quem_faz: Usuario = self.__login.usuario_logado
        return ResultadoPesquisaDeSegredos([x.up for x in Segredo.listar_segredos(quem_faz)])

    # Pode lançar SegredoNaoExisteException
    def buscar_segredo_por_chave(self, chave: SegredoChave) -> SegredoComChave:
        quem_faz: Usuario = self.__login.usuario_logado
        return Segredo.buscar_segredo(quem_faz, chave)

    # Não implementado ainda! Pode lançar SegredoNaoExisteException
    def pesquisar_segredos(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        quem_faz: Usuario = self.__login.usuario_logado
        return Segredo.pesquisar_segredos(quem_faz, dados)

# Todos os métodos podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class ServicoCategoriaImpl(ServicoCategoria):

    def __init__(self, gl: GerenciadorLogin) -> None:
        self.__login: ServicoLogin = ServicoLogin(gl)

    # Pode lançar CategoriaNaoExisteException
    def buscar_categoria_por_nome(self, nome: str) -> CategoriaComChave:
        self.__login.usuario_logado
        return Categoria.encontrar_existente_por_nome(nome).up

    # Pode lançar CategoriaNaoExisteException
    def buscar_categoria_por_chave(self, chave: CategoriaChave) -> CategoriaComChave:
        self.__login.usuario_logado
        return Categoria.encontrar_existente_por_chave(chave).up

    # Pode lançar CategoriaJaExisteException
    def criar_categoria(self, dados: NomeCategoria) -> None:
        self.__login.admin_logado
        Categoria.criar(dados.nome)

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_categoria(self, dados: RenomeCategoria) -> None:
        self.__login.admin_logado
        Categoria.encontrar_existente_por_nome(dados.antigo).renomear(dados.novo)

    # Pode lançar CategoriaNaoExisteException
    def excluir_categoria(self, dados: NomeCategoria) -> None:
        self.__login.admin_logado
        Categoria.encontrar_existente_por_nome(dados.nome).excluir()

    def listar_categorias(self) -> ResultadoListaDeCategorias:
        self.__login.usuario_logado
        return ResultadoListaDeCategorias([x.up for x in Categoria.listar()])