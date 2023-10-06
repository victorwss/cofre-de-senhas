from typing import override
from cofre_de_senhas.service import LoginComSenha, GerenciadorLogin, UsuarioComChave, ChaveUsuario
from cofre_de_senhas.service_impl import Servicos
from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
from cofre_de_senhas.bd.raiz import Raiz

class _Nao(GerenciadorLogin): # pragma: no cover

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert False

    @override
    def logout(self) -> None:
        assert False

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario:
        assert False

def _criar_bd() -> None:

    login1: str = input("Informe o login do usuário administrador : ")
    login2: str = input("Confirme o login do usuário administrador: ")

    if login1 != login2:
        print("Os logins não conferem")
        return

    senha1 = input("Informe a senha do usuário administrador : ")
    senha2 = input("Confirme a senha do usuário administrador: ")

    if senha1 != senha2:
        print("As senhas não conferem")
        return

    Servicos(_Nao(), cofre.instance).bd.criar_bd(LoginComSenha(login1, senha1))

cofre: Raiz = Raiz("cofre.bd")
CofreDeSenhasDAOImpl(cofre.instance)
_criar_bd()