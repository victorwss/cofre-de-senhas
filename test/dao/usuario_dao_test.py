from ..db_test_util import applier, applier_trans, DbTestConfig
from ..fixtures import (
    dbs, assert_db_ok,
    todos_usuarios, parte_usuarios, nome_curto, nome_longo,
    harry_potter, dumbledore,
    snape, snape_sem_pk, sectumsempra, voldemort,
    lixo1, lixo2, lixo3, lixo4, lixo5, lixo6
)
from connection.trans import TransactedConnection
from connection.conn import IntegrityViolationException
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioSemPK, LoginUsuarioUK
from cofre_de_senhas.usuario.usuario_dao_impl import UsuarioDAOImpl
from pytest import raises


@applier(dbs, assert_db_ok)
def test_instanciar(db: DbTestConfig) -> None:
    UsuarioDAOImpl(db.conn)


@applier_trans(dbs, assert_db_ok)
def test_criar_usuario(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = snape_sem_pk
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == snape.pk_usuario


@applier_trans(dbs, assert_db_ok)
def test_ler_usuario_por_pk(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    pk: UsuarioPK = UsuarioPK(dumbledore.pk_usuario)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido == dumbledore


@applier_trans(dbs, assert_db_ok)
def test_ler_usuario_por_login(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuarioUK(dumbledore.login))
    assert lido == dumbledore


@applier_trans(dbs, assert_db_ok)
def test_criar_e_ler_usuario(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = snape_sem_pk
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == snape.pk_usuario

    lido1: DadosUsuario | None = dao.buscar_por_pk(pk)
    lido2: DadosUsuario | None = dao.buscar_por_login(LoginUsuarioUK(snape.login))

    assert lido1 == snape
    assert lido2 == snape
    assert lido1 is not lido2
    assert lido1 is not snape
    assert lido2 is not snape


@applier_trans(dbs, assert_db_ok)
def test_ler_usuario_por_pk_nao_existe(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    lido: DadosUsuario | None = dao.buscar_por_pk(UsuarioPK(lixo2))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_ler_usuario_por_login_nao_existe(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuarioUK(lixo4))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_por_pk(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    pk1: UsuarioPK = UsuarioPK(harry_potter.pk_usuario)
    pk2: UsuarioPK = UsuarioPK(dumbledore.pk_usuario)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2])
    assert lido == parte_usuarios


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_por_pk_nao_existem(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    pk1: UsuarioPK = UsuarioPK(lixo1)
    pk2: UsuarioPK = UsuarioPK(lixo2)
    pk3: UsuarioPK = UsuarioPK(lixo3)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_por_pk_alguns_existem(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    pk1: UsuarioPK = UsuarioPK(lixo3)
    pk2: UsuarioPK = UsuarioPK(harry_potter.pk_usuario)
    pk3: UsuarioPK = UsuarioPK(lixo1)
    pk4: UsuarioPK = UsuarioPK(dumbledore.pk_usuario)
    pk5: UsuarioPK = UsuarioPK(lixo2)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5])
    assert lido == parte_usuarios


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_por_login(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    n1: LoginUsuarioUK = LoginUsuarioUK(dumbledore.login)
    n2: LoginUsuarioUK = LoginUsuarioUK(harry_potter.login)
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2])
    assert lido == parte_usuarios


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_por_login_nao_existem(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    n1: LoginUsuarioUK = LoginUsuarioUK(lixo4)
    n2: LoginUsuarioUK = LoginUsuarioUK(lixo5)
    n3: LoginUsuarioUK = LoginUsuarioUK(lixo6)
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2, n3])
    assert lido == []


@applier_trans(dbs, assert_db_ok)
def test_listar_usuarios_por_login_alguns_existem(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    n1: LoginUsuarioUK = LoginUsuarioUK(dumbledore.login)
    n2: LoginUsuarioUK = LoginUsuarioUK(lixo4)
    n3: LoginUsuarioUK = LoginUsuarioUK(harry_potter.login)
    n4: LoginUsuarioUK = LoginUsuarioUK(lixo5)
    n5: LoginUsuarioUK = LoginUsuarioUK(lixo6)
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2, n3, n4, n5])
    assert lido == parte_usuarios


@applier_trans(dbs, assert_db_ok)
def test_listar_tudo(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    lido: list[DadosUsuario] = dao.listar()
    assert lido == todos_usuarios


@applier_trans(dbs, assert_db_ok)
def test_listar_tudo_apos_insercao(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = snape_sem_pk
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == snape.pk_usuario
    lido: list[DadosUsuario] = dao.listar()
    esperado: list[DadosUsuario] = todos_usuarios[:]
    esperado.append(snape)
    assert lido == esperado


@applier_trans(dbs, assert_db_ok)
def test_excluir_usuario_por_pk(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    pk: UsuarioPK = UsuarioPK(voldemort.pk_usuario)
    lido1: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido1 == voldemort
    assert dao.deletar_por_pk(pk)
    lido2: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido2 is None


# @applier_trans(dbs, assert_db_ok)
# def test_excluir_usuario_por_pk_cascateia_permissao(c: TransactedConnection) -> None:
#     dao: UsuarioDAO = UsuarioDAOImpl(c)
#     pk: UsuarioPK = UsuarioPK(harry_potter.pk_usuario)
#
#     dao.deletar_por_pk(pk)
#
#     assert False # INCOMPLETO


@applier_trans(dbs, assert_db_ok)
def test_excluir_usuario_por_pk_nao_existe(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    pk: UsuarioPK = UsuarioPK(lixo2)
    assert not dao.deletar_por_pk(pk)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_salvar_usuario_com_pk(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuario = DadosUsuario(voldemort.pk_usuario, "Snape", 1, sectumsempra)
    assert dao.salvar_com_pk(dados)  # Substitui Voldemort por Snape.

    pk: UsuarioPK = UsuarioPK(voldemort.pk_usuario)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido == dados


@applier_trans(dbs, assert_db_ok)
def test_salvar_usuario_com_pk_nao_existe(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuario = DadosUsuario(lixo3, "Snape", 1, sectumsempra)
    assert not dao.salvar_com_pk(dados)  # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: UsuarioPK = UsuarioPK(lixo3)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_criar_usuario_tipo_nao_existe(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK("Snape", lixo1, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuarioUK(snape.login))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_criar_usuario_login_repetido(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK("Harry Potter", 0, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuarioUK(harry_potter.login))
    assert lido == harry_potter


@applier_trans(dbs, assert_db_ok)
def test_criar_usuario_login_curto(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK(nome_curto, 0, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuarioUK(nome_curto))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_criar_usuario_login_longo(c: TransactedConnection) -> None:
    dao: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK(nome_longo, 0, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuarioUK(nome_longo))
    assert lido is None


# TODO:
# Testar listar_por_permissao
