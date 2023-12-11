from typing import override
from .service import LoginComSenha, GerenciadorLogin, UsuarioComChave, ChaveUsuario
from .service_impl import Servicos
from .bd.bd_dao_impl import CofreDeSenhasDAOImpl
from connection.trans import TransactedConnection
from .conn_factory import connect

class _Nao(GerenciadorLogin): #  pragma: no cover

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


def _criar_bd(cofre: TransactedConnection) -> None:

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


def admin() -> None:
    cofre: TransactedConnection = connect()
    CofreDeSenhasDAOImpl(cofre)
    _criar_bd(cofre)