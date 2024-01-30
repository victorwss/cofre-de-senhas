from ..db_test_util import applier_trans
from ..fixtures import (
    dbs, assert_db_ok,
    segredo_m1, dbz, lotr, star_wars, star_trek, openheimer,
    servicos_normal, servicos_admin, servicos_banido, servicos_usuario_nao_existe, servicos_nao_logado
)
from connection.trans import TransactedConnection
from cofre_de_senhas.erro import (
    PermissaoNegadaException, UsuarioBanidoException, LoginExpiradoException, UsuarioNaoLogadoException
)
from cofre_de_senhas.service import ChaveSegredo, ResultadoPesquisaDeSegredos, SegredoComChave, TipoSegredo, CabecalhoSegredoComChave
from cofre_de_senhas.service_impl import Servicos
from pytest import raises


tudo: ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([
    CabecalhoSegredoComChave(ChaveSegredo(segredo_m1.pk_segredo), segredo_m1.nome, segredo_m1.descricao, TipoSegredo.ENCONTRAVEL ),  # noqa: E201,E202,E203
    CabecalhoSegredoComChave(ChaveSegredo(dbz       .pk_segredo), dbz       .nome, dbz       .descricao, TipoSegredo.CONFIDENCIAL),  # noqa: E201,E202,E203
    CabecalhoSegredoComChave(ChaveSegredo(lotr      .pk_segredo), lotr      .nome, lotr      .descricao, TipoSegredo.ENCONTRAVEL ),  # noqa: E201,E202,E203
    CabecalhoSegredoComChave(ChaveSegredo(star_wars .pk_segredo), star_wars .nome, star_wars .descricao, TipoSegredo.PUBLICO     ),  # noqa: E201,E202,E203
    CabecalhoSegredoComChave(ChaveSegredo(openheimer.pk_segredo), openheimer.nome, openheimer.descricao, TipoSegredo.CONFIDENCIAL),  # noqa: E201,E202,E203
])

nem_tudo: ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([
    CabecalhoSegredoComChave(ChaveSegredo(segredo_m1.pk_segredo), segredo_m1.nome, segredo_m1.descricao, TipoSegredo.ENCONTRAVEL ),  # noqa: E201,E202,E203
    CabecalhoSegredoComChave(ChaveSegredo(dbz       .pk_segredo), dbz       .nome, dbz       .descricao, TipoSegredo.CONFIDENCIAL),  # noqa: E201,E202,E203
    CabecalhoSegredoComChave(ChaveSegredo(lotr      .pk_segredo), lotr      .nome, lotr      .descricao, TipoSegredo.ENCONTRAVEL ),  # noqa: E201,E202,E203
    CabecalhoSegredoComChave(ChaveSegredo(star_wars .pk_segredo), star_wars .nome, star_wars .descricao, TipoSegredo.PUBLICO     ),  # noqa: E201,E202,E203
])


def test_nao_instanciar_servicos() -> None:
    from cofre_de_senhas.segredo.segredo import Servicos as SegredoServico
    with raises(Exception):
        SegredoServico()


# Método listar(self) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _LEE


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_ok1(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert x == nem_tudo


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_ok2(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert x == tudo


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert isinstance(x, UsuarioNaoLogadoException)
