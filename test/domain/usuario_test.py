from ..fixtures import (
    applier_ctx, applier_ctx_local, applier_ctx_remoto, ContextoOperacao, ContextoOperacaoLocal, ContextoOperacaoRemoto,
    harry_potter, voldemort, dumbledore, hermione, snape,
    lixo4,
    GerenciadorLogout, no_transaction
)
from cofre_de_senhas.service import (
    Servicos,
    LoginUsuario, LoginComSenha, TrocaSenha, SenhaAlterada, ResetLoginUsuario, RenomeUsuario,
    ChaveUsuario, NivelAcesso, UsuarioComChave, UsuarioNovo, UsuarioComNivel, ResultadoListaDeUsuarios
)
from cofre_de_senhas.erro import (
    UsuarioBanidoException, LoginExpiradoException, PermissaoNegadaException, UsuarioNaoLogadoException, SenhaErradaException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    ValorIncorretoException
)
from cofre_de_senhas.service_impl import ServicosImpl
from pytest import raises


tudo: ResultadoListaDeUsuarios = ResultadoListaDeUsuarios([
    UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL),
    UsuarioComChave(ChaveUsuario(voldemort   .pk_usuario), voldemort   .login, NivelAcesso.DESATIVADO),
    UsuarioComChave(ChaveUsuario(dumbledore  .pk_usuario), dumbledore  .login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO),
    UsuarioComChave(ChaveUsuario(hermione    .pk_usuario), hermione    .login, NivelAcesso.NORMAL)
])


# Método criar(self, dados: UsuarioNovo) -> UsuarioComChave | _UNLE | _UBE | _PNE | _UJEE | _LEE:


# @applier_trans(dbs, assert_db_ok)
# def test_criar_ok_supremo(c: TransactedConnection) -> None:
#     s: Servicos = servicos_admin(c)
#     dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO, "sectumsempra")

#     x: UsuarioComChave | BaseException = s.usuario.criar(dados)
#     assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


# @sqlite_db.decorator
# def test_criar_ok_supremo_remoto() -> None:
#     with servicos_admin_remoto() as r:
#         s: Servicos = r.servicos
#         dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO, "sectumsempra")

#         x: UsuarioComChave | BaseException = s.usuario.criar(dados)
#         assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


@applier_ctx
def test_criar_ok_supremo(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO, "sectumsempra")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


@applier_ctx
def test_criar_ok_normal(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.NORMAL, "sectumsempra")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.NORMAL)


@applier_ctx
def test_criar_ok_desativado(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.DESATIVADO)


@applier_ctx
def test_criar_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_criar_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_criar_PNE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, PermissaoNegadaException)


@applier_ctx
def test_criar_UJEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(hermione.login, NivelAcesso.NORMAL, "expelliarmus")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, UsuarioJaExisteException)


@applier_ctx
def test_criar_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo(hermione.login, NivelAcesso.NORMAL, "expelliarmus")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, UsuarioNaoLogadoException)


@applier_ctx
def test_criar_VIE_vazio(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo("", NivelAcesso.DESATIVADO, "xxx")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, ValorIncorretoException)


@applier_ctx
def test_criar_VIE_curto(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo("abc", NivelAcesso.DESATIVADO, "xxx")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, ValorIncorretoException)


@applier_ctx
def test_criar_VIE_longo(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: UsuarioNovo = UsuarioNovo("1234567890" * 5 + "1", NivelAcesso.DESATIVADO, "xxx")

        x: UsuarioComChave | BaseException = s.usuario.criar(dados)
        assert isinstance(x, ValorIncorretoException)


# Método buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:


@applier_ctx
def test_buscar_por_login_normal(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: LoginUsuario = LoginUsuario(hermione.login)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
        assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_ctx
def test_buscar_por_login_admin(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: LoginUsuario = LoginUsuario(hermione.login)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
        assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_ctx
def test_buscar_por_login_UNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: LoginUsuario = LoginUsuario(snape.login)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
        assert isinstance(x, UsuarioNaoExisteException)


@applier_ctx
def test_buscar_por_login_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        dados: LoginUsuario = LoginUsuario(hermione.login)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_buscar_por_login_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        dados: LoginUsuario = LoginUsuario(hermione.login)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_buscar_por_login_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: LoginUsuario = LoginUsuario(hermione.login)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
        assert isinstance(x, UsuarioNaoLogadoException)


# Método buscar_por_chave(self, dados: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:


@applier_ctx
def test_buscar_por_chave_normal(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
        assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_ctx
def test_buscar_por_chave_admin(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
        assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_ctx
def test_buscar_por_chave_UNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        dados: ChaveUsuario = ChaveUsuario(snape.pk_usuario)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
        assert isinstance(x, UsuarioNaoExisteException)


@applier_ctx
def test_buscar_por_chave_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_buscar_por_chave_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_buscar_por_chave_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

        x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
        assert isinstance(x, UsuarioNaoLogadoException)


# Método listar(self) -> ResultadoListaDeUsuarios | _UNLE | _UBE | _LEE


@applier_ctx
def test_listar_usuarios_ok_normal(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
        assert x == tudo


@applier_ctx
def test_listar_usuarios_ok_admin(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
        assert x == tudo


@applier_ctx
def test_listar_usuarios_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_listar_usuarios_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_listar_usuarios_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
        assert isinstance(x, UsuarioNaoLogadoException)


# Método login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE


@applier_ctx_local
def test_login_ok1(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_normal2_login() as r:
        s: Servicos = r.servicos
        login: LoginComSenha = LoginComSenha(hermione.login, "expelliarmus")
        x: UsuarioComChave | BaseException = s.usuario.login(login)
        assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)
        ctx.verificar()


@applier_ctx_local
def test_login_ok2(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_normal_login() as r:
        s: Servicos = r.servicos
        login: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
        x: UsuarioComChave | BaseException = s.usuario.login(login)
        assert x == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)
        ctx.verificar()


@applier_ctx_local
def test_login_ok3(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_admin_login() as r:
        s: Servicos = r.servicos
        login: LoginComSenha = LoginComSenha(dumbledore.login, "expecto patronum")
        x: UsuarioComChave | BaseException = s.usuario.login(login)
        assert x == UsuarioComChave(ChaveUsuario(dumbledore.pk_usuario), dumbledore.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)
        ctx.verificar()


@applier_ctx
def test_login_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        login: LoginComSenha = LoginComSenha(voldemort.login, "avada kedavra")
        x: UsuarioComChave | BaseException = s.usuario.login(login)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_login_SEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        login: LoginComSenha = LoginComSenha(harry_potter.login, "xxxx")
        x: UsuarioComChave | BaseException = s.usuario.login(login)
        assert isinstance(x, SenhaErradaException)


@applier_ctx
def test_login_SEE_usuario_nao_existe(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        login: LoginComSenha = LoginComSenha("xxx", "xxxx")
        x: UsuarioComChave | BaseException = s.usuario.login(login)
        assert isinstance(x, SenhaErradaException)


@applier_ctx
def test_login_UBE_antes_de_SEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        login: LoginComSenha = LoginComSenha(voldemort.login, "xxxx")
        x: UsuarioComChave | BaseException = s.usuario.login(login)
        assert isinstance(x, UsuarioBanidoException)


# Método logout(self) -> None


def test_logout() -> None:
    commited: bool = False
    closed: bool = False

    def back(t: str) -> None:
        nonlocal commited
        nonlocal closed
        if not commited and t == "commit":
            commited = True
        elif not closed and t == "close":
            closed = True
        else:
            assert False

    gl: GerenciadorLogout = GerenciadorLogout()
    s: Servicos = ServicosImpl(gl, no_transaction(back))
    s.usuario.logout()
    gl.verificar()
    assert commited
    assert closed


# Método renomear_por_login(self, dados: RenomeUsuario) -> None | _UNLE | _UNEE | _UJEE | _UBE | _PNE | _LEE | _VIE:


@applier_ctx
def test_renomear_ok(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
        x1: None | BaseException = s.usuario.renomear_por_login(t)
        assert x1 is None

        dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)
        x2: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
        assert x2 == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login + "XXX", NivelAcesso.NORMAL)


@applier_ctx
def test_renomear_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, UsuarioNaoLogadoException)


@applier_ctx
def test_renomear_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, LoginExpiradoException)


@applier_ctx
def test_renomear_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, UsuarioBanidoException)


@applier_ctx
def test_renomear_PNE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, PermissaoNegadaException)


@applier_ctx
def test_renomear_UNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login + "YYY", hermione.login + "XXX")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, UsuarioNaoExisteException)


@applier_ctx
def test_renomear_UJEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, harry_potter.login)
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, UsuarioJaExisteException)


@applier_ctx
def test_renomear_VIE_vazio(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, "")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, ValorIncorretoException)


@applier_ctx
def test_renomear_VIE_curto(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, "xxx")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, ValorIncorretoException)


@applier_ctx
def test_renomear_VIE_longo(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s: Servicos = r.servicos
        t: RenomeUsuario = RenomeUsuario(hermione.login, "0123456789" * 5 + "1")
        x: None | BaseException = s.usuario.renomear_por_login(t)
        assert isinstance(x, ValorIncorretoException)


# Método trocar_senha_por_chave(self, dados: TrocaSenha) -> None | _UNLE | _UBE | _SEE | _LEE:


@applier_ctx_local
def test_trocar_senha_por_chave_admin(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        t: TrocaSenha = TrocaSenha("expecto patronum", "wingardium leviosa")
        x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
        assert x1 is None

    with ctx.servicos_admin_login() as r:
        s2: Servicos = r.servicos
        login1: LoginComSenha = LoginComSenha(dumbledore.login, "wingardium leviosa")
        x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
        assert x2 == UsuarioComChave(ChaveUsuario(dumbledore.pk_usuario), dumbledore.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)
        ctx.verificar()

    with ctx.servicos_admin() as r:
        s3: Servicos = r.servicos
        login2: LoginComSenha = LoginComSenha(dumbledore.login, "expecto patronum")
        x3: UsuarioComChave | BaseException = s3.usuario.login(login2)
        assert isinstance(x3, SenhaErradaException)


@applier_ctx_local
def test_trocar_senha_por_chave_normal(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        t: TrocaSenha = TrocaSenha("alohomora", "wingardium leviosa")
        x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
        assert x1 is None

    with ctx.servicos_normal_login() as r:
        s2: Servicos = r.servicos
        login1: LoginComSenha = LoginComSenha(harry_potter.login, "wingardium leviosa")
        x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
        assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)
        ctx.verificar()

    with ctx.servicos_normal() as r:
        s3: Servicos = r.servicos
        login2: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
        x3: UsuarioComChave | BaseException = s3.usuario.login(login2)
        assert isinstance(x3, SenhaErradaException)


@applier_ctx_local
def test_trocar_senha_por_chave_SEE(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        t: TrocaSenha = TrocaSenha("xxxx", "wingardium leviosa")
        x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
        assert isinstance(x1, SenhaErradaException)

    with ctx.servicos_normal_login() as r:
        s2: Servicos = r.servicos
        login1: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
        x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
        assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)
        ctx.verificar()


@applier_ctx
def test_trocar_senha_por_chave_UBE_antes_de_SEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        t: TrocaSenha = TrocaSenha("xxxx", "wingardium leviosa")
        x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
        assert isinstance(x1, UsuarioBanidoException)


@applier_ctx
def test_trocar_senha_por_chave_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        t: TrocaSenha = TrocaSenha("avada kedavra", "wingardium leviosa")
        x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
        assert isinstance(x1, UsuarioBanidoException)

        login1: LoginComSenha = LoginComSenha(voldemort.login, "wingardium leviosa")
        x2: UsuarioComChave | BaseException = s1.usuario.login(login1)
        assert isinstance(x2, UsuarioBanidoException)


@applier_ctx
def test_trocar_senha_por_chave_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        t: TrocaSenha = TrocaSenha("blabla", "xxx xxx xxx")
        x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
        assert isinstance(x1, LoginExpiradoException)


@applier_ctx
def test_trocar_senha_por_chave_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        t: TrocaSenha = TrocaSenha("blabla", "xxx xxx xxx")
        x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
        assert isinstance(x1, UsuarioNaoLogadoException)


# Método resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada | _UNLE | _UBE | _PNE | _UNEE | _LEE:


@applier_ctx_local
def test_resetar_senha_por_login_ok1(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        t: ResetLoginUsuario = ResetLoginUsuario(harry_potter.login)
        x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
        assert isinstance(x1, SenhaAlterada)
        assert x1.chave == ChaveUsuario(harry_potter.pk_usuario)
        assert x1.login == harry_potter.login
        nova_senha: str = x1.nova_senha
        assert len(nova_senha) == 20

    with ctx.servicos_normal_login() as r:
        s2: Servicos = r.servicos
        login1: LoginComSenha = LoginComSenha(harry_potter.login, nova_senha)
        x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
        assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)
        ctx.verificar()

        login2: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
        x3: UsuarioComChave | BaseException = s2.usuario.login(login2)
        assert isinstance(x3, SenhaErradaException)


@applier_ctx
def test_resetar_senha_por_login_PNE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
        x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
        assert isinstance(x1, PermissaoNegadaException)


@applier_ctx
def test_resetar_senha_por_login_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
        x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
        assert isinstance(x1, UsuarioBanidoException)


@applier_ctx
def test_resetar_senha_por_login_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
        x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
        assert isinstance(x1, UsuarioNaoLogadoException)


@applier_ctx
def test_resetar_senha_por_login_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
        x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
        assert isinstance(x1, LoginExpiradoException)


@applier_ctx
def test_resetar_senha_por_login_UNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        t: ResetLoginUsuario = ResetLoginUsuario(lixo4)
        x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
        assert isinstance(x1, UsuarioNaoExisteException)


# Método alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None | _UNLE | _UBE | _PNE | _UNEE | _LEE:


@applier_ctx
def test_alterar_nivel_por_login_ok1(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        t: UsuarioComNivel = UsuarioComNivel(harry_potter.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)
        x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
        assert x1 is None

        login1: LoginUsuario = LoginUsuario(harry_potter.login)
        x2: UsuarioComChave | BaseException = s1.usuario.buscar_por_login(login1)
        assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


@applier_ctx
def test_alterar_nivel_por_login_ok2(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
        x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
        assert x1 is None

        login1: LoginUsuario = LoginUsuario(hermione.login)
        x2: UsuarioComChave | BaseException = s1.usuario.buscar_por_login(login1)
        assert x2 == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.DESATIVADO)


@applier_ctx
def test_alterar_nivel_por_login_PNE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_normal() as r:
        s1: Servicos = r.servicos
        t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
        x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
        assert isinstance(x1, PermissaoNegadaException)


@applier_ctx
def test_alterar_nivel_por_login_UBE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_banido() as r:
        s1: Servicos = r.servicos
        t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
        x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
        assert isinstance(x1, UsuarioBanidoException)


@applier_ctx
def test_alterar_nivel_por_login_UNLE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_nao_logar() as r:
        s1: Servicos = r.servicos
        t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
        x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
        assert isinstance(x1, UsuarioNaoLogadoException)


@applier_ctx
def test_alterar_nivel_por_login_LEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_usuario_nao_existe() as r:
        s1: Servicos = r.servicos
        t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
        x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
        assert isinstance(x1, LoginExpiradoException)


@applier_ctx
def test_alterar_nivel_por_login_UNEE(ctx: ContextoOperacao) -> None:
    with ctx.servicos_admin() as r:
        s1: Servicos = r.servicos
        t: UsuarioComNivel = UsuarioComNivel(lixo4, NivelAcesso.DESATIVADO)
        x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
        assert isinstance(x1, UsuarioNaoExisteException)


# Método criar_admin(self, dados: LoginComSenha) -> UsuarioComChave | _VIE | _UJEE:


@applier_ctx_local
def test_criar_admin_ok(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: LoginComSenha = LoginComSenha(snape.login, "sectumsempra")

        x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
        assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


@applier_ctx_local
def test_criar_admin_UJEE(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: LoginComSenha = LoginComSenha(dumbledore.login, "xxx")

        x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
        assert isinstance(x, UsuarioJaExisteException)


@applier_ctx_local
def test_criar_admin_VIE_vazio(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: LoginComSenha = LoginComSenha("", "xxx")

        x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
        assert isinstance(x, ValorIncorretoException)


@applier_ctx_local
def test_criar_admin_VIE_curto(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: LoginComSenha = LoginComSenha("abc", "xxx")

        x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
        assert isinstance(x, ValorIncorretoException)


@applier_ctx_local
def test_criar_admin_VIE_longo(ctx: ContextoOperacaoLocal) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: LoginComSenha = LoginComSenha("1234567890" * 5 + "1", "xxx")

        x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
        assert isinstance(x, ValorIncorretoException)


@applier_ctx_remoto
def test_criar_admin_remoto(ctx: ContextoOperacaoRemoto) -> None:
    with ctx.servicos_nao_logar() as r:
        s: Servicos = r.servicos
        dados: LoginComSenha = LoginComSenha(snape.login, "sectumsempra")

        with raises(NotImplementedError):
            s.bd.criar_admin(dados)
