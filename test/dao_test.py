from .db_test_util import DbTestConfig

db: DbTestConfig = DbTestConfig("test/cofre-teste.db", "test/cofre-teste-run.db")

@db.decorator
def test_instanciar() -> None:
    from cofre_de_senhas.dao import CofreDeSenhasDAO
    from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
    f: CofreDeSenhasDAO = CofreDeSenhasDAOImpl()
    assert f == CofreDeSenhasDAO.instance()