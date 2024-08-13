from typing import override
from connection.trans import TransactedConnection
from ..dao import CofreDeSenhasDAO

if TYPE_CHECKING:
    from _typeshed import TextIOWrapper


class CofreDeSenhasDAOImpl(CofreDeSenhasDAO):

    def __init__(self, conn: TransactedConnection) -> None:
        super().__init__(conn)

    def __sql_criar_bd(self) -> str:
        n: str = self._connection.database_type.lower()
        f: TextIOWrapper
        with open(f"src/{n}-create.sql", "r", encoding = "utf-8") as f:
            return f.read()

    @override
    def criar_bd(self) -> None:
        sql: str = self.__sql_criar_bd()
        self._executar_sql(sql)

    @override
    @property
    def aplicacao_aberta(self) -> bool:
        sql: str = "SELECT pk_usuario, login, fk_nivel_acesso, hash_com_sal FROM usuario WHERE fk_nivel_acesso = 2"
        return self._connection.execute(sql).fetchone() is not None
