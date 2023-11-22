from typing import override
from connection.trans import TransactedConnection
from cofre_de_senhas.dao import CofreDeSenhasDAO

class CofreDeSenhasDAOImpl(CofreDeSenhasDAO):

    def __init__(self, conn: TransactedConnection) -> None:
        super().__init__(conn)

    def sql_criar_bd(self) -> str:
        n: str = self._connection.database_type.lower()
        with open(f"src/{n}-create.sql", "r", encoding = "utf-8") as f:
            return f.read().replace("$$$$", "cofre")

    @override
    def criar_bd(self) -> None:
        self._connection.executescript(self.sql_criar_bd())