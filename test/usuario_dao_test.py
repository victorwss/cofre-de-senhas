from .db_test_util import DbTestConfig
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioSemPK, SegredoPK, LoginUsuario
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.usuario.usuario_dao_impl import UsuarioDAOImpl

db: DbTestConfig = DbTestConfig("test/cofre-teste.db", "test/cofre-teste-run.db")

alohomora       : str = "azOtltNwtdffb9debae4824dae79896e7b0a8d401fbd4e44fa99fac184b107f564"
avada_kedavra   : str = "FqOZTDhozi01501c59c673335d6d851868ae23e35823cc96b9057c81dfbca306e8"
expecto_patronum: str = "nHknWfqwmLa6d2afe45e8420f15941c1a27265acfdf88a9d45c11a9ca48ba5b12f"
sectumsempra    : str = "ifBgTTmWRy668c168f35e51cc9f9c1334cbd9e084801f71a326d434f3e70b674ad"

"""
INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Harry Potter', 1, 'azOtltNwtdffb9debae4824dae79896e7b0a8d401fbd4e44fa99fac184b107f564'); -- alohomora
INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Voldemort'   , 0, 'FqOZTDhozi01501c59c673335d6d851868ae23e35823cc96b9057c81dfbca306e8'); -- avada kedavra
INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Dumbledore'  , 2, 'nHknWfqwmLa6d2afe45e8420f15941c1a27265acfdf88a9d45c11a9ca48ba5b12f'); -- expecto patronum
"""

tudo = [
    DadosUsuario(1, "Harry Potter", 1, alohomora       ),
    DadosUsuario(2, "Voldemort"   , 0, avada_kedavra   ),
    DadosUsuario(3, "Dumbledore"  , 2, expecto_patronum)
]
parte = [tudo[0], tudo[2]]
snape = DadosUsuario(4, "Snape", 1, sectumsempra)

@db.transacted
def test_criar_usuario() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    dados = DadosUsuarioSemPK("Snape", 1, sectumsempra)
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == 4

@db.transacted
def test_ler_usuario_por_pk() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    pk: UsuarioPK = UsuarioPK(3)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido == tudo[3 - 1]

@db.transacted
def test_ler_usuario_por_login() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuario("Dumbledore"))
    assert lido == tudo[3 - 1]

@db.transacted
def test_criar_e_ler_usuario() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    dados = DadosUsuarioSemPK("Snape", 1, sectumsempra)
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == 4

    lido1: DadosUsuario | None = dao.buscar_por_pk(pk)
    lido2: DadosUsuario | None = dao.buscar_por_login(LoginUsuario("Snape"))

    assert lido1 == snape
    assert lido2 == snape
    assert lido1 is not lido2

@db.transacted
def test_ler_usuario_por_pk_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    lido: DadosUsuario | None = dao.buscar_por_pk(UsuarioPK(666))
    assert lido is None

@db.transacted
def test_ler_usuario_por_login_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    lido: DadosUsuario | None = dao.buscar_por_login(LoginUsuario("Dollynho"))
    assert lido is None

@db.transacted
def test_listar_usuarios() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    pk1: UsuarioPK = UsuarioPK(1)
    pk2: UsuarioPK = UsuarioPK(3)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2])
    assert lido == parte

@db.transacted
def test_listar_usuarios_nao_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    pk1: UsuarioPK = UsuarioPK(444)
    pk2: UsuarioPK = UsuarioPK(555)
    pk3: UsuarioPK = UsuarioPK(666)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []

@db.transacted
def test_listar_usuarios_alguns_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    pk1: UsuarioPK = UsuarioPK(666)
    pk2: UsuarioPK = UsuarioPK(1)
    pk3: UsuarioPK = UsuarioPK(555)
    pk4: UsuarioPK = UsuarioPK(3)
    pk5: UsuarioPK = UsuarioPK(444)
    lido: list[DadosUsuario] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5])
    assert lido == parte

@db.transacted
def test_listar_usuarios_por_login() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    n1: LoginUsuario = LoginUsuario("Dumbledore")
    n2: LoginUsuario = LoginUsuario("Harry Potter")
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2])
    assert lido == parte

@db.transacted
def test_listar_usuarios_por_login_nao_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    n1: LoginUsuario = LoginUsuario("Melancia")
    n2: LoginUsuario = LoginUsuario("Cachorro")
    n3: LoginUsuario = LoginUsuario("Elefante")
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2, n3])
    assert lido == []

@db.transacted
def test_listar_usuarios_por_login_alguns_existem() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    n1: LoginUsuario = LoginUsuario("Dumbledore")
    n2: LoginUsuario = LoginUsuario("Melancia")
    n3: LoginUsuario = LoginUsuario("Harry Potter")
    n4: LoginUsuario = LoginUsuario("Cachorro")
    n5: LoginUsuario = LoginUsuario("Elefante")
    lido: list[DadosUsuario] = dao.listar_por_logins([n1, n2, n3, n4, n5])
    assert lido == parte

@db.transacted
def test_listar_tudo() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    lido: list[DadosUsuario] = dao.listar()
    assert lido == tudo

@db.transacted
def test_listar_tudo_apos_insercao() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    dados = DadosUsuarioSemPK("Snape", 1, sectumsempra)
    pk: UsuarioPK = dao.criar(dados)
    assert pk.pk_usuario == 4
    lido: list[DadosUsuario] = dao.listar()
    esperado: list[DadosUsuario] = tudo[:]
    esperado.append(snape)
    assert lido == esperado

@db.transacted
def test_excluir_usuario_por_pk() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    pk: UsuarioPK = UsuarioPK(2)
    lido1: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido1 == tudo[2 - 1]
    dao.deletar_por_pk(pk)
    lido2: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido2 is None

@db.transacted
def test_excluir_usuario_por_pk_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    pk: UsuarioPK = UsuarioPK(666)
    dao.deletar_por_pk(pk)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_salvar_usuario_com_pk() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    dados: DadosUsuario = DadosUsuario(2, "Snape", 1, sectumsempra)
    dao.salvar_com_pk(dados)

    pk: UsuarioPK = UsuarioPK(2)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido == dados

@db.transacted
def test_salvar_usuario_com_pk_nao_existe() -> None:
    dao: UsuarioDAOImpl = UsuarioDAOImpl()
    dados: DadosUsuario = DadosUsuario(666, "Snape", 1, sectumsempra)
    dao.salvar_com_pk(dados) # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: UsuarioPK = UsuarioPK(666)
    lido: DadosUsuario | None = dao.buscar_por_pk(pk)
    assert lido is None

# TODO:
# Testar listar_por_permissao