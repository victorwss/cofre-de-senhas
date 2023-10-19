from typing import override
from cofre_de_senhas.service import LoginComSenha, GerenciadorLogin, UsuarioComChave, ChaveUsuario
from cofre_de_senhas.service_impl import Servicos
from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
from connection.sqlite3conn import connect
from connection.trans import TransactedConnection

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

    Servicos(_Nao(), cofre).bd.criar_bd(LoginComSenha(login1, senha1))

cofre: TransactedConnection = connect("cofre.db")
CofreDeSenhasDAOImpl(cofre)
_criar_bd()