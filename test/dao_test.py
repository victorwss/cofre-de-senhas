from .db_test_util import DbTestConfig

db: DbTestConfig = DbTestConfig("test/cofre-teste.db", "test/cofre-teste-run.db")

@db.decorator
def test_instanciar() -> None:
    from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
    from cofre_de_senhas.categoria.categoria_dao_impl import CategoriaDAOImpl
    from cofre_de_senhas.segredo.segredo_dao_impl import SegredoDAOImpl
    from cofre_de_senhas.usuario.usuario_dao_impl import UsuarioDAOImpl

    CofreDeSenhasDAOImpl()
    CategoriaDAOImpl()
    SegredoDAOImpl()
    UsuarioDAOImpl()