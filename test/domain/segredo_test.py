from ..fixtures import (
    applier_ctx, ContextoOperacao,
    segredo_m1, dbz, lotr, star_wars, oppenheimer, star_trek
)
from cofre_de_senhas.erro import (
    UsuarioBanidoException, LoginExpiradoException, UsuarioNaoLogadoException, UsuarioNaoExisteException,
    CategoriaNaoExisteException,
    SegredoNaoExisteException,
    PermissaoNegadaException, ValorIncorretoException
)
from cofre_de_senhas.service import (
    Servicos,
    ChaveSegredo, SegredoSemChave, SegredoComChave,
    ResultadoPesquisaDeSegredos, CabecalhoSegredoComChave,
    TipoSegredo, TipoPermissao
)


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
        rep: int = 0,
        tipo: TipoSegredo = TipoSegredo.PUBLICO,
        harry_potter: TipoPermissao | None = TipoPermissao.PROPRIETARIO,
        hermione: TipoPermissao | None = TipoPermissao.LEITURA_E_ESCRITA
) -> SegredoSemChave:
    categorias: list[str] = ["API", "Produção", "QA"]
    if cnee == 1:
        categorias.append("Coisas boas feitas pela PRODAM")
    if cnee == 2:
        categorias.append("aplicação")
    if rep == 1:
        categorias.append("QA")
    if rep == 2:
        categorias.reverse()
    if rep == 3:
        categorias.append("QA")
        categorias.reverse()
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


def criar_segredo_normal(
        ctx: ContextoOperacao,
        *,
        unee: int = 0,
        cnee: int = 0,
        alt: int = 0,
        tipo: TipoSegredo = TipoSegredo.PUBLICO,
        quem: int = 0,
        harry_potter: TipoPermissao | None = TipoPermissao.PROPRIETARIO,
        hermione: TipoPermissao | None = TipoPermissao.LEITURA_E_ESCRITA
) -> SegredoComChave:
    with (ctx.servicos_admin() if quem == 0 else ctx.servicos_normal() if quem == 1 else ctx.servicos_normal2()) as r:
        s1: Servicos = r.servicos
        chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
        dados1: SegredoSemChave = star_trek_data(unee = unee, cnee = cnee, alt = alt, tipo = tipo, harry_potter = harry_potter, hermione = hermione)
        com_chave1: SegredoComChave = dados1.com_chave(chave)
        x1: SegredoComChave | BaseException = s1.segredo.criar(dados1)
        assert x1 == com_chave1
        return com_chave1


def verificar_segredo(ctx: ContextoOperacao, com_chave: SegredoComChave) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(com_chave.chave)
        assert x == com_chave


def verificar_segredo_nao_existe(ctx: ContextoOperacao, chave: ChaveSegredo) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
        assert isinstance(x, SegredoNaoExisteException)


# Método listar(self) -> ResultadoPesquisaDeSegredos | _UNLE | _UBE | _LEE


@applier_ctx
def test_listar_segredos_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
        assert x == nem_tudo


@applier_ctx
def test_listar_segredos_ok2(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
        assert x == tudo


@applier_ctx
def test_listar_segredos_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_listar_segredos_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_listar_segredos_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        x: ResultadoPesquisaDeSegredos | BaseException = s.segredo.listar()
        assert isinstance(x, UsuarioNaoLogadoException)


# Método criar(self, dados: SegredoSemChave) -> SegredoComChave | _UNLE | _UBE | _UNEE | _CNEE | _PNE | _LEE | _VIE


@applier_ctx
def test_criar_segredo_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()
        chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
        com_chave: SegredoComChave = dados.com_chave(chave)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert x1 == com_chave

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo_com_algo_mais


@applier_ctx
def test_criar_segredo_ok2(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(tipo = TipoSegredo.CONFIDENCIAL)
        chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
        com_chave: SegredoComChave = dados.com_chave(chave)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert x1 == com_chave

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo_com_algo_mais_2


@applier_ctx
def test_criar_segredo_ok3(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()
        chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
        com_chave: SegredoComChave = dados.com_chave(chave)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert x1 == com_chave

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo_com_algo_mais


@applier_ctx
def test_criar_segredo_ok4(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(rep = 2)
        chave: ChaveSegredo = ChaveSegredo(star_trek.pk_segredo)
        com_chave: SegredoComChave = dados.com_chave(chave)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert x1 == star_trek_data().com_chave(chave)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo_com_algo_mais


@applier_ctx
def test_criar_segredo_VIE_1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(harry_potter = TipoPermissao.SOMENTE_LEITURA)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, ValorIncorretoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_VIE_2(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(harry_potter = None)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, ValorIncorretoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_VIE_3(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(rep = 1)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, ValorIncorretoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_VIE_4(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(rep = 3)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, ValorIncorretoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, UsuarioBanidoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, LoginExpiradoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, UsuarioNaoLogadoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_UNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(unee = 1)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, UsuarioNaoExisteException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_UNEE_case_sensitive(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(unee = 2)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, UsuarioNaoExisteException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_CNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(cnee = 1)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, CategoriaNaoExisteException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_CNEE_case_sensitive(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(cnee = 2)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, CategoriaNaoExisteException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_UNEE_antes_de_CNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(unee = 1, cnee = 1)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, UsuarioNaoExisteException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_VIE_antes_de_UNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(unee = 1, harry_potter = TipoPermissao.SOMENTE_LEITURA)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, ValorIncorretoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


@applier_ctx
def test_criar_segredo_LEE_antes_de_VIE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(harry_potter = TipoPermissao.SOMENTE_LEITURA)

        x1: SegredoComChave | BaseException = s1.segredo.criar(dados)
        assert isinstance(x1, LoginExpiradoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: ResultadoPesquisaDeSegredos | BaseException = s2.segredo.listar()
        assert x2 == tudo


# Método buscar_por_chave(self, chave: ChaveSegredo) -> SegredoComChave | _UNLE | _UBE | _SNEE | _LEE


@applier_ctx
def test_buscar_por_chave_ok1(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
        assert x == original


@applier_ctx
def test_buscar_por_chave_ok2(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
        assert x == original


@applier_ctx
def test_buscar_por_chave_SNEE_invisivel(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.CONFIDENCIAL, quem = 2, hermione = TipoPermissao.PROPRIETARIO, harry_potter = None)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
        assert isinstance(x1, SegredoNaoExisteException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(original.chave)
        assert x2 == original

    with ctx.servicos_normal2() as r:
        s3: Servicos = r.servicos
        x3: SegredoComChave | BaseException = s3.segredo.buscar_por_chave(original.chave)
        assert x3 == original


@applier_ctx
def test_buscar_por_chave_parcialmente_invisivel(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.ENCONTRAVEL, quem = 2, hermione = TipoPermissao.PROPRIETARIO, harry_potter = None)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
        assert x1 == original.limpar_campos

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(original.chave)
        assert x2 == original

    with ctx.servicos_normal2() as r:
        s3: Servicos = r.servicos
        x3: SegredoComChave | BaseException = s3.segredo.buscar_por_chave(original.chave)
        assert x3 == original


@applier_ctx
def test_buscar_por_chave_publico(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.PUBLICO, quem = 2, hermione = TipoPermissao.PROPRIETARIO, harry_potter = None)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
        assert x1 == original

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        x2: SegredoComChave | BaseException = s2.segredo.buscar_por_chave(original.chave)
        assert x2 == original

    with ctx.servicos_normal2() as r:
        s3: Servicos = r.servicos
        x3: SegredoComChave | BaseException = s3.segredo.buscar_por_chave(original.chave)
        assert x3 == original


@applier_ctx
def test_buscar_por_chave_somente_leitura(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(
        ctx,
        tipo = TipoSegredo.CONFIDENCIAL,
        quem = 2,
        hermione = TipoPermissao.PROPRIETARIO,
        harry_potter = TipoPermissao.SOMENTE_LEITURA
    )

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
        assert x1 == original


@applier_ctx
def test_buscar_por_chave_leitura_escrita(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(
        ctx,
        tipo = TipoSegredo.CONFIDENCIAL,
        quem = 2,
        hermione = TipoPermissao.PROPRIETARIO,
        harry_potter = TipoPermissao.LEITURA_E_ESCRITA
    )

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
        assert x1 == original


@applier_ctx
def test_buscar_por_chave_dois_proprietarios(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(
        ctx,
        tipo = TipoSegredo.CONFIDENCIAL,
        quem = 2,
        hermione = TipoPermissao.PROPRIETARIO,
        harry_potter = TipoPermissao.PROPRIETARIO
    )

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x1: SegredoComChave | BaseException = s1.segredo.buscar_por_chave(original.chave)
        assert x1 == original


@applier_ctx
def test_buscar_por_chave_UNLE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
        assert isinstance(x, UsuarioNaoLogadoException)


@applier_ctx
def test_buscar_por_chave_LEE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_buscar_por_chave_UBE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(original.chave)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_buscar_por_chave_SNEE(ctx: ContextoOperacao) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.segredo.buscar_por_chave(chave)
        assert isinstance(x, SegredoNaoExisteException)


# Método buscar_por_chave_sem_logar(self, chave: ChaveSegredo) -> SegredoComChave | _SNEE


@applier_ctx
def test_buscar_por_chave_sem_logar_ok(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.bd.buscar_por_chave_sem_logar(original.chave)
        assert x == original


@applier_ctx
def test_buscar_por_chave_sem_logar_SNEE(ctx: ContextoOperacao) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        x: SegredoComChave | BaseException = s.bd.buscar_por_chave_sem_logar(chave)
        assert isinstance(x, SegredoNaoExisteException)


# Método alterar_por_chave(self, dados: SegredoComChave) -> None | _UNLE | _UNEE | _UBE | _SNEE | _PNE | _CNEE | _LEE


@applier_ctx
def test_alterar_por_chave_ok_proprietario(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert x1 is None

    verificar_segredo(ctx, com_chave)


@applier_ctx
def test_alterar_por_chave_ok_admin(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert x1 is None

    verificar_segredo(ctx, com_chave)


@applier_ctx
def test_alterar_por_chave_ok_leitura_escrita(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, hermione = TipoPermissao.LEITURA_E_ESCRITA)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert x1 is None

    verificar_segredo(ctx, com_chave)


@applier_ctx
def test_alterar_por_chave_ok_ordem(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1, rep = 2)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert x1 is None

    verificar_segredo(ctx, star_trek_data(alt = 1).com_chave(original.chave))


@applier_ctx
def test_alterar_por_chave_SNEE(ctx: ContextoOperacao) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()
        com_chave: SegredoComChave = dados.com_chave(chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo_nao_existe(ctx, chave)


@applier_ctx
def test_alterar_por_chave_SNEE_invisivel(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.CONFIDENCIAL, hermione = None)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_PNE_somente_leitura(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, hermione = TipoPermissao.SOMENTE_LEITURA)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_PNE_sem_acesso(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.ENCONTRAVEL, hermione = None)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_PNE_alterando_permissao(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, hermione = TipoPermissao.LEITURA_E_ESCRITA)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1, hermione = TipoPermissao.PROPRIETARIO)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_UBE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, UsuarioBanidoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_LEE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, LoginExpiradoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_UNLE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data()
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, UsuarioNaoLogadoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_UNEE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(unee = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, UsuarioNaoExisteException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_CNEE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(cnee = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, CategoriaNaoExisteException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_VIE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(harry_potter = TipoPermissao.SOMENTE_LEITURA)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, ValorIncorretoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_VIE_ordem_1(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1, rep = 1)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, ValorIncorretoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_alterar_por_chave_VIE_ordem_2(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        dados: SegredoSemChave = star_trek_data(alt = 1, rep = 3)
        com_chave: SegredoComChave = dados.com_chave(original.chave)

        x1: None | BaseException = s1.segredo.alterar_por_chave(com_chave)
        assert isinstance(x1, ValorIncorretoException)

    verificar_segredo(ctx, original)


# Método excluir_por_chave(self, dados: ChaveSegredo) -> None | _UNLE | _UBE | _SNEE | _PNE | _LEE


@applier_ctx
def test_excluir_por_chave_ok_proprietario(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert x1 is None

    verificar_segredo_nao_existe(ctx, original.chave)


@applier_ctx
def test_excluir_por_chave_ok_admin(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert x1 is None

    verificar_segredo_nao_existe(ctx, original.chave)


@applier_ctx
def test_excluir_por_chave_ok_coproprietario(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, hermione = TipoPermissao.PROPRIETARIO)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert x1 is None

    verificar_segredo_nao_existe(ctx, original.chave)


@applier_ctx
def test_excluir_por_chave_SNEE(ctx: ContextoOperacao) -> None:
    chave: ChaveSegredo = ChaveSegredo(9999)

    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(chave)
        assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo_nao_existe(ctx, chave)


@applier_ctx
def test_excluir_por_chave_SNEE_oculto(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.CONFIDENCIAL, hermione = None)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert isinstance(x1, SegredoNaoExisteException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_excluir_por_chave_UBE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert isinstance(x1, UsuarioBanidoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_excluir_por_chave_LEE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert isinstance(x1, LoginExpiradoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_excluir_por_chave_UNLE(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx)

    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert isinstance(x1, UsuarioNaoLogadoException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_excluir_por_chave_PNE_sem_relacao(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.ENCONTRAVEL, hermione = None)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(ctx, original)


@applier_ctx
def test_excluir_por_chave_PNE_fraco(ctx: ContextoOperacao) -> None:
    original: SegredoComChave = criar_segredo_normal(ctx, tipo = TipoSegredo.CONFIDENCIAL, hermione = TipoPermissao.LEITURA_E_ESCRITA)

    with ctx.servicos_normal2() as r:
        s1: Servicos = r.servicos
        x1: None | BaseException = s1.segredo.excluir_por_chave(original.chave)
        assert isinstance(x1, PermissaoNegadaException)

    verificar_segredo(ctx, original)
