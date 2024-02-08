from ..db_test_util import applier_trans
from ..fixtures import (
    dbs, assert_db_ok,
    segredo_m1, dbz, lotr, star_wars, openheimer, star_trek,
    servicos_normal, servicos_admin, servicos_banido, servicos_usuario_nao_existe, servicos_nao_logado
)
from connection.trans import TransactedConnection
from cofre_de_senhas.erro import (
    UsuarioBanidoException, LoginExpiradoException, UsuarioNaoLogadoException, UsuarioNaoExisteException,
    CategoriaNaoExisteException,
    SegredoNaoExisteException,
    ValorIncorretoException
)
from cofre_de_senhas.service import (
    ChaveSegredo, SegredoSemChave, SegredoComChave,
    ResultadoPesquisaDeSegredos, CabecalhoSegredoComChave,
    TipoSegredo, TipoPermissao
)
from cofre_de_senhas.service_impl import Servicos
from pytest import raises


c_m1        : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(segredo_m1.pk_segredo), segredo_m1.nome, segredo_m1.descricao, TipoSegredo.ENCONTRAVEL )  # noqa: E201,E202,E203
c_dbz       : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(dbz       .pk_segredo), dbz       .nome, dbz       .descricao, TipoSegredo.CONFIDENCIAL)  # noqa: E201,E202,E203
c_lotr      : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(lotr      .pk_segredo), lotr      .nome, lotr      .descricao, TipoSegredo.ENCONTRAVEL )  # noqa: E201,E202,E203
c_star_wars : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(star_wars .pk_segredo), star_wars .nome, star_wars .descricao, TipoSegredo.PUBLICO     )  # noqa: E201,E202,E203
c_openheimer: CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(openheimer.pk_segredo), openheimer.nome, openheimer.descricao, TipoSegredo.CONFIDENCIAL)  # noqa: E201,E202,E203
c_star_trek : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(star_trek .pk_segredo), star_trek .nome, star_trek .descricao, TipoSegredo.PUBLICO     )  # noqa: E201,E202,E203

tudo              : ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([c_m1, c_dbz, c_lotr, c_star_wars, c_openheimer             ])
nem_tudo          : ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([c_m1, c_dbz, c_lotr, c_star_wars                           ])
tudo_com_algo_mais: ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([c_m1, c_dbz, c_lotr, c_star_wars, c_openheimer, c_star_trek])


def star_trek_data(unee: int = 0, cnee: int = 0, vie: int = 0) -> SegredoSemChave:
    categorias: set[str] = {"API", "Produção", "QA"}
    if cnee == 1:
        categorias.add("Coisas boas feitas pela PRODAM")
    if cnee == 2:
        categorias.add("aplicação")
    usuarios: dict[str, TipoPermissao] = {"Harry Potter": TipoPermissao.PROPRIETARIO, "Hermione": TipoPermissao.LEITURA_E_ESCRITA}
    if unee == 1:
        usuarios["Papai Noel"] = TipoPermissao.LEITURA_E_ESCRITA
    if unee == 2:
        usuarios["DUMBLEDORE"] = TipoPermissao.LEITURA_E_ESCRITA
    if vie == 1:
        usuarios["Harry Potter"] = TipoPermissao.LEITURA_E_ESCRITA
    if vie == 2:
        del usuarios["Harry Potter"]
    props: dict[str, str] = {"Capitão": "Kirk", "Vulcano": "Spock"}
    return SegredoSemChave(star_trek.nome, star_trek.descricao, TipoSegredo.PUBLICO, props, categorias, usuarios)


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
def test_listar_segredos_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)

    x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
    assert isinstance(x, UsuarioNaoLogadoException)


# Método criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE | _PNE | _LEE | _VIE


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_ok1(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data()
    com_chave: SegredoComChave = dados.com_chave(ChaveSegredo(star_trek.pk_segredo))

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert x1 == com_chave

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo_com_algo_mais


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_ok2(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    dados: SegredoSemChave = star_trek_data()
    com_chave: SegredoComChave = dados.com_chave(ChaveSegredo(star_trek.pk_segredo))

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert x1 == com_chave

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo_com_algo_mais


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_VIE_1(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(vie = 1)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, ValorIncorretoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_VIE_2(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(vie = 2)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, ValorIncorretoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo



@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_UBE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_banido(c)
    dados: SegredoSemChave = star_trek_data()

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, UsuarioBanidoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_LEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_usuario_nao_existe(c)
    dados: SegredoSemChave = star_trek_data()

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, LoginExpiradoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_UNLE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_nao_logado(c)
    dados: SegredoSemChave = star_trek_data()

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, UsuarioNaoLogadoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_UNEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(unee = 1)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, UsuarioNaoExisteException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_UNEE_case_sensitive(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(unee = 2)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, UsuarioNaoExisteException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_CNEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(cnee = 1)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, CategoriaNaoExisteException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_CNEE_case_sensitive(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(cnee = 2)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, CategoriaNaoExisteException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_UNEE_antes_de_CNEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(unee = 1, cnee = 1)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, UsuarioNaoExisteException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_VIE_antes_de_UNEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(unee = 1, vie = 1)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, ValorIncorretoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_LEE_antes_de_VIE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_usuario_nao_existe(c)
    dados: SegredoSemChave = star_trek_data(vie = 1)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, LoginExpiradoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


# Método buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE | _LEE


# @applier_trans(dbs, assert_db_ok)
# def test_buscar_por_chave_ok1(c: TransactedConnection) -> None:
#     chave: ChaveSegredo = ChaveSegredo(star_wars.pk_segredo)
#     s: Servicos = servicos_normal(c)
#     x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
#     assert x == star_wars


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_UNLE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(star_wars.pk_segredo)
    s: Servicos = servicos_nao_logado(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
    assert isinstance(x, UsuarioNaoLogadoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_LEE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(star_wars.pk_segredo)
    s: Servicos = servicos_usuario_nao_existe(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_UBE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(star_wars.pk_segredo)
    s: Servicos = servicos_banido(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_SNEE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
    s: Servicos = servicos_admin(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
    assert isinstance(x, SegredoNaoExisteException)


# Método alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_SNEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data()
    chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
    com_chave: SegredoComChave = dados.com_chave(chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, SegredoNaoExisteException)

    s2: Servicos = servicos_admin(c)
    x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(chave)
    assert isinstance(x2, SegredoNaoExisteException)