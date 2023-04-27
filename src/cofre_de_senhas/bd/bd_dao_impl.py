from connection.conn import TransactedConnection
from cofre_de_senhas.dao import CofreDeSenhasDAO

class CofreDeSenhasDAOImpl(CofreDeSenhasDAO):

    def __init__(self, transacted_conn: TransactedConnection) -> None:
        self.__cf: TransactedConnection = transacted_conn

    def sql_criar_bd(self) -> str:
        with open("create.sql", "r") as f:
            return f.read()

    def criar_bd(self) -> None:
        self.__cf.executescript(self.sql_criar_bd())