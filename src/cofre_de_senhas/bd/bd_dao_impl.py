from typing import override
from cofre_de_senhas.dao import CofreDeSenhasDAO
from cofre_de_senhas.bd.raiz import Raiz

class CofreDeSenhasDAOImpl(CofreDeSenhasDAO):

    def __init__(self) -> None:
        CofreDeSenhasDAO.register(self)

    def sql_criar_bd(self) -> str:
        with open("src/create.sql", "r", encoding = "utf-8") as f:
            return f.read()

    @override
    def criar_bd(self) -> None:
        Raiz.instance().executescript(self.sql_criar_bd())