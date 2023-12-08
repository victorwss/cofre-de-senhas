from typing import Sequence
from connection.conn import RAW_DATA
from connection.trans import TransactedConnection
from .fixtures import *
from cofre_de_senhas.dao import DadosUsuario, DadosCategoria, DadosSegredo

@applier(dbs, assert_db_ok)
def test_instanciar(db: DbTestConfig) -> None:
    from cofre_de_senhas.dao import CofreDeSenhasDAO
    from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
    f: CofreDeSenhasDAO = CofreDeSenhasDAOImpl(db.conn)
    assert f == CofreDeSenhasDAO.instance()

sqlite_db_x : SqliteTestConfig  = SqliteTestConfig ("test/empty.db", "test/cofre-teste-create-run.db")
mysql_db_x  : MysqlTestConfig   = MysqlTestConfig  ("", "root", "root", "mariadb", 3306, "test_cofre_empty")
mariadb_db_x: MariaDbTestConfig = MariaDbTestConfig("", "root", "root", "mariadb", 3306, "test_cofre_empty", 3)

dbs_x: dict[str, DbTestConfig] = { \
    "sqlite" : sqlite_db_x , \
    "mysql"  : mysql_db_x  , \
    "mariadb": mariadb_db_x  \
}

@applier(dbs_x)
def test_criar_bd(db: DbTestConfig) -> None:
    from cofre_de_senhas.dao import CofreDeSenhasDAO
    from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
    dao: CofreDeSenhasDAO = CofreDeSenhasDAOImpl(db.conn)

    with db.conn as c:
        dao.criar_bd()

    with db.conn as c:
        sql_extra: str = read_all("test/test-mass.sql")
        if db == mariadb_db_x:
            for part in sql_extra.split(";"):
                if part.strip() != "":
                    c.execute(part)
        else:
            c.executescript(sql_extra)

    with db.conn as c:
        c.execute("SELECT * FROM categoria ORDER BY pk_categoria")
        cc: list[DadosCategoria] = c.fetchall_class(DadosCategoria)
        assert cc == todas_categorias

        c.execute("SELECT * FROM usuario ORDER BY pk_usuario")
        uu: list[DadosUsuario] = c.fetchall_class(DadosUsuario)
        assert uu == todos_usuarios

        c.execute("SELECT * FROM segredo ORDER BY pk_segredo")
        ss: list[DadosSegredo] = c.fetchall_class(DadosSegredo)
        assert ss == todos_segredos
