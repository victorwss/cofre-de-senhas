from typing import override
from connection.trans import TransactedConnection
from ..dao import CofreDeSenhasDAO


class CofreDeSenhasDAOImpl(CofreDeSenhasDAO):

    def __init__(self, conn: TransactedConnection) -> None:
        super().__init__(conn)

    def __sql_criar_bd(self) -> str:
        n: str = self._connection.database_type.lower()
        with open(f"src/{n}-create.sql", "r", encoding = "utf-8") as f:
            return f.read().replace("$$$$", self._connection.database_name)

    @override
    def criar_bd(self) -> None:
        sql: str = self.__sql_criar_bd()
        self._executar_sql(sql)
