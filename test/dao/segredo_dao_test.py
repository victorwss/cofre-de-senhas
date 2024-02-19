from ..db_test_util import applier, applier_trans, DbTestConfig
from ..fixtures import (
    dbs, assert_db_ok,
    todos_segredos, parte_segredos, visiv_segredos, harry_segredos, hermi_segredos,
    harry_potter, dumbledore, voldemort, hermione, snape, snape_sem_pk,
    dbz, lotr, star_wars, oppenheimer, star_trek, star_trek_sem_pk,
    qa, aplicacao, integracao, producao,
    lixo1, lixo2, lixo3
)
from connection.trans import TransactedConnection
from connection.conn import IntegrityViolationException
from cofre_de_senhas.dao import (
    CategoriaDAO, UsuarioDAO, SegredoDAO,
    BuscaPermissaoPorLogin, SegredoPK, DadosSegredo, DadosSegredoSemPK, CampoDeSegredo, PermissaoDeSegredo,
    DadosCategoria, CategoriaDeSegredo, UsuarioPK, DadosUsuarioSemPK, LoginUsuarioUK
)
from cofre_de_senhas.categoria.categoria_dao_impl import CategoriaDAOImpl
from cofre_de_senhas.segredo.segredo_dao_impl import SegredoDAOImpl
from cofre_de_senhas.usuario.usuario_dao_impl import UsuarioDAOImpl
from pytest import raises


@applier(dbs, assert_db_ok)
def test_instanciar(db: DbTestConfig) -> None:
    s: SegredoDAO = SegredoDAOImpl(db.conn)
    assert s == SegredoDAO.instance()


@applier_trans(dbs, assert_db_ok)
def test_criar_segredo(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    dados: DadosSegredoSemPK = star_trek_sem_pk
    pk: SegredoPK = dao.criar(dados)
    assert pk.pk_segredo == star_trek.pk_segredo


@applier_trans(dbs, assert_db_ok)
def test_ler_segredo_por_pk(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk: SegredoPK = SegredoPK(3)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido == star_wars


@applier_trans(dbs, assert_db_ok)
def test_criar_e_ler_segredo(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    dados: DadosSegredoSemPK = star_trek_sem_pk
    pk: SegredoPK = dao.criar(dados)
    assert pk.pk_segredo == star_trek.pk_segredo

    lido1: DadosSegredo | None = dao.buscar_por_pk(pk)

    assert lido1 == star_trek
    assert lido1 is not star_trek


@applier_trans(dbs, assert_db_ok)
def test_ler_segredo_por_pk_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    lido: DadosSegredo | None = dao.buscar_por_pk(SegredoPK(666))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_por_pk(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk1: SegredoPK = SegredoPK(lotr.pk_segredo)
    pk2: SegredoPK = SegredoPK(star_wars.pk_segredo)
    lido: list[DadosSegredo] = dao.listar_por_pks([pk1, pk2])
    assert lido == parte_segredos


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_por_pk_nao_existem(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk1: SegredoPK = SegredoPK(lixo1)
    pk2: SegredoPK = SegredoPK(lixo2)
    pk3: SegredoPK = SegredoPK(lixo3)
    lido: list[DadosSegredo] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_por_pk_alguns_existem(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk1: SegredoPK = SegredoPK(lixo3)
    pk2: SegredoPK = SegredoPK(lotr.pk_segredo)
    pk3: SegredoPK = SegredoPK(lixo1)
    pk4: SegredoPK = SegredoPK(star_wars.pk_segredo)
    pk5: SegredoPK = SegredoPK(lixo2)
    lido: list[DadosSegredo] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5])
    assert lido == parte_segredos


@applier_trans(dbs, assert_db_ok)
def test_listar_tudo(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    lido: list[DadosSegredo] = dao.listar()
    assert lido == todos_segredos


@applier_trans(dbs, assert_db_ok)
def test_listar_tudo_apos_insercao(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    dados: DadosSegredoSemPK = star_trek_sem_pk
    pk: SegredoPK = dao.criar(dados)
    assert pk.pk_segredo == star_trek.pk_segredo
    lido: list[DadosSegredo] = dao.listar()
    esperado: list[DadosSegredo] = todos_segredos[:]
    esperado.append(star_trek)
    assert lido == esperado


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_visiveis_1(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    lido: list[DadosSegredo] = dao.listar_visiveis(LoginUsuarioUK(harry_potter.login))
    assert lido == harry_segredos


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_visiveis_2(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    lido: list[DadosSegredo] = dao.listar_visiveis(LoginUsuarioUK(voldemort.login))
    assert lido == visiv_segredos


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_visiveis_3(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    # Dumbledore é chaveiro, mas não é responsabilidade do DAO verificar isso.
    lido: list[DadosSegredo] = dao.listar_visiveis(LoginUsuarioUK(dumbledore.login))
    assert lido == visiv_segredos


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_visiveis_4(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    lido: list[DadosSegredo] = dao.listar_visiveis(LoginUsuarioUK(hermione.login))
    assert lido == visiv_segredos


@applier_trans(dbs, assert_db_ok)
def test_listar_segredos_visiveis_5(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    lido: list[DadosSegredo] = dao.listar_visiveis(LoginUsuarioUK(snape.login))
    assert lido == visiv_segredos


@applier_trans(dbs, assert_db_ok)
def test_excluir_segredo_por_pk(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk: SegredoPK = SegredoPK(dbz.pk_segredo)
    lido1: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido1 == dbz
    assert dao.deletar_por_pk(pk)
    lido2: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido2 is None


@applier_trans(dbs, assert_db_ok)
def test_excluir_segredo_por_pk_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk: SegredoPK = SegredoPK(lixo2)
    assert not dao.deletar_por_pk(pk)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_salvar_segredo_com_pk(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    dados: DadosSegredo = DadosSegredo(dbz.pk_segredo, "Pokémon", "Segredos da Equipe Rocket", 1)
    assert dao.salvar_com_pk(dados)  # Transforma Dragon Ball Z em Pokémon.

    pk: SegredoPK = SegredoPK(dbz.pk_segredo)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido == dados


@applier_trans(dbs, assert_db_ok)
def test_salvar_segredo_com_pk_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    dados: DadosSegredo = DadosSegredo(lixo3, "Pokémon", "Segredos da Equipe Rocket", 1)
    assert not dao.salvar_com_pk(dados)  # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: SegredoPK = SegredoPK(lixo3)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_ler_campos_segredo(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == [
        CampoDeSegredo(star_wars.pk_segredo, "Nome do cara vestido de preto", "Darth Vader"),
        CampoDeSegredo(star_wars.pk_segredo, "Nome do imperador", "Palpatine"),
        CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "C3PO")
    ]


@applier_trans(dbs, assert_db_ok)
def test_ler_campos_segredo_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    pk: SegredoPK = SegredoPK(lixo1)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == []


@applier_trans(dbs, assert_db_ok)
def test_criar_campo_segredo(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    campo: CampoDeSegredo = CampoDeSegredo(star_wars.pk_segredo, "Pequeno, mas poderoso", "Yoda")
    assert dao.criar_campo_segredo(campo)
    pk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == [
        CampoDeSegredo(star_wars.pk_segredo, "Nome do cara vestido de preto", "Darth Vader"),
        CampoDeSegredo(star_wars.pk_segredo, "Nome do imperador", "Palpatine"),
        CampoDeSegredo(star_wars.pk_segredo, "Pequeno, mas poderoso", "Yoda"),
        CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "C3PO")
    ]


@applier_trans(dbs, assert_db_ok)
def test_criar_campo_segredo_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    campo: CampoDeSegredo = CampoDeSegredo(lixo1, "Patati", "Patatá")

    with raises(IntegrityViolationException):
        dao.criar_campo_segredo(campo)

    pk: SegredoPK = SegredoPK(lixo1)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == []


@applier_trans(dbs, assert_db_ok)
def test_criar_campo_segredo_duplicado(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    campo: CampoDeSegredo = CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "R2D2")

    with raises(IntegrityViolationException):
        dao.criar_campo_segredo(campo)

    pk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == [
        CampoDeSegredo(star_wars.pk_segredo, "Nome do cara vestido de preto", "Darth Vader"),
        CampoDeSegredo(star_wars.pk_segredo, "Nome do imperador", "Palpatine"),
        CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "C3PO")
    ]


@applier_trans(dbs, assert_db_ok)
def test_criar_permissao(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(hermione.pk_usuario, oppenheimer.pk_segredo, 2)
    assert dao.criar_permissao(perm1)

    lido: list[DadosSegredo] = dao.listar_visiveis(LoginUsuarioUK(hermione.login))
    assert lido == hermi_segredos

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(oppenheimer.pk_segredo, "Hermione")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm1 == perm2


@applier_trans(dbs, assert_db_ok)
def test_criar_permissao_usuario_nao_existe(c: TransactedConnection) -> None:
    dao1: SegredoDAO = SegredoDAOImpl(c)
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(snape.pk_usuario, dbz.pk_segredo, 2)

    with raises(IntegrityViolationException):
        dao1.criar_permissao(perm1)

    dao2: UsuarioDAO = UsuarioDAOImpl(c)
    dados: DadosUsuarioSemPK = snape_sem_pk
    pk: UsuarioPK = dao2.criar(dados)
    assert pk.pk_usuario == snape.pk_usuario

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(snape.pk_usuario, "Snape")
    perm2: PermissaoDeSegredo | None = dao1.buscar_permissao(busca)
    assert perm2 is None


@applier_trans(dbs, assert_db_ok)
def test_criar_permissao_segredo_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(hermione.pk_usuario, lixo1, 2)

    with raises(IntegrityViolationException):
        dao.criar_permissao(perm1)

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lixo1, "Hermione")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm2 is None


@applier_trans(dbs, assert_db_ok)
def test_criar_permissao_tipo_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(hermione.pk_usuario, dbz.pk_segredo, lixo1)

    with raises(IntegrityViolationException):
        dao.criar_permissao(perm1)

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(dbz.pk_segredo, "Hermione")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm2 is None


@applier_trans(dbs, assert_db_ok)
def test_criar_permissao_ja_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(harry_potter.pk_usuario, dbz.pk_segredo, 3)

    with raises(IntegrityViolationException):
        dao.criar_permissao(perm1)

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(dbz.pk_segredo, "Harry Potter")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm2 == PermissaoDeSegredo(harry_potter.pk_usuario, dbz.pk_segredo, 1)


@applier_trans(dbs, assert_db_ok)
def test_buscar_permissao_1(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(dbz.pk_segredo, "Harry Potter")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm == PermissaoDeSegredo(harry_potter.pk_usuario, dbz.pk_segredo, 1)


@applier_trans(dbs, assert_db_ok)
def test_buscar_permissao_2(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lotr.pk_segredo, "Harry Potter")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm == PermissaoDeSegredo(harry_potter.pk_usuario, lotr.pk_segredo, 2)


@applier_trans(dbs, assert_db_ok)
def test_buscar_permissao_nao_tem(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lotr.pk_segredo, "Hermione")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm is None


@applier_trans(dbs, assert_db_ok)
def test_buscar_permissao_login_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lotr.pk_segredo, "Dollynho")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm is None


@applier_trans(dbs, assert_db_ok)
def test_buscar_permissao_segredo_nao_existe(c: TransactedConnection) -> None:
    dao: SegredoDAO = SegredoDAOImpl(c)
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lixo1, "Harry Potter")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm is None


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_segredo(c: TransactedConnection) -> None:
    dao1: SegredoDAO = SegredoDAOImpl(c)
    cs: CategoriaDeSegredo = CategoriaDeSegredo(star_wars.pk_segredo, qa.pk_categoria)
    assert dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAO = CategoriaDAOImpl(c)
    spk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == [producao, qa]


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_segredo_com_segredo_que_nao_existe(c: TransactedConnection) -> None:
    dao1: SegredoDAO = SegredoDAOImpl(c)
    cs: CategoriaDeSegredo = CategoriaDeSegredo(lixo1, qa.pk_categoria)

    with raises(IntegrityViolationException):
        dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAO = CategoriaDAOImpl(c)
    spk: SegredoPK = SegredoPK(lixo1)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == []


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_segredo_com_categoria_que_nao_existe(c: TransactedConnection) -> None:
    dao1: SegredoDAO = SegredoDAOImpl(c)
    cs: CategoriaDeSegredo = CategoriaDeSegredo(star_wars.pk_segredo, lixo3)

    with raises(IntegrityViolationException):
        dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAO = CategoriaDAOImpl(c)
    spk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == [producao]


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_segredo_ja_existe(c: TransactedConnection) -> None:
    dao1: SegredoDAO = SegredoDAOImpl(c)
    cs: CategoriaDeSegredo = CategoriaDeSegredo(dbz.pk_segredo, qa.pk_categoria)

    with raises(IntegrityViolationException):
        dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAO = CategoriaDAOImpl(c)
    spk: SegredoPK = SegredoPK(dbz.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == [qa]


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_segredo(c: TransactedConnection) -> None:
    dao2: CategoriaDAO = CategoriaDAOImpl(c)
    spk: SegredoPK = SegredoPK(lotr.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)
    assert dados == [aplicacao, integracao]


@applier_trans(dbs, assert_db_ok)
def test_buscar_categoria_segredo_nao_existe(c: TransactedConnection) -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl(c)
    spk: SegredoPK = SegredoPK(lixo1)
    dados: list[DadosCategoria] = dao.listar_por_segredo(spk)
    assert dados == []


# @applier_trans(dbs, assert_db_ok)
# def test_criar_listar_por_permissao(c: TransactedConnection) -> None:
#     pk: SegredoPk = SegredoPK(dbz.pk_segredo)
#     dao: UsuarioDAOImpl = UsuarioDAOImpl(c)
#     permissoes: list[DadosUsuarioComPermissao] = dao.listar_por_permissao(pk)
#     assert permissoes = [
#         DadosUsuarioComPermissao(harry_potter.pk_usuario, harry_potter.login, harry_potter.fk_nivel_acesso, harry_potter)
#     ]
