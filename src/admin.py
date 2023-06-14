from cofre_de_senhas.service import LoginUsuario
from cofre_de_senhas.service_impl import ServicoBDImpl, ServicoUsuarioImpl

def criar_bd() -> None:
    login1: str = input("Informe o login do usuário administrador : ")
    login2: str = input("Confirme o login do usuário administrador: ")

    if login1 != login2:
        print("Os logins não conferem")

    senha1 = input("Informe a senha do usuário administrador : ")
    senha2 = input("Confirme a senha do usuário administrador: ")

    if senha1 != senha2:
        print("As senhas não conferem")

    ServicoBDImpl().criar_bd(LoginUsuario(login1, senha1))

criar_bd()