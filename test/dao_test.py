from cofre_de_senhas.bd.raiz import Raiz

def test_x1():
    Raiz.register_sqlite("test/cofre-teste.db")
    CategoriaDAOImpl()
    CofreDeSenhasDAOImpl()
    SegredoDAOImpl()
    UsuarioDAOImpl()
