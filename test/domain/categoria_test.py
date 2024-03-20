from ..fixtures import (
    applier_ctx, applier_ctx_local, ContextoOperacao, ContextoOperacaoLocal,
    banco_de_dados, aplicacao, servidor, api, producao, homologacao, desenvolvimento, qa, integracao,
    millenium_falcon, lixo2, lixo4, nome_em_branco, nome_longo_demais, nao_existe
)
from cofre_de_senhas.erro import (
    PermissaoNegadaException, UsuarioBanidoException, LoginExpiradoException, UsuarioNaoLogadoException,
    CategoriaNaoExisteException, CategoriaJaExisteException,
    ValorIncorretoException, ExclusaoSemCascataException
)
from cofre_de_senhas.service import Servicos, NomeCategoria, CategoriaComChave, ChaveCategoria, RenomeCategoria, ResultadoListaDeCategorias


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


# Método buscar_por_nome(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE


@applier_ctx
def test_buscar_categoria_por_nome_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(qa.nome)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_ctx
def test_buscar_categoria_por_nome_ok2(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(desenvolvimento.nome)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert x == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_ctx
def test_buscar_categoria_por_nome_CNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(lixo4)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert isinstance(x, CategoriaNaoExisteException)


@applier_ctx
def test_buscar_categoria_por_nome_CNEE_case_sensitive(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(qa.nome.lower())

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert isinstance(x, CategoriaNaoExisteException)


@applier_ctx
def test_buscar_categoria_por_nome_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(qa.nome)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_buscar_categoria_por_nome_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(qa.nome)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_buscar_categoria_por_nome_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(qa.nome)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert isinstance(x, UsuarioNaoLogadoException)


# Método buscar_por_chave(self, chave: ChaveCategoria) -> CategoriaComChave | _UNLE | _UBE | _CNEE | _LEE


@applier_ctx
def test_buscar_categoria_por_chave_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
        assert x == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_ctx
def test_buscar_categoria_por_chave_ok2(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: ChaveCategoria = ChaveCategoria(desenvolvimento.pk_categoria)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
        assert x == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_ctx
def test_buscar_categoria_por_chave_CNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: ChaveCategoria = ChaveCategoria(lixo2)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
        assert isinstance(x, CategoriaNaoExisteException)


@applier_ctx
def test_buscar_categoria_por_chave_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_buscar_categoria_por_chave_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_buscar_categoria_por_chave_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: ChaveCategoria = ChaveCategoria(qa.pk_categoria)

        x: CategoriaComChave | BaseException = s.categoria.buscar_por_chave(dados)
        assert isinstance(x, UsuarioNaoLogadoException)


# Método criar(self, dados: NomeCategoria) -> CategoriaComChave | _UNLE | _LEE | _UBE | _PNE | _CJEE | _VIE


@applier_ctx
def test_criar_categoria_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(millenium_falcon.nome)

        x: CategoriaComChave | BaseException = s.categoria.criar(dados)
        assert x == CategoriaComChave(ChaveCategoria(millenium_falcon.pk_categoria), millenium_falcon.nome)

        y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert x == y


@applier_ctx
def test_criar_categoria_CJEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(qa.nome)

        x: CategoriaComChave | BaseException = s.categoria.criar(dados)
        assert isinstance(x, CategoriaJaExisteException)

        y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert y == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)


@applier_ctx
def test_criar_categoria_PNE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(millenium_falcon.nome)

        x: CategoriaComChave | BaseException = s1.categoria.criar(dados)
        assert isinstance(x, PermissaoNegadaException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(dados)
        assert isinstance(y, CategoriaNaoExisteException)


@applier_ctx
def test_criar_categoria_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(millenium_falcon.nome)

        x: CategoriaComChave | BaseException = s1.categoria.criar(dados)
        assert isinstance(x, UsuarioBanidoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(dados)
        assert isinstance(y, CategoriaNaoExisteException)


@applier_ctx
def test_criar_categoria_VIE_nome_curto(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(nome_em_branco)

        x: CategoriaComChave | BaseException = s.categoria.criar(dados)
        assert isinstance(x, ValorIncorretoException)

        y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert isinstance(y, CategoriaNaoExisteException)


@applier_ctx
def test_criar_categoria_VIE_nome_longo(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(nome_longo_demais)

        x: CategoriaComChave | BaseException = s.categoria.criar(dados)
        assert isinstance(x, ValorIncorretoException)

        y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados)
        assert isinstance(y, CategoriaNaoExisteException)


@applier_ctx
def test_criar_categoria_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(millenium_falcon.nome)

        x: CategoriaComChave | BaseException = s1.categoria.criar(dados)
        assert isinstance(x, LoginExpiradoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(dados)
        assert isinstance(y, CategoriaNaoExisteException)


@applier_ctx
def test_criar_categoria_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(millenium_falcon.nome)

        x: CategoriaComChave | BaseException = s1.categoria.criar(dados)
        assert isinstance(x, UsuarioNaoLogadoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(dados)
        assert isinstance(y, CategoriaNaoExisteException)


# Método renomear_por_nome(self, dados: RenomeCategoria) -> None | _UNLE | _LEE | _UBE | _PNE | _VIE | _CJEE | _CNEE


@applier_ctx
def test_renomear_categoria_ok(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, millenium_falcon.nome)

        x: None | BaseException = s.categoria.renomear_por_nome(dados)
        assert x is None

        z: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert isinstance(z, CategoriaNaoExisteException)

        y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert y == CategoriaComChave(ChaveCategoria(qa.pk_categoria), millenium_falcon.nome)


@applier_ctx
def test_renomear_categoria_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, millenium_falcon.nome)

        x: None | BaseException = s1.categoria.renomear_por_nome(dados)
        assert isinstance(x, LoginExpiradoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y1: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, millenium_falcon.nome)

        x: None | BaseException = s1.categoria.renomear_por_nome(dados)
        assert isinstance(x, UsuarioBanidoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y1: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_PNE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, millenium_falcon.nome)

        x: None | BaseException = s1.categoria.renomear_por_nome(dados)
        assert isinstance(x, PermissaoNegadaException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y1: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_CJEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, desenvolvimento.nome)

        x: None | BaseException = s.categoria.renomear_por_nome(dados)
        assert isinstance(x, CategoriaJaExisteException)

        y1: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_CNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(millenium_falcon.nome, nao_existe.nome)

        x: None | BaseException = s.categoria.renomear_por_nome(dados)
        assert isinstance(x, CategoriaNaoExisteException)

        y1: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_CNEE_antes_de_CJEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(millenium_falcon.nome, qa.nome)

        x: None | BaseException = s.categoria.renomear_por_nome(dados)
        assert isinstance(x, CategoriaNaoExisteException)

        y1: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_VIE_nome_curto(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, nome_em_branco)

        x: None | BaseException = s.categoria.renomear_por_nome(dados)
        assert isinstance(x, ValorIncorretoException)

        y1: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(nome_em_branco))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_VIE_nome_longo(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, nome_longo_demais)

        x: None | BaseException = s.categoria.renomear_por_nome(dados)
        assert isinstance(x, ValorIncorretoException)

        y1: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(NomeCategoria(nome_longo_demais))
        assert isinstance(y2, CategoriaNaoExisteException)


@applier_ctx
def test_renomear_categoria_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        dados: RenomeCategoria = RenomeCategoria(qa.nome, millenium_falcon.nome)

        x: None | BaseException = s1.categoria.renomear_por_nome(dados)
        assert isinstance(x, UsuarioNaoLogadoException)

    with ctx.servicos_admin() as r:
        s2: Servicos = r.servicos
        y1: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(qa.nome))
        assert y1 == CategoriaComChave(ChaveCategoria(qa.pk_categoria), qa.nome)

        y2: CategoriaComChave | BaseException = s2.categoria.buscar_por_nome(NomeCategoria(millenium_falcon.nome))
        assert isinstance(y2, CategoriaNaoExisteException)


# Método excluir_por_nome(self, dados: NomeCategoria) -> None | _UNLE | _UBE | _PNE | _CNEE | _LEE | _ESCE


@applier_ctx
def test_excluir_categoria_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados1: NomeCategoria = NomeCategoria(api.nome)

        x: None | BaseException = s.categoria.excluir_por_nome(dados1)
        assert x is None

        y: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados1)
        assert isinstance(y, CategoriaNaoExisteException)

        dados2: NomeCategoria = NomeCategoria(desenvolvimento.nome)
        z: CategoriaComChave | BaseException = s.categoria.buscar_por_nome(dados2)
        assert z == CategoriaComChave(ChaveCategoria(desenvolvimento.pk_categoria), desenvolvimento.nome)


@applier_ctx
def test_excluir_categoria_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(api.nome)

        x: None | BaseException = s.categoria.excluir_por_nome(dados)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_excluir_categoria_PNE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(api.nome)

        x: None | BaseException = s.categoria.excluir_por_nome(dados)
        assert isinstance(x, PermissaoNegadaException)


@applier_ctx
def test_excluir_categoria_CNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(millenium_falcon.nome)

        x: None | BaseException = s.categoria.excluir_por_nome(dados)
        assert isinstance(x, CategoriaNaoExisteException)


@applier_ctx
def test_excluir_categoria_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(api.nome)

        x: None | BaseException = s.categoria.excluir_por_nome(dados)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_excluir_categoria_ESCE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(qa.nome)

        x: None | BaseException = s.categoria.excluir_por_nome(dados)
        assert isinstance(x, ExclusaoSemCascataException)


@applier_ctx
def test_excluir_categoria_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: NomeCategoria = NomeCategoria(api.nome)

        x: None | BaseException = s.categoria.excluir_por_nome(dados)
        assert isinstance(x, UsuarioNaoLogadoException)


# Método listar(self) -> ResultadoListaDeCategorias | _UNLE | _UBE | _LEE


@applier_ctx
def test_listar_categorias_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
        assert x == tudo


@applier_ctx
def test_listar_categorias_ok2(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
        assert x == tudo


@applier_ctx
def test_listar_categorias_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_listar_categorias_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_listar_categorias_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeCategorias | BaseException = s.categoria.listar()
        assert isinstance(x, UsuarioNaoLogadoException)


# Método criar_bd(self) -> None


@applier_ctx_local
def test_criar_bd_ok(ctx: ContextoOperacaoLocal) -> None:
    with ctx.conn as z:
        z.execute("DROP TABLE permissao")
        z.execute("DROP TABLE categoria_segredo")
        z.execute("DROP TABLE campo_segredo")
        z.execute("DROP TABLE segredo")
        z.execute("DROP TABLE categoria")
        z.execute("DROP TABLE usuario")
        z.execute("DROP TABLE enum_nivel_acesso")
        z.execute("DROP TABLE enum_tipo_permissao")
        z.execute("DROP TABLE enum_tipo_segredo")

    with ctx.servicos_nao_logar() as r:
        s0: Servicos = r.servicos
        s0.bd.criar_bd()

    hash: str = \
        "SbhhiMEETzPiquOxabc178eb35f26c8f59981b01a11cbec48b16f6a8e2c204f4a9a1b633c9199e0b3b2a64b13e49226306bb451c57c851f3c6e872885115404cb74279db7f5372ea"
    sql_insert: str = f"INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Harry Potter', 1, '{hash}');"

    with ctx.conn as z:
        z.execute(sql_insert)

    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        x: ResultadoListaDeCategorias | BaseException = s1.categoria.listar()
        assert x == tudo
