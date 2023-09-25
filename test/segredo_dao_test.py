from .fixtures import *
from connection.conn import IntegrityViolationException
from cofre_de_senhas.dao import \
    BuscaPermissaoPorLogin, SegredoDAO, SegredoPK, DadosSegredo, DadosSegredoSemPK, CampoDeSegredo, PermissaoDeSegredo, \
    DadosCategoria, CategoriaDAO, CategoriaDeSegredo
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.categoria.categoria_dao_impl import CategoriaDAOImpl
from cofre_de_senhas.segredo.segredo_dao_impl import SegredoDAOImpl
from pytest import raises

@db.decorator
def test_instanciar() -> None:
    s: SegredoDAO = SegredoDAOImpl()
    assert s == SegredoDAO.instance()

@db.transacted
def test_criar_segredo() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    dados: DadosSegredoSemPK = star_trek_sem_pk
    pk: SegredoPK = dao.criar(dados)
    assert pk.pk_segredo == star_trek.pk_segredo

@db.transacted
def test_ler_segredo_por_pk() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk: SegredoPK = SegredoPK(3)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido == star_wars

@db.transacted
def test_criar_e_ler_segredo() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    dados: DadosSegredoSemPK = star_trek_sem_pk
    pk: SegredoPK = dao.criar(dados)
    assert pk.pk_segredo == star_trek.pk_segredo

    lido1: DadosSegredo | None = dao.buscar_por_pk(pk)

    assert lido1 == star_trek
    assert lido1 is not star_trek

@db.transacted
def test_ler_segredo_por_pk_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    lido: DadosSegredo | None = dao.buscar_por_pk(SegredoPK(666))
    assert lido is None

@db.transacted
def test_listar_segredos_por_pk() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk1: SegredoPK = SegredoPK(lotr.pk_segredo)
    pk2: SegredoPK = SegredoPK(star_wars.pk_segredo)
    lido: list[DadosSegredo] = dao.listar_por_pks([pk1, pk2])
    assert lido == parte_segredos

@db.transacted
def test_listar_segredos_por_pk_nao_existem() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk1: SegredoPK = SegredoPK(lixo1)
    pk2: SegredoPK = SegredoPK(lixo2)
    pk3: SegredoPK = SegredoPK(lixo3)
    lido: list[DadosSegredo] = dao.listar_por_pks([pk1, pk2, pk3])
    assert lido == []

@db.transacted
def test_listar_segredos_por_pk_alguns_existem() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk1: SegredoPK = SegredoPK(lixo3)
    pk2: SegredoPK = SegredoPK(lotr.pk_segredo)
    pk3: SegredoPK = SegredoPK(lixo1)
    pk4: SegredoPK = SegredoPK(star_wars.pk_segredo)
    pk5: SegredoPK = SegredoPK(lixo2)
    lido: list[DadosSegredo] = dao.listar_por_pks([pk1, pk2, pk3, pk4, pk5])
    assert lido == parte_segredos

@db.transacted
def test_listar_tudo() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    lido: list[DadosSegredo] = dao.listar()
    assert lido == todos_segredos

@db.transacted
def test_listar_tudo_apos_insercao() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    dados: DadosSegredoSemPK = star_trek_sem_pk
    pk: SegredoPK = dao.criar(dados)
    assert pk.pk_segredo == star_trek.pk_segredo
    lido: list[DadosSegredo] = dao.listar()
    esperado: list[DadosSegredo] = todos_segredos[:]
    esperado.append(star_trek)
    assert lido == esperado

@db.transacted
def test_listar_segredos_visiveis_1() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    lido: list[DadosSegredo] = dao.listar_visiveis(login_harry_potter)
    assert lido == todos_segredos

@db.transacted
def test_listar_segredos_visiveis_2() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    lido: list[DadosSegredo] = dao.listar_visiveis(login_voldemort)
    assert lido == visiv_segredos

@db.transacted
def test_listar_segredos_visiveis_3() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    lido: list[DadosSegredo] = dao.listar_visiveis(login_dumbledore) # Dumbledore é chaveiro, mas não é responsabilidade do DAO verificar isso.
    assert lido == visiv_segredos

@db.transacted
def test_listar_segredos_visiveis_4() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    lido: list[DadosSegredo] = dao.listar_visiveis(login_hermione)
    assert lido == visiv_segredos

@db.transacted
def test_listar_segredos_visiveis_5() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    lido: list[DadosSegredo] = dao.listar_visiveis(login_snape)
    assert lido == visiv_segredos

@db.transacted
def test_excluir_segredo_por_pk() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk: SegredoPK = SegredoPK(dbz.pk_segredo)
    lido1: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido1 == dbz
    dao.deletar_por_pk(pk)
    lido2: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido2 is None

@db.transacted
def test_excluir_segredo_por_pk_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk: SegredoPK = SegredoPK(lixo2)
    dao.deletar_por_pk(pk)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_salvar_segredo_com_pk() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    dados: DadosSegredo = DadosSegredo(dbz.pk_segredo, "Pokémon", "Segredos da Equipe Rocket", 1)
    dao.salvar_com_pk(dados) # Transforma Dragon Ball Z em Pokémon.

    pk: SegredoPK = SegredoPK(dbz.pk_segredo)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido == dados

@db.transacted
def test_salvar_segredo_com_pk_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    dados: DadosSegredo = DadosSegredo(lixo3, "Pokémon", "Segredos da Equipe Rocket", 1)
    dao.salvar_com_pk(dados) # Não é responsabilidade do DAO saber se isso existe ou não, ele apenas roda o UPDATE.

    pk: SegredoPK = SegredoPK(lixo3)
    lido: DadosSegredo | None = dao.buscar_por_pk(pk)
    assert lido is None

@db.transacted
def test_ler_campos_segredo() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == [
        CampoDeSegredo(star_wars.pk_segredo, "Nome do cara vestido de preto", "Darth Vader"), \
        CampoDeSegredo(star_wars.pk_segredo, "Nome do imperador", "Palpatine"), \
        CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "C3PO") \
    ]

@db.transacted
def test_ler_campos_segredo_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    pk: SegredoPK = SegredoPK(lixo1)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == []

@db.transacted
def test_criar_campo_segredo() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    campo: CampoDeSegredo = CampoDeSegredo(star_wars.pk_segredo, "Pequeno, mas poderoso", "Yoda")
    dao.criar_campo_segredo(campo)
    pk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == [
        CampoDeSegredo(star_wars.pk_segredo, "Nome do cara vestido de preto", "Darth Vader"), \
        CampoDeSegredo(star_wars.pk_segredo, "Nome do imperador", "Palpatine"), \
        CampoDeSegredo(star_wars.pk_segredo, "Pequeno, mas poderoso", "Yoda"), \
        CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "C3PO") \
    ]

@db.transacted
def test_criar_campo_segredo_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    campo: CampoDeSegredo = CampoDeSegredo(lixo1, "Patati", "Patatá")

    with raises(IntegrityViolationException):
        dao.criar_campo_segredo(campo)

    pk: SegredoPK = SegredoPK(lixo1)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == []

@db.transacted
def test_criar_campo_segredo_duplicado() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    campo: CampoDeSegredo = CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "R2D2")

    with raises(IntegrityViolationException):
        dao.criar_campo_segredo(campo)

    pk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    campos: list[CampoDeSegredo] = dao.ler_campos_segredo(pk)
    assert campos == [
        CampoDeSegredo(star_wars.pk_segredo, "Nome do cara vestido de preto", "Darth Vader"), \
        CampoDeSegredo(star_wars.pk_segredo, "Nome do imperador", "Palpatine"), \
        CampoDeSegredo(star_wars.pk_segredo, "Robô chato e falastrão", "C3PO") \
    ]

@db.transacted
def test_criar_permissao() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(hermione.pk_usuario, dbz.pk_segredo, 2)
    dao.criar_permissao(perm1)

    lido: list[DadosSegredo] = dao.listar_visiveis(login_hermione)
    assert lido == todos_segredos

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(dbz.pk_segredo, "Hermione")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm1 == perm2

@db.transacted
def test_criar_permissao_usuario_nao_existe() -> None:
    dao1: SegredoDAOImpl = SegredoDAOImpl()
    perm: PermissaoDeSegredo = PermissaoDeSegredo(lixo1, dbz.pk_segredo, 2)

    with raises(IntegrityViolationException):
        dao1.criar_permissao(perm)

    #lido: list[DadosSegredo] = dao1.listar_visiveis(lixo1)
    #assert lido == []

@db.transacted
def test_criar_permissao_segredo_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(hermione.pk_usuario, lixo1, 2)

    with raises(IntegrityViolationException):
        dao.criar_permissao(perm1)

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lixo1, "Hermione")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm2 is None

@db.transacted
def test_criar_permissao_tipo_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(hermione.pk_usuario, dbz.pk_segredo, lixo1)

    with raises(IntegrityViolationException):
        dao.criar_permissao(perm1)

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(dbz.pk_segredo, "Hermione")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm2 is None

@db.transacted
def test_criar_permissao_ja_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    perm1: PermissaoDeSegredo = PermissaoDeSegredo(harry_potter.pk_usuario, dbz.pk_segredo, 3)

    with raises(IntegrityViolationException):
        dao.criar_permissao(perm1)

    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(dbz.pk_segredo, "Harry Potter")
    perm2: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm2 == PermissaoDeSegredo(harry_potter.pk_usuario, dbz.pk_segredo, 1)

@db.transacted
def test_buscar_permissao_1() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(dbz.pk_segredo, "Harry Potter")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm == PermissaoDeSegredo(harry_potter.pk_usuario, dbz.pk_segredo, 1)

@db.transacted
def test_buscar_permissao_2() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lotr.pk_segredo, "Harry Potter")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm == PermissaoDeSegredo(harry_potter.pk_usuario, lotr.pk_segredo, 2)

@db.transacted
def test_buscar_permissao_nao_tem() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lotr.pk_segredo, "Hermione")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm is None

@db.transacted
def test_buscar_permissao_login_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lotr.pk_segredo, "Dollynho")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm is None

@db.transacted
def test_buscar_permissao_segredo_nao_existe() -> None:
    dao: SegredoDAOImpl = SegredoDAOImpl()
    busca: BuscaPermissaoPorLogin = BuscaPermissaoPorLogin(lixo1, "Harry Potter")
    perm: PermissaoDeSegredo | None = dao.buscar_permissao(busca)
    assert perm is None

@db.transacted
def test_criar_categoria_segredo() -> None:
    dao1: SegredoDAOImpl = SegredoDAOImpl()
    cs: CategoriaDeSegredo = CategoriaDeSegredo(star_wars.pk_segredo, qa.pk_categoria)
    dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAOImpl = CategoriaDAOImpl()
    spk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == [producao, qa]

@db.transacted
def test_criar_categoria_segredo_com_segredo_que_nao_existe() -> None:
    dao1: SegredoDAOImpl = SegredoDAOImpl()
    cs: CategoriaDeSegredo = CategoriaDeSegredo(lixo1, qa.pk_categoria)

    with raises(IntegrityViolationException):
        dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAOImpl = CategoriaDAOImpl()
    spk: SegredoPK = SegredoPK(lixo1)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == []

@db.transacted
def test_criar_categoria_segredo_com_categoria_que_nao_existe() -> None:
    dao1: SegredoDAOImpl = SegredoDAOImpl()
    cs: CategoriaDeSegredo = CategoriaDeSegredo(star_wars.pk_segredo, lixo3)

    with raises(IntegrityViolationException):
        dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAOImpl = CategoriaDAOImpl()
    spk: SegredoPK = SegredoPK(star_wars.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == [producao]

@db.transacted
def test_criar_categoria_segredo_ja_existe() -> None:
    dao1: SegredoDAOImpl = SegredoDAOImpl()
    cs: CategoriaDeSegredo = CategoriaDeSegredo(dbz.pk_segredo, qa.pk_categoria)

    with raises(IntegrityViolationException):
        dao1.criar_categoria_segredo(cs)

    dao2: CategoriaDAOImpl = CategoriaDAOImpl()
    spk: SegredoPK = SegredoPK(dbz.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)

    assert dados == [qa]

@db.transacted
def test_buscar_categoria_segredo() -> None:
    dao2: CategoriaDAOImpl = CategoriaDAOImpl()
    spk: SegredoPK = SegredoPK(lotr.pk_segredo)
    dados: list[DadosCategoria] = dao2.listar_por_segredo(spk)
    assert dados == [aplicacao, integracao]

@db.transacted
def test_buscar_categoria_segredo_nao_existe() -> None:
    dao: CategoriaDAOImpl = CategoriaDAOImpl()
    spk: SegredoPK = SegredoPK(lixo1)
    dados: list[DadosCategoria] = dao.listar_por_segredo(spk)
    assert dados == []

#@db.transacted
#def test_criar_listar_por_permissao() -> None:
#    pk: SegredoPk = SegredoPK(dbz.pk_segredo)
#    dao: UsuarioDAOImpl = UsuarioDAOImpl()
#    permissoes: list[DadosUsuarioComPermissao] = dao.listar_por_permissao(pk)
#    assert permissoes = [
#        DadosUsuarioComPermissao(harry_potter.pk_usuario, harry_potter.login, harry_potter.fk_nivel_acesso, harry_potter)
#    ]