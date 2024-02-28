from ..db_test_util import applier_trans
from ..fixtures import (
    dbs, assert_db_ok, ServicosLogout, ServicosDecorator,
    harry_potter, voldemort, dumbledore, hermione, snape,
    servicos_normal, servicos_admin,
    servicos_normal_login, servicos_normal2_login, servicos_admin_login,
    servicos_banido, servicos_usuario_nao_existe, servicos_nao_logado, servicos_nao_logar,
    lixo4
)
from connection.trans import TransactedConnection
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


tudo: ResultadoListaDeUsuarios = ResultadoListaDeUsuarios([
    UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL),
    UsuarioComChave(ChaveUsuario(voldemort   .pk_usuario), voldemort   .login, NivelAcesso.DESATIVADO),
    UsuarioComChave(ChaveUsuario(dumbledore  .pk_usuario), dumbledore  .login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO),
    UsuarioComChave(ChaveUsuario(hermione    .pk_usuario), hermione    .login, NivelAcesso.NORMAL)
])


# Método criar(self, dados: UsuarioNovo) -> UsuarioComChave | _UNLE | _UBE | _PNE | _UJEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def test_criar_ok_supremo(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO, "sectumsempra")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


@applier_trans(dbs, assert_db_ok)
def test_criar_ok_normal(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.NORMAL, "sectumsempra")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def test_criar_ok_desativado(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.DESATIVADO)


@applier_trans(dbs, assert_db_ok)
def test_criar_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_PNE(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: UsuarioNovo = UsuarioNovo(snape.login, NivelAcesso.DESATIVADO, "sectumsempra")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, PermissaoNegadaException)


@applier_trans(dbs, assert_db_ok)
def test_criar_UJEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: UsuarioNovo = UsuarioNovo(hermione.login, NivelAcesso.NORMAL, "expelliarmus")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, UsuarioJaExisteException)


@applier_trans(dbs, assert_db_ok)
def test_criar_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)
    dados: UsuarioNovo = UsuarioNovo(hermione.login, NivelAcesso.NORMAL, "expelliarmus")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, UsuarioNaoLogadoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_VIE_vazio(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: UsuarioNovo = UsuarioNovo("", NivelAcesso.DESATIVADO, "xxx")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_VIE_curto(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: UsuarioNovo = UsuarioNovo("abc", NivelAcesso.DESATIVADO, "xxx")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_VIE_longo(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: UsuarioNovo = UsuarioNovo("1234567890" * 5 + "1", NivelAcesso.DESATIVADO, "xxx")

    x: UsuarioComChave | BaseException = s.usuario.criar(dados)
    assert isinstance(x, ValorIncorretoException)


# Método buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_login_normal(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_login_admin(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_login_UNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: LoginUsuario = LoginUsuario(snape.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, UsuarioNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_login_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_login_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_login_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, UsuarioNaoLogadoException)


# Método buscar_por_chave(self, dados: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_normal(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_admin(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_UNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: ChaveUsuario = ChaveUsuario(snape.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert isinstance(x, UsuarioNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_buscar_por_chave_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert isinstance(x, UsuarioNaoLogadoException)


# Método listar(self) -> ResultadoListaDeUsuarios | _UNLE | _UBE | _LEE


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_ok_normal(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
    assert x == tudo


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_ok_admin(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
    assert x == tudo


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)
    x: ResultadoListaDeUsuarios | BaseException = s.usuario.listar()
    assert isinstance(x, UsuarioNaoLogadoException)


# Método login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE


@applier_trans(dbs, assert_db_ok)
def test_login_ok1(c: TransactedConnection) -> None:
    s: ServicosDecorator = servicos_normal2_login(c)
    login: LoginComSenha = LoginComSenha(hermione.login, "expelliarmus")
    x: UsuarioComChave | BaseException = s.usuario.login(login)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)
    s.gl.verificar()


@applier_trans(dbs, assert_db_ok)
def test_login_ok2(c: TransactedConnection) -> None:
    s: ServicosDecorator = servicos_normal_login(c)
    login: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
    x: UsuarioComChave | BaseException = s.usuario.login(login)
    assert x == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)
    s.gl.verificar()


@applier_trans(dbs, assert_db_ok)
def test_login_ok3(c: TransactedConnection) -> None:
    s: ServicosDecorator = servicos_admin_login(c)
    login: LoginComSenha = LoginComSenha(dumbledore.login, "expecto patronum")
    x: UsuarioComChave | BaseException = s.usuario.login(login)
    assert x == UsuarioComChave(ChaveUsuario(dumbledore.pk_usuario), dumbledore.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)
    s.gl.verificar()


@applier_trans(dbs, assert_db_ok)
def test_login_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    login: LoginComSenha = LoginComSenha(voldemort.login, "avada kedavra")
    x: UsuarioComChave | BaseException = s.usuario.login(login)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_login_SEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    login: LoginComSenha = LoginComSenha(harry_potter.login, "xxxx")
    x: UsuarioComChave | BaseException = s.usuario.login(login)
    assert isinstance(x, SenhaErradaException)


@applier_trans(dbs, assert_db_ok)
def test_login_SEE_usuario_nao_existe(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    login: LoginComSenha = LoginComSenha("xxx", "xxxx")
    x: UsuarioComChave | BaseException = s.usuario.login(login)
    assert isinstance(x, SenhaErradaException)


@applier_trans(dbs, assert_db_ok)
def test_login_UBE_antes_de_SEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    login: LoginComSenha = LoginComSenha(voldemort.login, "xxxx")
    x: UsuarioComChave | BaseException = s.usuario.login(login)
    assert isinstance(x, UsuarioBanidoException)


# Método logout(self) -> None


def test_logout() -> None:
    sl: ServicosLogout = ServicosLogout()
    s: ServicosDecorator = sl.criar()
    s.usuario.logout()
    s.gl.verificar()
    assert sl.commited
    assert sl.closed


# Método renomear_por_login(self, dados: RenomeUsuario) -> None | _UNLE | _UNEE | _UJEE | _UBE | _PNE | _LEE | _VIE:


@applier_trans(dbs, assert_db_ok)
def test_renomear_ok(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
    x1: None | BaseException = s.usuario.renomear_por_login(t)
    assert x1 is None

    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)
    x2: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert x2 == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login + "XXX", NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def test_renomear_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, UsuarioNaoLogadoException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_PNE(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, hermione.login + "XXX")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, PermissaoNegadaException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_UNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login + "YYY", hermione.login + "XXX")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, UsuarioNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_UJEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, harry_potter.login)
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, UsuarioJaExisteException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_VIE_vazio(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, "")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_VIE_curto(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, "xxx")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_renomear_VIE_longo(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    t: RenomeUsuario = RenomeUsuario(hermione.login, "0123456789" * 5 + "1")
    x: None | BaseException = s.usuario.renomear_por_login(t)
    assert isinstance(x, ValorIncorretoException)


# Método trocar_senha_por_chave(self, dados: TrocaSenha) -> None | _UNLE | _UBE | _SEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def test_trocar_senha_por_chave_admin(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    t: TrocaSenha = TrocaSenha("expecto patronum", "wingardium leviosa")
    x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
    assert x1 is None

    s2: ServicosDecorator = servicos_admin_login(c)
    login1: LoginComSenha = LoginComSenha(dumbledore.login, "wingardium leviosa")
    x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
    assert x2 == UsuarioComChave(ChaveUsuario(dumbledore.pk_usuario), dumbledore.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)
    s2.gl.verificar()

    login2: LoginComSenha = LoginComSenha(dumbledore.login, "expecto patronum")
    x3: UsuarioComChave | BaseException = s1.usuario.login(login2)
    assert isinstance(x3, SenhaErradaException)


@applier_trans(dbs, assert_db_ok)
def test_trocar_senha_por_chave_normal(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    t: TrocaSenha = TrocaSenha("alohomora", "wingardium leviosa")
    x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
    assert x1 is None

    s2: ServicosDecorator = servicos_normal_login(c)
    login1: LoginComSenha = LoginComSenha(harry_potter.login, "wingardium leviosa")
    x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
    assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)
    s2.gl.verificar()

    login2: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
    x3: UsuarioComChave | BaseException = s1.usuario.login(login2)
    assert isinstance(x3, SenhaErradaException)


@applier_trans(dbs, assert_db_ok)
def test_trocar_senha_por_chave_SEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    t: TrocaSenha = TrocaSenha("xxxx", "wingardium leviosa")
    x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
    assert isinstance(x1, SenhaErradaException)

    s2: ServicosDecorator = servicos_normal_login(c)
    login1: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
    x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
    assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def test_trocar_senha_por_chave_UBE_antes_de_SEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_banido(c)
    t: TrocaSenha = TrocaSenha("xxxx", "wingardium leviosa")
    x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
    assert isinstance(x1, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_trocar_senha_por_chave_UBE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_banido(c)
    t: TrocaSenha = TrocaSenha("avada kedavra", "wingardium leviosa")
    x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
    assert isinstance(x1, UsuarioBanidoException)

    login1: LoginComSenha = LoginComSenha(voldemort.login, "wingardium leviosa")
    x2: UsuarioComChave | BaseException = s1.usuario.login(login1)
    assert isinstance(x2, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_trocar_senha_por_chave_LEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_usuario_nao_existe(c)
    t: TrocaSenha = TrocaSenha("blabla", "xxx xxx xxx")
    x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
    assert isinstance(x1, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_trocar_senha_por_chave_UNLE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_nao_logado(c)
    t: TrocaSenha = TrocaSenha("blabla", "xxx xxx xxx")
    x1: None | BaseException = s1.usuario.trocar_senha_por_chave(t)
    assert isinstance(x1, UsuarioNaoLogadoException)


# Método resetar_senha_por_login(self, dados: ResetLoginUsuario) -> SenhaAlterada | _UNLE | _UBE | _PNE | _UNEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def test_resetar_senha_por_login_ok1(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    t: ResetLoginUsuario = ResetLoginUsuario(harry_potter.login)
    x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
    assert isinstance(x1, SenhaAlterada)
    assert x1.chave == ChaveUsuario(harry_potter.pk_usuario)
    assert x1.login == harry_potter.login
    nova_senha: str = x1.nova_senha
    assert len(nova_senha) == 20

    s2: ServicosDecorator = servicos_normal_login(c)
    login1: LoginComSenha = LoginComSenha(harry_potter.login, nova_senha)
    x2: UsuarioComChave | BaseException = s2.usuario.login(login1)
    assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL)
    s2.gl.verificar()

    login2: LoginComSenha = LoginComSenha(harry_potter.login, "alohomora")
    x3: UsuarioComChave | BaseException = s2.usuario.login(login2)
    assert isinstance(x3, SenhaErradaException)


@applier_trans(dbs, assert_db_ok)
def test_resetar_senha_por_login_PNE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
    x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
    assert isinstance(x1, PermissaoNegadaException)


@applier_trans(dbs, assert_db_ok)
def test_resetar_senha_por_login_UBE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_banido(c)
    t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
    x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
    assert isinstance(x1, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_resetar_senha_por_login_UNLE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_nao_logado(c)
    t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
    x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
    assert isinstance(x1, UsuarioNaoLogadoException)


@applier_trans(dbs, assert_db_ok)
def test_resetar_senha_por_login_LEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_usuario_nao_existe(c)
    t: ResetLoginUsuario = ResetLoginUsuario(hermione.login)
    x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
    assert isinstance(x1, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_resetar_senha_por_login_UNEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    t: ResetLoginUsuario = ResetLoginUsuario(lixo4)
    x1: SenhaAlterada | BaseException = s1.usuario.resetar_senha_por_login(t)
    assert isinstance(x1, UsuarioNaoExisteException)


# Método alterar_nivel_por_login(self, dados: UsuarioComNivel) -> None | _UNLE | _UBE | _PNE | _UNEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def test_alterar_nivel_por_login_ok1(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    t: UsuarioComNivel = UsuarioComNivel(harry_potter.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)
    x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
    assert x1 is None

    login1: LoginUsuario = LoginUsuario(harry_potter.login)
    x2: UsuarioComChave | BaseException = s1.usuario.buscar_por_login(login1)
    assert x2 == UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


@applier_trans(dbs, assert_db_ok)
def test_alterar_nivel_por_login_ok2(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
    x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
    assert x1 is None

    login1: LoginUsuario = LoginUsuario(hermione.login)
    x2: UsuarioComChave | BaseException = s1.usuario.buscar_por_login(login1)
    assert x2 == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.DESATIVADO)


@applier_trans(dbs, assert_db_ok)
def test_alterar_nivel_por_login_PNE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_normal(c)
    t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
    x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
    assert isinstance(x1, PermissaoNegadaException)


@applier_trans(dbs, assert_db_ok)
def test_alterar_nivel_por_login_UBE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_banido(c)
    t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
    x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
    assert isinstance(x1, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def test_alterar_nivel_por_login_UNLE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_nao_logado(c)
    t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
    x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
    assert isinstance(x1, UsuarioNaoLogadoException)


@applier_trans(dbs, assert_db_ok)
def test_alterar_nivel_por_login_LEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_usuario_nao_existe(c)
    t: UsuarioComNivel = UsuarioComNivel(hermione.login, NivelAcesso.DESATIVADO)
    x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
    assert isinstance(x1, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def test_alterar_nivel_por_login_UNEE(c: TransactedConnection) -> None:
    s1: Servicos = servicos_admin(c)
    t: UsuarioComNivel = UsuarioComNivel(lixo4, NivelAcesso.DESATIVADO)
    x1: None | BaseException = s1.usuario.alterar_nivel_por_login(t)
    assert isinstance(x1, UsuarioNaoExisteException)


# Método criar_admin(self, dados: LoginComSenha) -> UsuarioComChave | _VIE | _UJEE:


@applier_trans(dbs, assert_db_ok)
def test_criar_admin_ok(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    dados: LoginComSenha = LoginComSenha(snape.login, "sectumsempra")

    x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
    assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


@applier_trans(dbs, assert_db_ok)
def test_criar_admin_UJEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    dados: LoginComSenha = LoginComSenha(dumbledore.login, "xxx")

    x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
    assert isinstance(x, UsuarioJaExisteException)


@applier_trans(dbs, assert_db_ok)
def test_criar_admin_VIE_vazio(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    dados: LoginComSenha = LoginComSenha("", "xxx")

    x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_admin_VIE_curto(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    dados: LoginComSenha = LoginComSenha("abc", "xxx")

    x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
    assert isinstance(x, ValorIncorretoException)


@applier_trans(dbs, assert_db_ok)
def test_criar_admin_VIE_longo(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logar(c)
    dados: LoginComSenha = LoginComSenha("1234567890" * 5 + "1", "xxx")

    x: UsuarioComChave | BaseException = s.bd.criar_admin(dados)
    assert isinstance(x, ValorIncorretoException)
