from .fixtures import *

@db.decorator
def test_instanciar() -> None:
    from cofre_de_senhas.dao import CofreDeSenhasDAO
    from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
    f: CofreDeSenhasDAO = CofreDeSenhasDAOImpl(db.raiz)
    assert f == CofreDeSenhasDAO.instance()