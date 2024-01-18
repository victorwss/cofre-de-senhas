from ..db_test_util import applier_trans
from ..fixtures import (
    dbs, assert_db_ok,
    harry_potter, voldemort, dumbledore, hermione, snape,
    servicos_normal, servicos_admin, servicos_banido, servicos_usuario_nao_existe, servicos_nao_logado
)
from connection.trans import TransactedConnection
from cofre_de_senhas.service import (
    ChaveUsuario, LoginUsuario, NivelAcesso, UsuarioComChave, UsuarioNovo, ResultadoListaDeUsuarios
)
from cofre_de_senhas.service_impl import Servicos
from cofre_de_senhas.erro import (
    UsuarioBanidoException, LoginExpiradoException, PermissaoNegadaException, UsuarioNaoLogadoException,
    UsuarioNaoExisteException, UsuarioJaExisteException
)
from pytest import raises


tudo: ResultadoListaDeUsuarios = ResultadoListaDeUsuarios([
    UsuarioComChave(ChaveUsuario(harry_potter.pk_usuario), harry_potter.login, NivelAcesso.NORMAL),
    UsuarioComChave(ChaveUsuario(voldemort   .pk_usuario), voldemort   .login, NivelAcesso.DESATIVADO),
    UsuarioComChave(ChaveUsuario(dumbledore  .pk_usuario), dumbledore  .login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO),
    UsuarioComChave(ChaveUsuario(hermione    .pk_usuario), hermione    .login, NivelAcesso.NORMAL)
])


def test_nao_instanciar_servicos() -> None:
    from cofre_de_senhas.usuario.usuario import Servicos as UsuarioServico
    with raises(Exception):
        UsuarioServico()


# @applier_trans(dbs, assert_db_ok)
# def test_criar_admin_ok(c: TransactedConnection) -> None:
#     from cofre_de_senhas.usuario.usuario import Servicos as UsuarioServico
#     s: Servicos = servicos_normal(c)
#     dados: LoginComSenha = LoginComSenha(snape.login, "sectumsempra")

#     x: UsuarioComChave | BaseException = UsuarioServico.criar_admin(dados)
#     assert x == UsuarioComChave(ChaveUsuario(snape.pk_usuario), snape.login, NivelAcesso.CHAVEIRO_DEUS_SUPREMO)


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


# Método buscar_por_login(self, dados: LoginUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def buscar_por_login_normal(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def buscar_por_login_admin(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def buscar_por_login_UNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: LoginUsuario = LoginUsuario(snape.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, UsuarioNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def buscar_por_login_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def buscar_por_login_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def buscar_por_login_UNLE(c: TransactedConnection) -> None:
    s: Servicos = servicos_nao_logado(c)
    dados: LoginUsuario = LoginUsuario(hermione.login)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_login(dados)
    assert isinstance(x, UsuarioNaoLogadoException)


# Método buscar_por_chave(self, dados: ChaveUsuario) -> UsuarioComChave | _UNLE | _UBE | _UNEE | _LEE:


@applier_trans(dbs, assert_db_ok)
def buscar_por_chave_normal(c: TransactedConnection) -> None:
    s: Servicos = servicos_normal(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def buscar_por_chave_admin(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert x == UsuarioComChave(ChaveUsuario(hermione.pk_usuario), hermione.login, NivelAcesso.NORMAL)


@applier_trans(dbs, assert_db_ok)
def buscar_por_chave_UNEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_admin(c)
    dados: ChaveUsuario = ChaveUsuario(snape.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert isinstance(x, UsuarioNaoExisteException)


@applier_trans(dbs, assert_db_ok)
def buscar_por_chave_UBE(c: TransactedConnection) -> None:
    s: Servicos = servicos_banido(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert isinstance(x, UsuarioBanidoException)


@applier_trans(dbs, assert_db_ok)
def buscar_por_chave_LEE(c: TransactedConnection) -> None:
    s: Servicos = servicos_usuario_nao_existe(c)
    dados: ChaveUsuario = ChaveUsuario(hermione.pk_usuario)

    x: UsuarioComChave | BaseException = s.usuario.buscar_por_chave(dados)
    assert isinstance(x, LoginExpiradoException)


@applier_trans(dbs, assert_db_ok)
def buscar_por_chave_UNLE(c: TransactedConnection) -> None:
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
