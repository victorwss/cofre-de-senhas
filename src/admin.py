from cofre_de_senhas.service import LoginComSenha
from cofre_de_senhas.service_impl import ServicoBDImpl, ServicoUsuarioImpl
from cofre_de_senhas.bd.raiz import Raiz
from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl

def criar_bd() -> None:
    login1: str = input("Informe o login do usuário administrador : ")
    login2: str = input("Confirme o login do usuário administrador: ")

    if login1 != login2:
        print("Os logins não conferem")

    senha1 = input("Informe a senha do usuário administrador : ")
    senha2 = input("Confirme a senha do usuário administrador: ")

    if senha1 != senha2:
        print("As senhas não conferem")

    ServicoBDImpl().criar_bd(LoginComSenha(login1, senha1))

Raiz.register_sqlite("cofre.db")
CofreDeSenhasDAOImpl()
criar_bd()