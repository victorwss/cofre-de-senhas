from ..db_test_util import applier_trans
from ..fixtures import (
    dbs, assert_db_ok,
    segredo_m1, dbz, lotr, star_wars, oppenheimer, star_trek,
    servicos_normal, servicos_normal2, servicos_admin, servicos_banido, servicos_usuario_nao_existe, servicos_nao_logado
)
from connection.trans import TransactedConnection
from cofre_de_senhas.erro import (
    UsuarioBanidoException, LoginExpiradoException, UsuarioNaoLogadoException, UsuarioNaoExisteException,
    CategoriaNaoExisteException,
    SegredoNaoExisteException,
    PermissaoNegadaException, ValorIncorretoException
)
from cofre_de_senhas.service import (
    ChaveSegredo, SegredoSemChave, SegredoComChave,
    ResultadoPesquisaDeSegredos, CabecalhoSegredoComChave,
    TipoSegredo, TipoPermissao
)
from cofre_de_senhas.service_impl import Servicos
from pytest import raises


c_m1         : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(segredo_m1 .pk_segredo), segredo_m1 .nome, segredo_m1 .descricao, TipoSegredo.ENCONTRAVEL )  # noqa: E201,E202,E203,E501
c_dbz        : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(dbz        .pk_segredo), dbz        .nome, dbz        .descricao, TipoSegredo.CONFIDENCIAL)  # noqa: E201,E202,E203,E501
c_lotr       : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(lotr       .pk_segredo), lotr       .nome, lotr       .descricao, TipoSegredo.ENCONTRAVEL )  # noqa: E201,E202,E203,E501
c_star_wars  : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(star_wars  .pk_segredo), star_wars  .nome, star_wars  .descricao, TipoSegredo.PUBLICO     )  # noqa: E201,E202,E203,E501
c_oppenheimer: CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(oppenheimer.pk_segredo), oppenheimer.nome, oppenheimer.descricao, TipoSegredo.CONFIDENCIAL)  # noqa: E201,E202,E203,E501
c_star_trek  : CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(star_trek  .pk_segredo), star_trek  .nome, star_trek  .descricao, TipoSegredo.PUBLICO     )  # noqa: E201,E202,E203,E501
c_star_trek_2: CabecalhoSegredoComChave = CabecalhoSegredoComChave(ChaveSegredo(star_trek  .pk_segredo), star_trek  .nome, star_trek  .descricao, TipoSegredo.CONFIDENCIAL)  # noqa: E201,E202,E203,E501


tudo                : ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([c_m1, c_dbz, c_lotr, c_star_wars, c_oppenheimer               ])  # noqa: E202,E203,E501
nem_tudo            : ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([c_m1, c_dbz, c_lotr, c_star_wars                              ])  # noqa: E202,E203,E501
tudo_com_algo_mais  : ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([c_m1, c_dbz, c_lotr, c_star_wars, c_oppenheimer, c_star_trek  ])  # noqa: E202,E203,E501
tudo_com_algo_mais_2: ResultadoPesquisaDeSegredos = ResultadoPesquisaDeSegredos([c_m1, c_dbz, c_lotr, c_star_wars, c_oppenheimer, c_star_trek_2])  # noqa: E202,E203,E501


def star_trek_data(
        *,
        unee: int = 0,
        cnee: int = 0,
        alt: int = 0,
        tipo: TipoSegredo = TipoSegredo.PUBLICO,
        harry_potter: TipoPermissao | None = TipoPermissao.PROPRIETARIO,
        hermione: TipoPermissao | None = TipoPermissao.LEITURA_E_ESCRITA
) -> SegredoSemChave:
    categorias: set[str] = {"API", "Produção", "QA"}
    if cnee == 1:
        categorias.add("Coisas boas feitas pela PRODAM")
    if cnee == 2:
        categorias.add("aplicação")
    usuarios: dict[str, TipoPermissao] = {}
    if harry_potter is not None:
        usuarios["Harry Potter"] = harry_potter
    if hermione is not None:
        usuarios["Hermione"] = hermione
    if unee == 1:
        usuarios["Papai Noel"] = TipoPermissao.LEITURA_E_ESCRITA
    if unee == 2:
        usuarios["DUMBLEDORE"] = TipoPermissao.LEITURA_E_ESCRITA
    props: dict[str, str] = {"Capitão": "Kirk", "Vulcano": "Spock"}
    if alt == 1:
        props["Nave"] = "USS Enterprise"
    return SegredoSemChave(star_trek.nome, star_trek.descricao, tipo, props, categorias, usuarios)


def test_nao_instanciar_servicos() -> None:
    from cofre_de_senhas.segredo.segredo import Servicos as SegredoServico
    with raises(Exception):
        SegredoServico()


def criar_segredo_normal(
        c: TransactedConnection,
        *,
        unee: int = 0,
        cnee: int = 0,
        alt: int = 0,
        tipo: TipoSegredo = TipoSegredo.PUBLICO,
        quem: int = 0,
        harry_potter: TipoPermissao | None = TipoPermissao.PROPRIETARIO,
        hermione: TipoPermissao | None = TipoPermissao.LEITURA_E_ESCRITA
) -> SegredoComChave:
    s1: Servicos = servicos_admin(c) if quem == 0 else servicos_normal(c) if quem == 1 else servicos_normal2(c)
    chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
    dados1: SegredoSemChave = star_trek_data(unee = unee, cnee = cnee, alt = alt, tipo = tipo, harry_potter = harry_potter, hermione = hermione)
    com_chave1: SegredoComChave = dados1.com_chave(chave)
    x1: SegredoComChave | BaseException = s1.segredo.criar(dados1)
    assert x1 == com_chave1
    return com_chave1


def verificar_segredo(c: TransactedConnection, com_chave: SegredoComChave) -> None:
    s2: Servicos = servicos_admin(c)
    x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(com_chave.chave)
    assert x2 == com_chave


def verificar_segredo_nao_existe(c: TransactedConnection, chave: ChaveSegredo) -> None:
    s2: Servicos = servicos_admin(c)
    x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(chave)
    assert isinstance(x2, SegredoNaoExisteException)


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
    chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
    com_chave: SegredoComChave = dados.com_chave(chave)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert x1 == com_chave

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo_com_algo_mais


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_ok2(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(tipo = TipoSegredo.CONFIDENCIAL)
    chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
    com_chave: SegredoComChave = dados.com_chave(chave)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert x1 == com_chave

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo_com_algo_mais_2


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_ok3(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    dados: SegredoSemChave = star_trek_data()
    chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
    com_chave: SegredoComChave = dados.com_chave(chave)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert x1 == com_chave

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo_com_algo_mais


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_VIE_1(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(harry_potter = TipoPermissao.SOMENTE_LEITURA)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, ValorIncorretoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_VIE_2(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(harry_potter = None)

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
    dados: SegredoSemChave = star_trek_data(unee = 1, harry_potter = TipoPermissao.SOMENTE_LEITURA)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, ValorIncorretoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo_LEE_antes_de_VIE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_usuario_nao_existe(c)
    dados: SegredoSemChave = star_trek_data(harry_potter = TipoPermissao.SOMENTE_LEITURA)

    x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
    assert isinstance(x1, LoginExpiradoException)

    s2: Servicos = servicos_admin(c)
    x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
    assert x2 == tudo


# Método buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE | _LEE


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_ok1(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s: Servicos = servicos_admin(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
    assert x == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_ok2(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s: Servicos = servicos_normal(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
    assert x == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_SNEE_invisivel(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.CONFIDENCIAL, quem = 2, hermione = TipoPermissao.PROPRIETARIO, harry_potter = None)

    s1: Servicos = servicos_normal(c)
    x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
    assert isinstance(x1, SegredoNaoExisteException)

    s2: Servicos = servicos_admin(c)
    x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(original.chave)
    assert x2 == original

    s3: Servicos = servicos_normal2(c)
    x3: SegredoComChave | BaseException = s3.segredo.buscar_por_chave(original.chave)
    assert x3 == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_parcialmente_invisivel(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.ENCONTRAVEL, quem = 2, hermione = TipoPermissao.PROPRIETARIO, harry_potter = None)

    s1: Servicos = servicos_normal(c)
    x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
    assert x1 == original.limpar_campos

    s2: Servicos = servicos_admin(c)
    x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(original.chave)
    assert x2 == original

    s3: Servicos = servicos_normal2(c)
    x3: SegredoComChave | BaseException = s3.segredo.buscar_por_chave(original.chave)
    assert x3 == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_publico(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.PUBLICO, quem = 2, hermione = TipoPermissao.PROPRIETARIO, harry_potter = None)

    s1: Servicos = servicos_normal(c)
    x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
    assert x1 == original

    s2: Servicos = servicos_admin(c)
    x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(original.chave)
    assert x2 == original

    s3: Servicos = servicos_normal2(c)
    x3: SegredoComChave | BaseException = s3.segredo.buscar_por_chave(original.chave)
    assert x3 == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_somente_leitura(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(
        c,
        tipo = TipoSegredo.CONFIDENCIAL,
        quem = 2,
        hermione = TipoPermissao.PROPRIETARIO,
        harry_potter = TipoPermissao.SOMENTE_LEITURA
    )

    s1: Servicos = servicos_normal(c)
    x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
    assert x1 == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_leitura_escrita(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(
        c,
        tipo = TipoSegredo.CONFIDENCIAL,
        quem = 2,
        hermione = TipoPermissao.PROPRIETARIO,
        harry_potter = TipoPermissao.LEITURA_E_ESCRITA
    )

    s1: Servicos = servicos_normal(c)
    x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
    assert x1 == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_dois_proprietarios(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(
        c,
        tipo = TipoSegredo.CONFIDENCIAL,
        quem = 2,
        hermione = TipoPermissao.PROPRIETARIO,
        harry_potter = TipoPermissao.PROPRIETARIO
    )

    s1: Servicos = servicos_normal(c)
    x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
    assert x1 == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_UNLE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s: Servicos = servicos_nao_logado(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
    assert isinstance(x, UsuarioNaoLogadoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_LEE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s: Servicos = servicos_usuario_nao_existe(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_UBE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s: Servicos = servicos_banido(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_SNEE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    s: Servicos = servicos_admin(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
    assert isinstance(x, SegredoNaoExisteException)


# Método buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_sem_logar_ok(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s: Servicos = servicos_banido(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave_sem_logar(original.chave)
    assert x == original


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_sem_logar_SNEE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    s: Servicos = servicos_banido(c)
    x: SegredoComChave | BaseException = s.segredo.buscar_por_chave_sem_logar(chave)
    assert isinstance(x, SegredoNaoExisteException)


# Método alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_ok_proprietario(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(alt = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert x1 is None

    verificar_segredo(c, com_chave)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_ok_admin(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_admin(c)
    dados: SegredoSemChave = star_trek_data(alt = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert x1 is None

    verificar_segredo(c, com_chave)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_ok_leitura_escrita(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, hermione = TipoPermissao.LEITURA_E_ESCRITA)

    s1: Servicos = servicos_normal2(c)
    dados: SegredoSemChave = star_trek_data(alt = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert x1 is None

    verificar_segredo(c, com_chave)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_SNEE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data()
    com_chave: SegredoComChave = dados.com_chave(chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo_nao_existe(c, chave)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_SNEE_invisivel(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.CONFIDENCIAL, hermione = None)

    s1: Servicos = servicos_normal2(c)
    dados: SegredoSemChave = star_trek_data(alt = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_PNE_somente_leitura(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, hermione = TipoPermissao.SOMENTE_LEITURA)

    s1: Servicos = servicos_normal2(c)
    dados: SegredoSemChave = star_trek_data(alt = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_PNE_sem_acesso(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.ENCONTRAVEL, hermione = None)

    s1: Servicos = servicos_normal2(c)
    dados: SegredoSemChave = star_trek_data(alt = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_PNE_alterando_permissao(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, hermione = TipoPermissao.LEITURA_E_ESCRITA)

    s1: Servicos = servicos_normal2(c)
    dados: SegredoSemChave = star_trek_data(alt = 1, hermione = TipoPermissao.PROPRIETARIO)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_UBE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_banido(c)
    dados: SegredoSemChave = star_trek_data()
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, UsuarioBanidoException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_LEE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_usuario_nao_existe(c)
    dados: SegredoSemChave = star_trek_data()
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, LoginExpiradoException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_UNLE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_nao_logado(c)
    dados: SegredoSemChave = star_trek_data()
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, UsuarioNaoLogadoException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_UNEE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(unee = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, UsuarioNaoExisteException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_CNEE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(cnee = 1)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, CategoriaNaoExisteException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_alterar_por_chave_VIE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_normal(c)
    dados: SegredoSemChave = star_trek_data(harry_potter = TipoPermissao.SOMENTE_LEITURA)
    com_chave: SegredoComChave = dados.com_chave(original.chave)

    x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
    assert isinstance(x1, ValorIncorretoException)

    verificar_segredo(c, original)


# Método excluir_por_chave(self, dados: ChaveSegredo) -> None | _UNLE | _UBE | _SNEE | _PNE | _LEE


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_ok_proprietario(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_normal(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert x1 is None

    verificar_segredo_nao_existe(c, original.chave)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_ok_admin(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_admin(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert x1 is None

    verificar_segredo_nao_existe(c, original.chave)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_ok_coproprietario(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, hermione = TipoPermissao.PROPRIETARIO)

    s1: Servicos = servicos_normal2(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert x1 is None

    verificar_segredo_nao_existe(c, original.chave)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_SNEE(c: TransactedConnection) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    s1: Servicos = servicos_admin(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(chave)
    assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo_nao_existe(c, chave)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_SNEE_oculto(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.CONFIDENCIAL, hermione = None)

    s1: Servicos = servicos_normal2(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_UBE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_banido(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert isinstance(x1, UsuarioBanidoException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_exlcuir_por_chave_LEE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_usuario_nao_existe(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert isinstance(x1, LoginExpiradoException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_UNLE(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c)

    s1: Servicos = servicos_nao_logado(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert isinstance(x1, UsuarioNaoLogadoException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_PNE_sem_relacao(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.ENCONTRAVEL, hermione = None)

    s1: Servicos = servicos_normal2(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(c, original)


@applier_trans(dbs, assert_db_ok)
def test_excluir_por_chave_PNE_fraco(c: TransactedConnection) -> None:
    original: SegredoComChave = criar_segredo_normal(c, tipo = TipoSegredo.CONFIDENCIAL, hermione = TipoPermissao.LEITURA_E_ESCRITA)

    s1: Servicos = servicos_normal2(c)
    x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
    assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(c, original)
