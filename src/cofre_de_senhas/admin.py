from typing import override, TypeAlias
from .service import Servicos, LoginComSenha, GerenciadorLogin, UsuarioComChave, ChaveUsuario
from .service_impl import ServicosImpl
from .erro import UsuarioJaExisteException, ValorIncorretoException
from .bd.bd_dao_impl import CofreDeSenhasDAOImpl
from connection.trans import TransactedConnection
from .conn_factory import connect
import getpass


_UJEE: TypeAlias = UsuarioJaExisteException
_VIE: TypeAlias = ValorIncorretoException


class _Nao(GerenciadorLogin):

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


class _Menu:

    def __init__(self, cofre: TransactedConnection) -> None:
        self.__cofre: TransactedConnection = cofre
        self.__servicos: Servicos = ServicosImpl(_Nao(), self.__cofre)

    def __mostrar_menu(self) -> None:
        print("Escolha uma das opções:")
        print("RESET - Criar ou recriar o banco de dados")
        print("ADMIN - Criar um usuário administrador")
        print("SAIR - Sair sem fazer nada")

        escolha: str = input("Informe a sua escolha: ").lower().strip()

        if escolha == "reset":
            self.__criar_bd()
        elif escolha == "admin":
            self.__criar_admin()
        elif escolha != "sair":
            print("Opção não reconhecida")

    def __criar_bd(self) -> None:
        self.__servicos.bd.criar_bd()

    def __criar_admin(self) -> None:

        login1: str = input("Informe  o login do usuário administrador: ")
        login2: str = input("Confirme o login do usuário administrador: ")

        if login1 != login2:
            print("Os logins não conferem")
            return

        senha1: str = getpass.getpass(prompt = "Informe  a senha do usuário administrador: ")
        senha2: str = getpass.getpass(prompt = "Confirme a senha do usuário administrador: ")

        if senha1 != senha2:
            print("As senhas não conferem.")
            return

        resultado: UsuarioComChave | _VIE | _UJEE = self.__servicos.bd.criar_admin(LoginComSenha(login1, senha1))
        if isinstance(resultado, UsuarioJaExisteException):
            print("Esse usuário já existe.")
        elif isinstance(resultado, ValorIncorretoException):
            print("Esse nome de usuário não é válido.")
        else:
            print(f"O usuário foi criado com a chave {resultado.chave.valor}.")

    @staticmethod
    def executar(cofre: TransactedConnection) -> None:
        _Menu(cofre).__mostrar_menu()


def admin() -> None:
    cofre: TransactedConnection = connect()
    CofreDeSenhasDAOImpl(cofre)
    _Menu.executar(cofre)
