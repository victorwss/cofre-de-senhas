from ..db_test_util import applier, applier_trans, DbTestConfig
from .fixtures import (
    dbs, assert_db_ok, mix,
    todas_categorias, parte_categorias, nome_longo, nome_nao_existe,
    millenium_falcon, nome_millenium_falcon, dados_millenium_falcon,
    api, qa, producao, homologacao, desenvolvimento, servidor, nome_qa, nome_producao,
    lixo1, lixo2, lixo3, lixo4, lixo5, lixo6
)
from connection.trans import TransactedConnection
from connection.conn import IntegrityViolationException
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, NomeCategoria
from cofre_de_senhas.categoria.categoria_dao_impl import CategoriaDAOImpl
from pytest import raises


@applier(dbs, assert_db_ok)
def test_instanciar(db: DbTestConfig) -> None:
    s: CategoriaDAO = CategoriaDAOImpl(db.conn)
    assert s == CategoriaDAO.instance()


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoriaSemPK = dados_millenium_falcon
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == millenium_falcon.pk_categoria


@applier_trans(dbs, assert_db_ok)
def test_ler_categoria_por_pk(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    pk: CategoriaPK = CategoriaPK(producao.pk_categoria)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == producao


@applier_trans(dbs, assert_db_ok)
def test_ler_categoria_por_nome(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    lido: DadosCategoria | None = dao.buscar_por_nome(nome_producao)
    assert lido == producao


@applier_trans(dbs, assert_db_ok)
def test_ler_categoria_por_nome_case_sensitive(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    lido1: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(nome_producao.valor.lower()))
    assert lido1 is None
    lido2: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(nome_qa.valor.lower()))
    assert lido2 is None


@applier_trans(dbs, assert_db_ok)
def test_criar_e_ler_categoria(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoriaSemPK = dados_millenium_falcon
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == millenium_falcon.pk_categoria

    lido1: DadosCategoria | None = dao.buscar_por_pk(pk)
    lido2: DadosCategoria | None = dao.buscar_por_nome(nome_millenium_falcon)

    assert lido1 == millenium_falcon
    assert lido2 == millenium_falcon
    assert lido1 is not lido2
    assert lido1 is not millenium_falcon
    assert lido2 is not millenium_falcon


@applier_trans(dbs, assert_db_ok)
def test_ler_categoria_por_pk_nao_existe(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    lido: DadosCategoria | None = dao.buscar_por_pk(CategoriaPK(lixo3))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_ler_categoria_por_nome_nao_existe(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    lido: DadosCategoria | None = dao.buscar_por_nome(nome_nao_existe)
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_por_pk(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    pk1: CategoriaPK = CategoriaPK(api.pk_categoria)
    pk2: CategoriaPK = CategoriaPK(producao.pk_categoria)
    pk3: CategoriaPK = CategoriaPK(homologacao.pk_categoria)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == parte_categorias


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_por_pk_nao_existem(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    pk1: CategoriaPK = CategoriaPK(lixo2)
    pk2: CategoriaPK = CategoriaPK(lixo1)
    pk3: CategoriaPK = CategoriaPK(lixo3)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_por_pk_alguns_existem(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    pk1: CategoriaPK = CategoriaPK(lixo3)
    pk2: CategoriaPK = CategoriaPK(api.pk_categoria)
    pk3: CategoriaPK = CategoriaPK(lixo2)
    pk4: CategoriaPK = CategoriaPK(homologacao.pk_categoria)
    pk5: CategoriaPK = CategoriaPK(producao.pk_categoria)
    pk6: CategoriaPK = CategoriaPK(lixo1)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5, pk6])
    assert lido == parte_categorias


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_por_nome(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    n1: NomeCategoria = NomeCategoria(homologacao.nome)
    n2: NomeCategoria = NomeCategoria(api.nome)
    n3: NomeCategoria = NomeCategoria(producao.nome)
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3])
    assert lido == parte_categorias


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_por_nome_nao_existem(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    n1: NomeCategoria = NomeCategoria(lixo4)
    n2: NomeCategoria = NomeCategoria(lixo5)
    n3: NomeCategoria = NomeCategoria(lixo6)
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3])
    assert lido == []


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_por_nome_alguns_existem(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    n1: NomeCategoria = NomeCategoria(homologacao.nome)
    n2: NomeCategoria = NomeCategoria(lixo4)
    n3: NomeCategoria = NomeCategoria(api.nome)
    n4: NomeCategoria = NomeCategoria(producao.nome)
    n5: NomeCategoria = NomeCategoria(lixo5)
    n6: NomeCategoria = NomeCategoria(lixo6)
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3, n4, n5, n6])
    assert lido == parte_categorias


@applier_trans(dbs, assert_db_ok)
def test_listar_categorias_por_nome_case_sensitive(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    n1: NomeCategoria = NomeCategoria(homologacao.nome.lower())
    n2: NomeCategoria = NomeCategoria(api.nome.lower())
    n3: NomeCategoria = NomeCategoria(producao.nome.upper())
    n4: NomeCategoria = NomeCategoria(qa.nome.lower())
    n5: NomeCategoria = NomeCategoria(mix(servidor.nome))
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3, n4, n5])
    assert lido == []


@applier_trans(dbs, assert_db_ok)
def test_listar_tudo(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    lido: list[DadosCategoria] = dao.listar()
    assert lido == todas_categorias


@applier_trans(dbs, assert_db_ok)
def test_listar_tudo_apos_insercao(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoriaSemPK = dados_millenium_falcon
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == millenium_falcon.pk_categoria
    lido: list[DadosCategoria] = dao.listar()
    esperado: list[DadosCategoria] = todas_categorias[:]
    esperado.append(millenium_falcon)
    assert lido == esperado


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_por_pk(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    pk: CategoriaPK = CategoriaPK(desenvolvimento.pk_categoria)
    lido1: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido1 == desenvolvimento
    dao.deletar_por_pk(pk)
    lido2: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido2 is None


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_por_pk_viola_chave_estrangeira(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    pk: CategoriaPK = CategoriaPK(qa.pk_categoria)

    with raises(IntegrityViolationException):
        dao.deletar_por_pk(pk)

    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == qa


@applier_trans(dbs, assert_db_ok)
def test_excluir_categoria_por_pk_nao_existe(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    pk: CategoriaPK = CategoriaPK(lixo2)
    dao.deletar_por_pk(pk)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_salvar_categoria_com_pk(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, "Pikachu")
    dao.salvar_com_pk(dados)  # Transforma QA em Pikachu.

    pk: CategoriaPK = CategoriaPK(qa.pk_categoria)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == dados


@applier_trans(dbs, assert_db_ok)
def test_salvar_categoria_com_pk_nao_existe(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoria = DadosCategoria(lixo3, "Pikachu")
    dao.salvar_com_pk(dados)  # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: CategoriaPK = CategoriaPK(lixo3)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nome_repetido(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoriaSemPK = DadosCategoriaSemPK(qa.nome)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido == qa


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nome_curto(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoriaSemPK = DadosCategoriaSemPK("")

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(""))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_criar_categoria_nome_longo(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoriaSemPK = DadosCategoriaSemPK(nome_longo)

    with raises(IntegrityViolationException):
        dao.criar(dados)

    lido: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(nome_longo))
    assert lido is None


@applier_trans(dbs, assert_db_ok)
def test_salvar_categoria_com_pk_nome_repetido(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, producao.nome)

    with raises(IntegrityViolationException):
        dao.salvar_com_pk(dados)

    lido1: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido1 == qa

    lido2: DadosCategoria | None = dao.buscar_por_nome(nome_producao)
    assert lido2 == producao


@applier_trans(dbs, assert_db_ok)
def test_salvar_categoria_com_pk_nome_curto(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, "")

    with raises(IntegrityViolationException):
        dao.salvar_com_pk(dados)

    lido1: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido1 == qa

    lido2: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(""))
    assert lido2 is None


@applier_trans(dbs, assert_db_ok)
def test_salvar_categoria_com_pk_nome_longo(c: TransactedConnection) -> None:
    dao: CategoriaDAO = CategoriaDAOImpl(c)
    dados: DadosCategoria = DadosCategoria(qa.pk_categoria, nome_longo)

    with raises(IntegrityViolationException):
        dao.salvar_com_pk(dados)

    lido1: DadosCategoria | None = dao.buscar_por_nome(nome_qa)
    assert lido1 == qa

    lido2: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria(nome_longo))
    assert lido2 is None


# TODO:
# Testar listar_por_segredo
