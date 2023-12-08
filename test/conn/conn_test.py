import sqlite3
from typing import Any, Callable, cast, Sequence, TYPE_CHECKING
from connection.conn import RAW_DATA, IntegrityViolationException, TransactionNotActiveException, UnsupportedOperationError
from connection.trans import TransactedConnection
from pytest import raises
from dataclasses import dataclass
from validator import dataclass_validate
from ..db_test_util import applier, applier_trans, applier_trans2, DbTestConfig, SqliteTestConfig, MariaDbTestConfig, MysqlTestConfig

sqlite_create: str = """
DROP TABLE IF EXISTS animal;
DROP TABLE IF EXISTS juice_2;
DROP TABLE IF EXISTS juice_1;
DROP TABLE IF EXISTS fruit;

CREATE TABLE fruit (
    pk_fruit        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;

INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');

CREATE TABLE juice_1 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT;

CREATE TABLE juice_2 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE RESTRICT ON UPDATE RESTRICT
) STRICT;

CREATE TABLE animal (
    pk_animal INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 2 AND LENGTH(name) <= 50),
    gender    TEXT    NOT NULL             CHECK (gender = 'M' OR gender = 'F' OR gender = '-'),
    species   TEXT    NOT NULL             CHECK (LENGTH(species) >= 4 AND LENGTH(species) <= 50),
    age       INTEGER NOT NULL
) STRICT;

INSERT INTO animal (name, gender, species, age) VALUES ('mimosa'   , 'F', 'bos taurus'      , 4);
INSERT INTO animal (name, gender, species, age) VALUES ('rex'      , 'M', 'canis familiaris', 6);
INSERT INTO animal (name, gender, species, age) VALUES ('sylvester', 'M', 'felis catus'     , 8);
"""

mysql_reset: str = """
DROP DATABASE IF EXISTS test_fruits;
CREATE DATABASE test_fruits /*!40100 COLLATE 'utf8mb4_general_ci' */;
USE test_fruits;

CREATE TABLE fruit (
    pk_fruit   INTEGER     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT name_min_size CHECK (LENGTH(name) >= 4)
) ENGINE = INNODB;

INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');

CREATE TABLE juice_1 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    CONSTRAINT FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = INNODB;

CREATE TABLE juice_2 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    CONSTRAINT FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE animal (
    pk_animal INTEGER     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(50) NOT NULL                UNIQUE,
    gender    CHAR(1)     NOT NULL,
    species   VARCHAR(50) NOT NULL,
    age       INTEGER     NOT NULL,
    CONSTRAINT name_min_size CHECK (LENGTH(name) >= 2),
    CONSTRAINT gener_domain  CHECK (gender = 'M' OR gender = 'F' OR gender = '-'),
    CONSTRAINT species_size  CHECK (LENGTH(species) >= 4)
) ENGINE = INNODB;

INSERT INTO animal (name, gender, species, age) VALUES ('mimosa'   , 'F', 'bos taurus'      , 4);
INSERT INTO animal (name, gender, species, age) VALUES ('rex'      , 'M', 'canis familiaris', 6);
INSERT INTO animal (name, gender, species, age) VALUES ('sylvester', 'M', 'felis catus'     , 8);
"""

sqlite_db : SqliteTestConfig  = SqliteTestConfig ("test/fruits-ok.db", "test/fruits.db")
mysql_db  : MysqlTestConfig   = MysqlTestConfig  (mysql_reset, "root", "root", "db_hostname", 3306, "test_fruits")
mariadb_db: MariaDbTestConfig = MariaDbTestConfig(mysql_reset, "root", "root", "db_hostname", 3306, "test_fruits", 3)

dbs: dict[str, DbTestConfig] = { \
    "sqlite" : sqlite_db , \
    "mysql"  : mysql_db  , \
    "mariadb": mariadb_db  \
}

run_on_dbs: list[DbTestConfig] = []

@dataclass_validate
@dataclass(frozen = True)
class Fruit:
    pk_fruit: int
    name: str

def foo(d: dict[str, RAW_DATA]) -> Fruit:
    return Fruit(cast(int, d["pk_fruit"]) *  10, "x_" + cast(str, d["name"]))

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
        assert all == [ \
            (1, "mimosa"   , "F", "bos taurus"      ,  4), \
            (2, "rex"      , "M", "canis familiaris",  6), \
            (3, "sylvester", "M", "felis catus"     ,  8), \
            (4, "bozo"     , "M", "bos taurus"      , 65)  \
        ]

@applier(dbs, assert_db_ok)
def test_executemany(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        data: list[list[RAW_DATA]] = [ \
            ["bozo"     , "M", "bos taurus"    , 65], \
            ["1000xeks" , "F", "bos taurus"    , 42], \
            ["sheik edu", "M", "musa acuminata", 36]  \
        ]
        q: str = c.placeholder
        c.executemany(f"INSERT INTO animal (name, gender, species, age) VALUES ({q}, {q}, {q}, {q})", data)
        assert c.rowcount == 3

    with conn as c:
        c.execute("SELECT pk_animal, name, gender, species, age FROM animal ORDER BY pk_animal")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [ \
            (1, "mimosa"   , "F", "bos taurus"      ,  4), \
            (2, "rex"      , "M", "canis familiaris",  6), \
            (3, "sylvester", "M", "felis catus"     ,  8), \
            (4, "bozo"     , "M", "bos taurus"      , 65), \
            (5, "1000xeks" , "F", "bos taurus"      , 42), \
            (6, "sheik edu", "M", "musa acuminata"  , 36)  \
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
        assert all == [ \
            (1, "acacia"), \
            (2, "ginkgo")  \
        ]

@applier(dbs, assert_db_ok)
def test_implicit_commit(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@applier(dbs, assert_db_ok)
def test_explicit_rollback(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.rollback()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@applier(dbs, assert_db_ok)
def test_implicit_rollback(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    class TestException(BaseException):
        pass

    with raises(TestException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('grape')")
            raise TestException()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@applier(dbs, assert_db_ok)
def test_transact_1(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    conn.transact(x)()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@applier(dbs, assert_db_ok)
def test_transact_2(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    @conn.transact
    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    x()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@applier(dbs, assert_db_ok)
def test_transact_rollback(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    @conn.transact
    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    with raises(IntegrityViolationException):
        x()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit ORDER BY pk_fruit")
        all: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@applier(dbs, assert_db_ok)
def test_no_transaction(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(TransactionNotActiveException):
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

@applier(dbs, assert_db_ok)
def test_check_constraint_1(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('abc')")

@applier(dbs, assert_db_ok)
def test_check_constraint_2(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('123456789012345678901234567890123456789012345678901')")

@applier(dbs, assert_db_ok)
def test_foreign_key_constraint_on_orphan_insert(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (666)")

@applier(dbs, assert_db_ok)
def test_foreign_key_constraint_on_update_cascade(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (1)")

    with conn as c:
        c.execute("UPDATE fruit SET pk_fruit = 777 WHERE pk_fruit = 1")

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_1 ORDER BY pk_fruit")
        t: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert t == [(777, )]

@applier(dbs, assert_db_ok)
def test_foreign_key_constraint_on_delete_cascade(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (1)")

    with conn as c:
        c.execute("DELETE FROM fruit WHERE pk_fruit = 1")

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_1 WHERE pk_fruit = 1")
        t: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert t == []

@applier(dbs, assert_db_ok)
def test_foreign_key_constraint_on_update_restrict(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_2 (pk_fruit) VALUES (1)")

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("UPDATE fruit SET pk_fruit = 777 WHERE pk_fruit = 1")

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_2")
        t: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert t == [(1, )]

@applier(dbs, assert_db_ok)
def test_foreign_key_constraint_on_delete_restrict(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_2 (pk_fruit) VALUES (1)")

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("DELETE FROM fruit WHERE pk_fruit = 1")

    with conn as c:
        c.execute("SELECT a.pk_fruit FROM juice_2 a INNER JOIN fruit b ON a.pk_fruit = b.pk_fruit WHERE a.pk_fruit = 1")
        t: Sequence[tuple[RAW_DATA, ...]] = c.fetchall()
        assert t == [(1, )]

@applier_trans2(dbs, assert_db_ok)
def test_lastrowid(c: TransactedConnection, db: DbTestConfig) -> None:
    assert c.lastrowid == 0 if db == sqlite_db else c.lastrowid is None
    c.execute("INSERT INTO fruit (name) VALUES ('melon')")
    assert c.lastrowid == 4
    assert c.asserted_lastrowid == 4

@applier_trans2(dbs, assert_db_ok)
def test_lastrowid_none(c: TransactedConnection, db: DbTestConfig) -> None:
    assert c.lastrowid == 0 if db == sqlite_db else c.lastrowid is None
    c.execute("SELECT pk_fruit FROM fruit WHERE pk_fruit = -1")
    t: tuple[RAW_DATA, ...] | None = c.fetchone()
    assert t is None
    assert c.lastrowid == 0 if db == sqlite_db else c.lastrowid is None

@applier_trans(dbs, assert_db_ok)
def test_raw(c: TransactedConnection) -> None:
    rco: str = c.raw_connection.__class__.__name__
    rcu: str = c.raw_cursor.__class__.__name__
    assert "Connection" in rco
    assert "Cursor" in rcu

@applier(dbs, assert_db_ok)
def test_transaction_nesting_counting(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    assert conn.reenter_count == 0
    assert not conn.is_active
    with conn as c1:
        assert c1.reenter_count == 1
        assert c1.is_active
        assert c1 is conn
        with conn as c2:
            assert c2.reenter_count == 2
            assert c2.is_active
            assert c2 is conn
        assert c1.reenter_count == 1
        assert c1.is_active
    assert conn.reenter_count == 0
    assert not conn.is_active

@applier(dbs, assert_db_ok)
def test_transaction_nesting_inheritance(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c1:
        with conn as c2:
            c2.execute("INSERT INTO fruit (name) VALUES ('melon')")
        c1.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 4")
        t: tuple[RAW_DATA, ...] | None = c1.fetchone()
        assert t == (4, "melon")

@applier(dbs, assert_db_ok)
def test_autocommit(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn
    assert not conn.autocommit
    with conn as c:
        assert not conn.wrapped.autocommit
        assert conn.raw_connection.autocommit in [False, -1]         # type: ignore
        assert conn.wrapped.raw_connection.autocommit in [False, -1] # type: ignore

@applier(dbs, assert_db_ok)
def test_placeholder(db: DbTestConfig) -> None:
    x: str = db.conn.placeholder
    y: str
    z: str
    with db.conn as c:
        y = db.conn.placeholder
        z = db.conn.wrapped.placeholder
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
        y = db.conn.database_type
        z = db.conn.wrapped.database_type
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
        y = db.conn.database_name
        z = db.conn.wrapped.database_name
    k: str = db.database_name
    assert x == k
    assert x == y
    assert x == z
