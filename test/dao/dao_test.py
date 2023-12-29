from ..db_test_util import applier, DbTestConfig
from .fixtures import (
    dbs, dbs_x, mariadb_db_x, assert_db_ok, read_all,
    todas_categorias, todos_usuarios, todos_segredos
)
from cofre_de_senhas.dao import DadosUsuario, DadosCategoria, DadosSegredo


@applier(dbs, assert_db_ok)
def test_instanciar(db: DbTestConfig) -> None:
    from cofre_de_senhas.dao import CofreDeSenhasDAO
    from cofre_de_senhas.bd.bd_dao_impl import CofreDeSenhasDAOImpl
    f: CofreDeSenhasDAO = CofreDeSenhasDAOImpl(db.conn)
    assert f == CofreDeSenhasDAO.instance()


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
