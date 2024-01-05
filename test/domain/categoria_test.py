from typing import override
from ..db_test_util import applier_trans
from ..dao.fixtures import dbs, assert_db_ok, harry_potter, voldemort, qa, desenvolvimento, lixo2, lixo4
from connection.trans import TransactedConnection
from cofre_de_senhas.erro import CategoriaNaoExisteException, PermissaoNegadaException, UsuarioNaoLogadoException, UsuarioNaoExisteException
from cofre_de_senhas.service import GerenciadorLogin, ChaveUsuario, NomeCategoria, CategoriaComChave, ChaveCategoria, UsuarioComChave
from cofre_de_senhas.service_impl import Servicos
from pytest import raises


class GerenciadorLoginNaoLogado(GerenciadorLogin):

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert False

    @override
    def logout(self) -> None:
        assert False

    # Pode lançar UsuarioNaoLogadoException.
    @property
    @override
    def usuario_logado(self) -> ChaveUsuario:
        raise UsuarioNaoLogadoException()


class GerenciadorLoginChave(GerenciadorLogin):

    def __init__(self, chave: ChaveUsuario) -> None:
        self.__chave: ChaveUsuario = chave

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert False

    @override
    def logout(self) -> None:
        assert False

    # Pode lançar UsuarioNaoLogadoException.
    @property
    @override
    def usuario_logado(self) -> ChaveUsuario:
        return self.__chave


def servicos_normal(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(harry_potter.pk_usuario)), c)


def servicos_especial(c: TransactedConnection, chave: int) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(chave)), c)


# Método buscar_por_nome


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)
    x: CategoriaComChave = s.categoria.buscar_por_nome(dados)
    assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_ok2(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(desenvolvimento.nome)
    x: CategoriaComChave = s.categoria.buscar_por_nome(dados)
    assert x == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(lixo4)

    with raises(CategoriaNaoExisteException):
        s.categoria.buscar_por_nome(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_case_sensitive(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome.lower())

    with raises(CategoriaNaoExisteException):
        s.categoria.buscar_por_nome(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_usuario_banido(c: TransactedConnection) -> None:
    s: Servicos = servicos_especial(c, voldemort.pk_usuario)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    with raises(PermissaoNegadaException):
        s.categoria.buscar_por_nome(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_usuario_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_especial(c, lixo2)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    with raises(UsuarioNaoExisteException):
        s.categoria.buscar_por_nome(dados)


# Método buscar_por_chave
