from .fixtures import *
from connection.conn import IntegrityViolationException
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioSemPK, SegredoPK, LoginUsuario
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.usuario.usuario_dao_impl import UsuarioDAOImpl
from pytest import raises

@db.decorator
def test_instanciar() -> None:
    s: UsuarioDAO = UsuarioDAOImpl(db.raiz)
    assert s == UsuarioDAO.instance()

@db.transacted
def test_criar_usuario() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuarioSemPK = snape_sem_pk
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == snape.pk_usuario

@db.transacted
def test_ler_usuario_por_pk() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    pk: UsuarioPK = UsuarioPK(dumbledore.pk_usuario)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido == dumbledore

@db.transacted
def test_ler_usuario_por_login() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    lido: DadosUsuario | None = dao.buscar_por_login(login_dumbledore)
    assert lido == dumbledore

@db.transacted
def test_criar_e_ler_usuario() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuarioSemPK = snape_sem_pk
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == snape.pk_usuario

    lido1: DadosUsuario | None = dao.buscar_por_pk(pk)
    lido2: DadosUsuario | None = dao.buscar_por_login(login_snape)

    assert lido1 == snape
    assert lido2 == snape
    assert lido1 is not lido2
    assert lido1 is not snape
    assert lido2 is not snape

@db.transacted
def test_ler_usuario_por_pk_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    lido: DadosUsuario | None = dao.buscar_por_pk(UsuarioPK(lixo2))
    assert lido is None

@db.transacted
def test_ler_usuario_por_login_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    lido: DadosUsuario | None = dao.buscar_por_login(login_lixo_1)
    assert lido is None

@db.transacted
def test_listar_usuarios_por_pk() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    pk1: UsuarioPK = UsuarioPK(harry_potter.pk_usuario)
    pk2: UsuarioPK = UsuarioPK(dumbledore.pk_usuario)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2])
    assert lido == parte_usuarios

@db.transacted
def test_listar_usuarios_por_pk_nao_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    pk1: UsuarioPK = UsuarioPK(lixo1)
    pk2: UsuarioPK = UsuarioPK(lixo2)
    pk3: UsuarioPK = UsuarioPK(lixo3)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []

@db.transacted
def test_listar_usuarios_por_pk_alguns_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    pk1: UsuarioPK = UsuarioPK(lixo3)
    pk2: UsuarioPK = UsuarioPK(harry_potter.pk_usuario)
    pk3: UsuarioPK = UsuarioPK(lixo1)
    pk4: UsuarioPK = UsuarioPK(dumbledore.pk_usuario)
    pk5: UsuarioPK = UsuarioPK(lixo2)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5])
    assert lido == parte_usuarios

@db.transacted
def test_listar_usuarios_por_login() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    n1: LoginUsuario = login_dumbledore
    n2: LoginUsuario = login_harry_potter
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2])
    assert lido == parte_usuarios

@db.transacted
def test_listar_usuarios_por_login_nao_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    n1: LoginUsuario = login_lixo_1
    n2: LoginUsuario = login_lixo_2
    n3: LoginUsuario = login_lixo_3
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2, n3])
    assert lido == []

@db.transacted
def test_listar_usuarios_por_login_alguns_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    n1: LoginUsuario = login_dumbledore
    n2: LoginUsuario = login_lixo_1
    n3: LoginUsuario = login_harry_potter
    n4: LoginUsuario = login_lixo_2
    n5: LoginUsuario = login_lixo_3
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2, n3, n4, n5])
    assert lido == parte_usuarios

@db.transacted
def test_listar_tudo() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    lido: list[DadosUsuario] = dao.listar()
    assert lido == todos_usuarios

@db.transacted
def test_listar_tudo_apos_insercao() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuarioSemPK = snape_sem_pk
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == snape.pk_usuario
    lido: list[DadosUsuario] = dao.listar()
    esperado: list[DadosUsuario] = todos_usuarios[:]
    esperado.append(snape)
    assert lido == esperado

@db.transacted
def test_excluir_usuario_por_pk() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    pk: UsuarioPK = UsuarioPK(voldemort.pk_usuario)
    lido1: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido1 == voldemort
    assert dao.deletar_por_pk(pk)
    lido2: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido2 is None

#@db.transacted
#def test_excluir_usuario_por_pk_cascateia_permissao() -> None:
#    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
#    pk: UsuarioPK = UsuarioPK(harry_potter.pk_usuario)
#
#    dao.deletar_por_pk(pk)
#
#    assert False # INCOMPLETO

@db.transacted
def test_excluir_usuario_por_pk_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    pk: UsuarioPK = UsuarioPK(lixo2)
    assert not dao.deletar_por_pk(pk)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_salvar_usuario_com_pk() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuario = DadosUsuario(voldemort.pk_usuario, "Snape", 1, sectumsempra)
    assert dao.salvar_com_pk(dados) # Substitui Voldemort por Snape.

    pk: UsuarioPK = UsuarioPK(voldemort.pk_usuario)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido == dados

@db.transacted
def test_salvar_usuario_com_pk_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuario = DadosUsuario(lixo3, "Snape", 1, sectumsempra)
    assert not dao.salvar_com_pk(dados) # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: UsuarioPK = UsuarioPK(lixo3)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_criar_usuario_tipo_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK("Snape", lixo1, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(login_snape)
    assert lido is None

@db.transacted
def test_criar_usuario_login_repetido() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK("Harry Potter", 0, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(login_harry_potter)
    assert lido == harry_potter

@db.transacted
def test_criar_usuario_login_curto() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK(nome_curto, 0, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuario(nome_curto))
    assert lido is None

@db.transacted
def test_criar_usuario_login_longo() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl(db.raiz)
    dados: DadosUsuarioSemPK = DadosUsuarioSemPK(nome_longo, 0, sectumsempra)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuario(nome_longo))
    assert lido is None

# TODO:
# Testar listar_por_permissao