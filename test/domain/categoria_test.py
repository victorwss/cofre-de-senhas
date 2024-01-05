from typing import override
from ..db_test_util import applier_trans
from ..dao.fixtures import (
    dbs, assert_db_ok,
    harry_potter, dumbledore, voldemort,
    qa, desenvolvimento, millenium_falcon,
    lixo2, lixo4,
    nome_em_branco, nome_longo_demais, nome_millenium_falcon
)
from connection.trans import TransactedConnection
from cofre_de_senhas.erro import (
    CategoriaNaoExisteException, CategoriaJaExisteException,
    PermissaoNegadaException, UsuarioNaoLogadoException, UsuarioNaoExisteException,
    ValorIncorretoException
)
from cofre_de_senhas.service import GerenciadorLogin, ChaveUsuario, NomeCategoria, CategoriaComChave, ChaveCategoria, UsuarioComChave, RenomeCategoria
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


def servicos_admin(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(dumbledore.pk_usuario)), c)


def servicos_banido(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(voldemort.pk_usuario)), c)


def servicos_usuario_nao_existe(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(lixo2)), c)


# Método buscar_por_nome


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)
    x: CategoriaComChave = s.categoria.buscar_por_nome(dados)
    assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_ok2(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(desenvolvimento.nome)
    x: CategoriaComChave = s.categoria.buscar_por_nome(dados)
    assert x == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(lixo4)

    with raises(CategoriaNaoExisteException):
        s.categoria.buscar_por_nome(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_case_sensitive(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome.lower())

    with raises(CategoriaNaoExisteException):
        s.categoria.buscar_por_nome(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_usuario_banido(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    with raises(PermissaoNegadaException):
        s.categoria.buscar_por_nome(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_usuario_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    with raises(UsuarioNaoExisteException):
        s.categoria.buscar_por_nome(dados)


# Método buscar_por_chave


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)
    x: CategoriaComChave = s.categoria.buscar_por_chave(dados)
    assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_ok2(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveCategoria = ChaveCategoria(desenvolvimento.pk_categoria)
    x: CategoriaComChave = s.categoria.buscar_por_chave(dados)
    assert x == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveCategoria = ChaveCategoria(lixo2)

    with raises(CategoriaNaoExisteException):
        s.categoria.buscar_por_chave(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_usuario_banido(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

    with raises(PermissaoNegadaException):
        s.categoria.buscar_por_chave(dados)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_usuario_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

    with raises(UsuarioNaoExisteException):
        s.categoria.buscar_por_chave(dados)


# Método criar


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nova(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(nome_millenium_falcon.valor)
    x: CategoriaComChave = s.categoria.criar(dados)
    assert x == CategoriaComChave(ChaveCategoria(millenium_falcon.pk_categoria), millenium_falcon.nome)
    assert x == s.categoria.buscar_por_nome(dados)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_ja_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    with raises(CategoriaJaExisteException):
        s.categoria.criar(dados)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_usuario_nao_admin(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    with raises(PermissaoNegadaException):
        s.categoria.criar(dados)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_usuario_banido(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    with raises(PermissaoNegadaException):
        s.categoria.criar(dados)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nome_curto(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(nome_em_branco.valor)

    with raises(ValorIncorretoException):
        s.categoria.criar(dados)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nome_longo(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(nome_longo_demais.valor)

    with raises(ValorIncorretoException):
        s.categoria.criar(dados)


# Método renomear_por_nome


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_ok(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: RenomeCategoria = RenomeCategoria(qa.nome, nome_millenium_falcon.valor)
    s.categoria.renomear_por_nome(dados)

    with raises(PermissaoNegadaException):
        s.categoria.buscar_por_nome(NomeCategoria(qa.nome))

    x: CategoriaComChave = s.categoria.buscar_por_nome(NomeCategoria(nome_millenium_falcon.valor))
    assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), millenium_falcon.nome)
