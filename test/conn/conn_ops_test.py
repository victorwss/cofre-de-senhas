from typing import cast, Sequence
from connection.conn import RAW_DATA, MisplacedOperationError, UnsupportedOperationError
from connection.trans import TransactedConnection
from pytest import raises
from dataclasses import dataclass
from validator import dataclass_validate
from ..db_test_util import applier, applier_trans, applier_trans2, DbTestConfig
from ..dao.fixtures import dbs_f as dbs, sqlite_db_f as sqlite_db, mysql_db_f as mysql_db, mariadb_db_f as mariadb_db


run_on_dbs: list[DbTestConfig] = []


@dataclass_validate
@dataclass(frozen = True)
class Fruit:
    pk_fruit: int
    name: str


def foo(d: dict[str, RAW_DATA]) -> Fruit:
    return Fruit(cast(int, d["pk_fruit"]) * 10, "x_" + cast(str, d["name"]))


def boo(d: dict[str, RAW_DATA]) -> Fruit:
    return Fruit(cast(int, d["pk_fruit"]) * 100, "y_" + cast(str, d["name"]))


def noo(d: dict[str, RAW_DATA]) -> Fruit:
    assert False


@applier(dbs)
def test_dbs(db: DbTestConfig) -> None:
    run_on_dbs.append(db)


def test_run_oks() -> None:
    assert run_on_dbs == [sqlite_db, mysql_db, mariadb_db]


def assert_db_ok(db: DbTestConfig) -> None:
    assert db in run_on_dbs, "Database connector failed to load."


@applier_trans(dbs, assert_db_ok)
def test_fetchone(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
    one: tuple[RAW_DATA, ...] | None = c.fetchone()
    assert one == (2, "strawberry")


@applier_trans(dbs, assert_db_ok)
def test_fetchone_none(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = -2")
    one: tuple[RAW_DATA, ...] | None = c.fetchone()
    assert one is None


@applier_trans(dbs, assert_db_ok)
def test_fetchall(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
    assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]


@applier_trans(dbs, assert_db_ok)
def test_iter(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    all: list[tuple[RAW_DATA, ...]] = [x for x in c]
    assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]


@applier_trans(dbs, assert_db_ok)
def test_fetchmany(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    p1: Sequence[tuple[RAW_DATA, ...]] = c.fetchmany(2)
    assert p1 == [(1, "orange"), (2, "strawberry")]
    p2: Sequence[tuple[RAW_DATA, ...]] = c.fetchmany(2)
    assert p2 == [(3, "lemon")]
    p3: Sequence[tuple[RAW_DATA, ...]] = c.fetchmany(2)
    assert p3 == []


@applier_trans(dbs, assert_db_ok)
def test_fetchone_dict(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
    one: dict[str, RAW_DATA] | None = c.fetchone_dict()
    assert one == {"pk_fruit": 2, "name": "strawberry"}


@applier_trans(dbs, assert_db_ok)
def test_fetchone_dict_none(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = -2")
    one: dict[str, RAW_DATA] | None = c.fetchone_dict()
    assert one is None


@applier_trans(dbs, assert_db_ok)
def test_fetchall_dict(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    all: Sequence[dict[str, RAW_DATA]] = c.fetchall_dict()
    assert all == [{"pk_fruit": 1, "name": "orange"}, {"pk_fruit": 2, "name": "strawberry"}, {"pk_fruit": 3, "name": "lemon"}]


@applier_trans(dbs, assert_db_ok)
def test_fetchmany_dict(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    p1: Sequence[dict[str, RAW_DATA]] = c.fetchmany_dict(2)
    assert p1 == [{"pk_fruit": 1, "name": "orange"}, {"pk_fruit": 2, "name": "strawberry"}]
    p2: Sequence[dict[str, RAW_DATA]] = c.fetchmany_dict(2)
    assert p2 == [{"pk_fruit": 3, "name": "lemon"}]
    p3: Sequence[dict[str, RAW_DATA]] = c.fetchmany_dict(2)
    assert p3 == []


@applier_trans(dbs, assert_db_ok)
def test_fetchone_class(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
    one: Fruit | None = c.fetchone_class(Fruit)
    assert one == Fruit(2, "strawberry")


@applier_trans(dbs, assert_db_ok)
def test_fetchone_class_none(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = -2")
    one: Fruit | None = c.fetchone_class(Fruit)
    assert one is None


@applier_trans(dbs, assert_db_ok)
def test_fetchall_class(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    all: Sequence[Fruit] = c.fetchall_class(Fruit)
    assert all == [Fruit(1, "orange"), Fruit(2, "strawberry"), Fruit(3, "lemon")]


@applier_trans(dbs, assert_db_ok)
def test_fetchmany_class(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    p1: Sequence[Fruit] = c.fetchmany_class(Fruit, 2)
    assert p1 == [Fruit(1, "orange"), Fruit(2, "strawberry")]
    p2: Sequence[Fruit] = c.fetchmany_class(Fruit, 2)
    assert p2 == [Fruit(3, "lemon")]
    p3: Sequence[Fruit] = c.fetchmany_class(Fruit, 2)
    assert p3 == []


@applier_trans(dbs, assert_db_ok)
def test_fetchone_class_lambda(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
    one: Fruit | None = c.fetchone_class_lambda(foo)
    assert one == Fruit(20, "x_strawberry")


@applier_trans(dbs, assert_db_ok)
def test_fetchone_class_lambda_none(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = -2")
    one: Fruit | None = c.fetchone_class_lambda(noo)
    assert one is None


@applier_trans(dbs, assert_db_ok)
def test_fetchall_class_lambda(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    all: Sequence[Fruit] = c.fetchall_class_lambda(foo)
    assert all == [Fruit(10, "x_orange"), Fruit(20, "x_strawberry"), Fruit(30, "x_lemon")]


@applier_trans(dbs, assert_db_ok)
def test_fetchmany_class_lambda(c: TransactedConnection) -> None:
    c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
    p1: Sequence[Fruit] = c.fetchmany_class_lambda(foo, 2)
    assert p1 == [Fruit(10, "x_orange"), Fruit(20, "x_strawberry")]
    p2: Sequence[Fruit] = c.fetchmany_class_lambda(boo, 2)
    assert p2 == [Fruit(300, "y_lemon")]
    p3: Sequence[Fruit] = c.fetchmany_class_lambda(noo, 2)
    assert p3 == []


@applier(dbs, assert_db_ok)
def test_execute_insert(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        q: str = c.placeholder
        c.execute(f"INSERT INTO animal (name, gender, species, age) VALUES ({q}, {q}, {q}, {q})", ["bozo", "M", "bos taurus", 65])
        assert c.rowcount == 1

    with conn as c:
        c.execute("SELECT pk_animal, name, gender, species, age FROM animal ORDER BY pk_animal")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [                                     # noqa: E203,E241
            (1, "mimosa"   , "F", "bos taurus"      ,  4),  # noqa: E203,E241
            (2, "rex"      , "M", "canis familiaris",  6),  # noqa: E203,E241
            (3, "sylvester", "M", "felis catus"     ,  8),  # noqa: E203,E241
            (4, "bozo"     , "M", "bos taurus"      , 65)   # noqa: E203,E241
        ]


@applier(dbs, assert_db_ok)
def test_executemany(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        data: list[list[RAW_DATA]] = [
            ["bozo"     , "M", "bos taurus"    , 65],  # noqa: E203,E241
            ["1000xeks" , "F", "bos taurus"    , 42],  # noqa: E203,E241
            ["sheik edu", "M", "musa acuminata", 36]   # noqa: E203,E241
        ]
        q: str = c.placeholder
        c.executemany(f"INSERT INTO animal (name, gender, species, age) VALUES ({q}, {q}, {q}, {q})", data)
        assert c.rowcount == 3

    with conn as c:
        c.execute("SELECT pk_animal, name, gender, species, age FROM animal ORDER BY pk_animal")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [
            (1, "mimosa"   , "F", "bos taurus"      ,  4),  # noqa: E203,E241
            (2, "rex"      , "M", "canis familiaris",  6),  # noqa: E203,E241
            (3, "sylvester", "M", "felis catus"     ,  8),  # noqa: E203,E241
            (4, "bozo"     , "M", "bos taurus"      , 65),  # noqa: E203,E241
            (5, "1000xeks" , "F", "bos taurus"      , 42),  # noqa: E203,E241
            (6, "sheik edu", "M", "musa acuminata"  , 36)   # noqa: E203,E241
        ]


longscript_sqlite: str = """
CREATE TABLE tree (
    pk_tree INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;

INSERT INTO tree (name) VALUES ('acacia');
INSERT INTO tree (name) VALUES ('ginkgo');
"""

longscript_mysql: str = """
CREATE TABLE tree (
    pk_tree INTEGER     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT name_size  CHECK (LENGTH(name) >= 4)
) ENGINE = INNODB;

INSERT INTO tree (name) VALUES ('acacia');
INSERT INTO tree (name) VALUES ('ginkgo');
"""


@applier(dbs, assert_db_ok)
def test_executescript(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    if db == mariadb_db:
        with raises(UnsupportedOperationError):
            with conn as c:
                c.executescript(longscript_mysql)
        return

    script: str
    if db == sqlite_db:
        script = longscript_sqlite
    elif db == mysql_db:
        script = longscript_mysql
    else:
        assert False

    with conn as c:
        c.executescript(script)

    with conn as c:
        c.execute("SELECT pk_tree, name FROM tree ORDER BY pk_tree")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [
            (1, "acacia"),
            (2, "ginkgo")
        ]


@applier_trans2(dbs, assert_db_ok)
def test_rowcount_before(c: TransactedConnection, db: DbTestConfig) -> None:
    with raises(MisplacedOperationError, match = "^rowcount shouldn't be used before execute, executemany, executescript or callproc$"):
        c.rowcount


@applier_trans2(dbs, assert_db_ok)
def test_lastrowid_before(c: TransactedConnection, db: DbTestConfig) -> None:
    with raises(MisplacedOperationError, match = "^lastrowid shouldn't be used before execute, executemany, executescript or callproc$"):
        c.lastrowid


@applier_trans2(dbs, assert_db_ok)
def test_lastrowid(c: TransactedConnection, db: DbTestConfig) -> None:
    c.execute("INSERT INTO fruit (name) VALUES ('melon')")
    assert c.lastrowid == 4
    assert c.asserted_lastrowid == 4


@applier_trans2(dbs, assert_db_ok)
def test_lastrowid_none(c: TransactedConnection, db: DbTestConfig) -> None:
    c.execute("SELECT pk_fruit FROM fruit WHERE pk_fruit = -1")
    t: tuple[RAW_DATA, ...] | None = c.fetchone()
    assert t is None
    assert c.lastrowid == 0 if db == sqlite_db else c.lastrowid is None  # Sqlite is buggy and gives zero instead of None!


@applier_trans(dbs, assert_db_ok)
def test_raw(c: TransactedConnection) -> None:
    rco: str = c.raw_connection.__class__.__name__
    rcu: str = c.raw_cursor.__class__.__name__
    assert "Connection" in rco
    assert "Cursor" in rcu


@applier(dbs, assert_db_ok)
def test_placeholder(db: DbTestConfig) -> None:
    x: str = db.conn.placeholder
    y: str
    z: str
    with db.conn as c:
        y = c.placeholder
        z = c.wrapped.placeholder
    k: str = db.placeholder
    assert x == k
    assert x == y
    assert x == z


@applier(dbs, assert_db_ok)
def test_database_type(db: DbTestConfig) -> None:
    x: str = db.conn.database_type
    y: str
    z: str
    with db.conn as c:
        y = c.database_type
        z = c.wrapped.database_type
    k: str = db.database_type
    assert x == k
    assert x == y
    assert x == z


@applier(dbs, assert_db_ok)
def test_database_name(db: DbTestConfig) -> None:
    x: str = db.conn.database_name
    y: str
    z: str
    with db.conn as c:
        y = c.database_name
        z = c.wrapped.database_name
    k: str = db.database_name
    assert x == k
    assert x == y
    assert x == z


@applier(dbs, assert_db_ok)
def test_description(db: DbTestConfig) -> None:
    with db.conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        c.fetchone()
        f: Fruit = c.description.column_names.row_to_class(Fruit, (5, "watermelon"))
        assert f == Fruit(5, "watermelon")


@applier_trans(dbs, assert_db_ok)
def test_description_trans(c: TransactedConnection) -> None:
    with c as conn:
        conn.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        conn.fetchone()
        f: Fruit = conn.description.column_names.row_to_class(Fruit, (5, "watermelon"))
        assert f == Fruit(5, "watermelon")


@applier(dbs, assert_db_ok)
def test_description_nonfetched_1(db: DbTestConfig) -> None:
    with db.conn as c:
        with raises(MisplacedOperationError, match = "^description shouldn't be used before a fetcher method$"):
            c.description


# @applier(dbs, assert_db_ok)
# def test_description_nonfetched_2(db: DbTestConfig) -> None:
#     with db.conn as c:
#         c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
#         with raises(MisplacedOperationError, match = "^description shouldn't be used before a fetcher method$"):
#             c.description


@applier(dbs, assert_db_ok)
def test_column_names(db: DbTestConfig) -> None:
    with db.conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        c.fetchone()
        f: Fruit = c.column_names.row_to_class(Fruit, (5, "watermelon"))
        assert f == Fruit(5, "watermelon")


@applier_trans(dbs, assert_db_ok)
def test_column_names_trans(c: TransactedConnection) -> None:
    with c as conn:
        conn.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        conn.fetchone()
        f: Fruit = conn.column_names.row_to_class(Fruit, (5, "watermelon"))
        assert f == Fruit(5, "watermelon")
