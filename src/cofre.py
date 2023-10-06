from cofre_de_senhas.controller import servir
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
from cofre_de_senhas.categoria.categoria_dao_impl import CategoriaDAOImpl
from cofre_de_senhas.usuario.usuario_dao_impl import UsuarioDAOImpl
from cofre_de_senhas.segredo.segredo_dao_impl import SegredoDAOImpl

if __name__ == "__main__":
    cofre: Raiz = Raiz("cofre.bd")
    CategoriaDAOImpl(cofre.instance)
    CofreDeSenhasDAOImpl(cofre.instance)
    SegredoDAOImpl(cofre.instance)
    UsuarioDAOImpl(cofre.instance)
    servir()