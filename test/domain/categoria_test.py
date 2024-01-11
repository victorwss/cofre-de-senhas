from typing import override
from ..db_test_util import applier_trans
from ..dao.fixtures import (
    dbs, assert_db_ok,
    harry_potter, dumbledore, voldemort,
    banco_de_dados, aplicacao, servidor, api, producao, homologacao, desenvolvimento, qa, integracao,
    millenium_falcon, lixo2, lixo4, nome_em_branco, nome_longo_demais, nome_millenium_falcon
)
from connection.trans import TransactedConnection
from cofre_de_senhas.erro import (
    PermissaoNegadaException, UsuarioNaoLogadoException, UsuarioBanidoException, LoginExpiradoException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    ValorIncorretoException
)
from cofre_de_senhas.service import (
    GerenciadorLogin, ChaveUsuario, UsuarioComChave,
    NomeCategoria, CategoriaComChave, ChaveCategoria, RenomeCategoria, ResultadoListaDeCategorias
)
from cofre_de_senhas.service_impl import Servicos


tudo: ResultadoListaDeCategorias = ResultadoListaDeCategorias([
    CategoriaComChave(ChaveCategoria(banco_de_dados .pk_categoria), banco_de_dados .nome),
    CategoriaComChave(ChaveCategoria(aplicacao      .pk_categoria), aplicacao      .nome),
    CategoriaComChave(ChaveCategoria(servidor       .pk_categoria), servidor       .nome),
    CategoriaComChave(ChaveCategoria(api            .pk_categoria), api            .nome),
    CategoriaComChave(ChaveCategoria(producao       .pk_categoria), producao       .nome),
    CategoriaComChave(ChaveCategoria(homologacao    .pk_categoria), homologacao    .nome),
    CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome),
    CategoriaComChave(ChaveCategoria(qa             .pk_categoria), qa             .nome),
    CategoriaComChave(ChaveCategoria(integracao     .pk_categoria), integracao     .nome)
])


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


# Método buscar_por_nome(quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
    assert isinstance(x, CategoriaComChave)
    assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_ok2(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(desenvolvimento.nome)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
    assert isinstance(x, CategoriaComChave)
    assert x == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(lixo4)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
    assert isinstance(x, CategoriaNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_case_sensitive(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome.lower())

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
    assert isinstance(x, CategoriaNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_usuario_banido(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_nome_usuario_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
    assert isinstance(x, LoginExpiradoException)


# Método buscar_por_chave(quem_faz: ChaveUsuario, chave: ChaveCategoria) -> CategoriaComChave | _LEE | _UBE | _CNEE:


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
    assert isinstance(x, CategoriaComChave)
    assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_ok2(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveCategoria = ChaveCategoria(desenvolvimento.pk_categoria)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
    assert isinstance(x, CategoriaComChave)
    assert x == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_CNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveCategoria = ChaveCategoria(lixo2)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
    assert isinstance(x, CategoriaNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_por_chave_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

    x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
    assert isinstance(x, LoginExpiradoException)


# Método criar(quem_faz: ChaveUsuario, dados: NomeCategoria) -> CategoriaComChave | _LEE | _UBE | _PNE | _CJEE | _VIE


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(nome_millenium_falcon.valor)

    x: CategoriaComChave | BaseException = s.categoria.criar(dados)
    assert isinstance(x, CategoriaComChave)
    assert x == CategoriaComChave(ChaveCategoria(millenium_falcon.pk_categoria), millenium_falcon.nome)

    y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
    assert x == y


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_CJEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: CategoriaComChave | BaseException = s.categoria.criar(dados)
    assert isinstance(x, CategoriaJaExisteException)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_PNE(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: CategoriaComChave | BaseException = s.categoria.criar(dados)
    assert isinstance(x, PermissaoNegadaException)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: CategoriaComChave | BaseException = s.categoria.criar(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nome_curto_VIE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(nome_em_branco.valor)

    x: CategoriaComChave | BaseException = s.categoria.criar(dados)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nome_longo_VIE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: NomeCategoria = NomeCategoria(nome_longo_demais.valor)

    x: CategoriaComChave | BaseException = s.categoria.criar(dados)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: CategoriaComChave | BaseException = s.categoria.criar(dados)
    assert isinstance(x, LoginExpiradoException)


# Método renomear_por_nome(quem_faz: ChaveUsuario, dados: RenomeCategoria) -> None | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_ok(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: RenomeCategoria = RenomeCategoria(qa.nome, nome_millenium_falcon.valor)

    x: None | BaseException = s.categoria.renomear_por_nome(dados)
    assert x is None

    z: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(qa.nome))
    assert isinstance(z, CategoriaNaoExisteException)

    y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(nome_millenium_falcon.valor))
    assert isinstance(y, CategoriaComChave)
    assert y == CategoriaComChave(ChaveCategoria(qa.pk_categoria), millenium_falcon.nome)


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: RenomeCategoria = RenomeCategoria(qa.nome, nome_millenium_falcon.valor)

    x: None | BaseException = s.categoria.renomear_por_nome(dados)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: RenomeCategoria = RenomeCategoria(qa.nome, nome_millenium_falcon.valor)

    x: None | BaseException = s.categoria.renomear_por_nome(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_PNE(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: RenomeCategoria = RenomeCategoria(qa.nome, nome_millenium_falcon.valor)

    x: None | BaseException = s.categoria.renomear_por_nome(dados)
    assert isinstance(x, PermissaoNegadaException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_CJEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: RenomeCategoria = RenomeCategoria(qa.nome, desenvolvimento.nome)

    x: None | BaseException = s.categoria.renomear_por_nome(dados)
    assert isinstance(x, CategoriaJaExisteException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_CNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: RenomeCategoria = RenomeCategoria(nome_millenium_falcon.valor, nome_millenium_falcon.valor + "x")

    x: None | BaseException = s.categoria.renomear_por_nome(dados)
    assert isinstance(x, CategoriaNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_categoria_CNEE_antes_de_CJEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: RenomeCategoria = RenomeCategoria(nome_millenium_falcon.valor, qa.nome)

    x: None | BaseException = s.categoria.renomear_por_nome(dados)
    assert isinstance(x, CategoriaNaoExisteException)


# Método excluir_por_nome(quem_faz: ChaveUsuario, dados: NomeCategoria) -> None | _UBE | _PNE | _CNEE | _LEE


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados1: NomeCategoria = NomeCategoria(qa.nome)

    x: None | BaseException = s.categoria.excluir_por_nome(dados1)
    assert x is None

    y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados1)
    assert isinstance(y, CategoriaNaoExisteException)

    dados2: NomeCategoria = NomeCategoria(desenvolvimento.nome)
    z: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados2)
    assert isinstance(z, CategoriaComChave)
    assert z == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: None | BaseException = s.categoria.excluir_por_nome(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_PNE(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: None | BaseException = s.categoria.excluir_por_nome(dados)
    assert isinstance(x, PermissaoNegadaException)


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_CNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: NomeCategoria = NomeCategoria(nome_millenium_falcon.valor)

    x: None | BaseException = s.categoria.excluir_por_nome(dados)
    assert isinstance(x, CategoriaNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: NomeCategoria = NomeCategoria(qa.nome)

    x: None | BaseException = s.categoria.excluir_por_nome(dados)
    assert isinstance(x, LoginExpiradoException)


# Método listar(quem_faz: ChaveUsuario) -> ResultadoListaDeCategorias | _LEE | _UBE


@applier_trans(dbs, assert_db_ok)
def test_listar_categoria_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)

    x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
    assert x == tudo


@applier_trans(dbs, assert_db_ok)
def test_listar_categoria_ok2(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)

    x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
    assert x == tudo


@applier_trans(dbs, assert_db_ok)
def test_listar_categoria_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)

    x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_listar_categoria_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)

    x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
    assert isinstance(x, UsuarioBanidoException)