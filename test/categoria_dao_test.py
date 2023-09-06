from .db_test_util import DbTestConfig
from cofre_de_senhas.dao import CategoriaDAO, CategoriaPK, DadosCategoria, DadosCategoriaSemPK, SegredoPK, NomeCategoria
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.categoria.categoria_dao_impl import CategoriaDAOImpl

db: DbTestConfig = DbTestConfig("test/cofre-teste.db", "test/cofre-teste-run.db")

tudo = [
    DadosCategoria(1, "Banco de dados" ), DadosCategoria(2, "Aplicação"), DadosCategoria(3, "Servidor"   ),
    DadosCategoria(4, "API"            ), DadosCategoria(5, "Produção" ), DadosCategoria(6, "Homologação"),
    DadosCategoria(7, "Desenvolvimento"), DadosCategoria(8, "QA"       ), DadosCategoria(9, "Integração" )
]
parte = tudo[3:6]
millenium_falcon = DadosCategoria(10, "Millenium Falcon")

@db.transacted
def test_criar_categoria() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados = DadosCategoriaSemPK("Millenium Falcon")
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == 10

@db.transacted
def test_ler_categoria_por_pk() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk: CategoriaPK = CategoriaPK(5)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == tudo[5 - 1]

@db.transacted
def test_ler_categoria_por_nome() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria("Produção"))
    assert lido == tudo[5 - 1]

@db.transacted
def test_criar_e_ler_categoria() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados = DadosCategoriaSemPK("Millenium Falcon")
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == 10

    lido1: DadosCategoria | None = dao.buscar_por_pk(pk)
    lido2: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria("Millenium Falcon"))

    assert lido1 == millenium_falcon
    assert lido2 == millenium_falcon
    assert lido1 is not lido2

@db.transacted
def test_ler_categoria_por_pk_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: DadosCategoria | None = dao.buscar_por_pk(CategoriaPK(666))
    assert lido is None

@db.transacted
def test_ler_categoria_por_nome_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: DadosCategoria | None = dao.buscar_por_nome(NomeCategoria("Qualidade na Prodam"))
    assert lido is None

@db.transacted
def test_listar_categorias() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk1: CategoriaPK = CategoriaPK(4)
    pk2: CategoriaPK = CategoriaPK(5)
    pk3: CategoriaPK = CategoriaPK(6)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == parte

@db.transacted
def test_listar_categorias_nao_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk1: CategoriaPK = CategoriaPK(444)
    pk2: CategoriaPK = CategoriaPK(555)
    pk3: CategoriaPK = CategoriaPK(666)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []

@db.transacted
def test_listar_categorias_alguns_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk1: CategoriaPK = CategoriaPK(666)
    pk2: CategoriaPK = CategoriaPK(4)
    pk3: CategoriaPK = CategoriaPK(555)
    pk4: CategoriaPK = CategoriaPK(6)
    pk5: CategoriaPK = CategoriaPK(5)
    pk6: CategoriaPK = CategoriaPK(444)
    lido: list[DadosCategoria] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5, pk6])
    assert lido == parte

@db.transacted
def test_listar_categorias_por_nome() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    n1: NomeCategoria = NomeCategoria("Homologação")
    n2: NomeCategoria = NomeCategoria("API")
    n3: NomeCategoria = NomeCategoria("Produção")
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3])
    assert lido == parte

@db.transacted
def test_listar_categorias_por_nome_nao_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    n1: NomeCategoria = NomeCategoria("Melancia")
    n2: NomeCategoria = NomeCategoria("Cachorro")
    n3: NomeCategoria = NomeCategoria("Elefante")
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3])
    assert lido == []

@db.transacted
def test_listar_categorias_por_nome_alguns_existem() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    n1: NomeCategoria = NomeCategoria("Homologação")
    n2: NomeCategoria = NomeCategoria("Melancia")
    n3: NomeCategoria = NomeCategoria("API")
    n4: NomeCategoria = NomeCategoria("Produção")
    n5: NomeCategoria = NomeCategoria("Cachorro")
    n6: NomeCategoria = NomeCategoria("Elefante")
    lido: list[DadosCategoria] = dao.listar_por_nomes([n1, n2, n3, n4, n5, n6])
    assert lido == parte

@db.transacted
def test_listar_tudo() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    lido: list[DadosCategoria] = dao.listar()
    assert lido == tudo

@db.transacted
def test_listar_tudo_apos_insercao() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados = DadosCategoriaSemPK("Millenium Falcon")
    pk: CategoriaPK = dao.criar(dados)
    assert pk.pk_categoria == 10
    lido: list[DadosCategoria] = dao.listar()
    esperado: list[DadosCategoria] = tudo[:]
    esperado.append(millenium_falcon)
    assert lido == esperado

@db.transacted
def test_excluir_categoria_por_pk() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk: CategoriaPK = CategoriaPK(8)
    lido1: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido1 == tudo[8 - 1]
    dao.deletar_por_pk(pk)
    lido2: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido2 is None

@db.transacted
def test_excluir_categoria_por_pk_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    pk: CategoriaPK = CategoriaPK(666)
    dao.deletar_por_pk(pk)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_salvar_categoria_com_pk() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoria = DadosCategoria(8, "Pikachu")
    dao.salvar_com_pk(dados)

    pk: CategoriaPK = CategoriaPK(8)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido == dados

@db.transacted
def test_salvar_categoria_com_pk_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    dados: DadosCategoria = DadosCategoria(666, "Pikachu")
    dao.salvar_com_pk(dados) # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: CategoriaPK = CategoriaPK(666)
    lido: DadosCategoria | None = dao.buscar_por_pk(pk)
    assert lido is None

# TODO:
# Testar listar_por_segredo