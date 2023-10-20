import sqlite3
from typing import Any, Callable, Sequence
from connection.conn import IntegrityViolationException, TransactionNotActiveException
from connection.trans import TransactedConnection
from pytest import raises
from dataclasses import dataclass
from validator import dataclass_validate
from ..db_test_util import applier, DbTestConfig, SqliteTestConfig, MariaDbTestConfig, MysqlTestConfig

sqlite_create: str = """
DROP TABLE IF NOT EXISTS animal;
DROP TABLE IF NOT EXISTS juice_2;
DROP TABLE IF NOT EXISTS juice_1;
DROP TABLE IF NOT EXISTS fruit;

CREATE TABLE IF NOT EXISTS fruit (
    pk_fruit        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;

INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');

CREATE TABLE IF NOT EXISTS juice_1 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS juice_2 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE RESTRICT ON UPDATE RESTRICT
) STRICT;

CREATE TABLE IF NOT EXISTS animal (
    pk_animal       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 2 AND LENGTH(name) <= 50),
    gender          TEXT    NOT NULL             CHECK (gender = 'M' OR gender = 'F' OR gender = '-'),
    species         TEXT    NOT NULL             CHECK (LENGTH(species) >= 4 AND LENGTH(species) <= 50),
    age             INTEGER NOT NULL
) STRICT;

INSERT INTO animal (name, gender, species, age) VALUES ('mimosa'   , 'F', 'bos taurus'      , 4);
INSERT INTO animal (name, gender, species, age) VALUES ('rex'      , 'M', 'canis familiaris', 6);
INSERT INTO animal (name, gender, species, age) VALUES ('sylvester', 'M', 'felis catus'     , 8);
"""

sqlite_drop: str = """
DROP TABLE IF NOT EXISTS animal;
DROP TABLE IF NOT EXISTS juice_2;
DROP TABLE IF NOT EXISTS juice_1;
DROP TABLE IF NOT EXISTS fruit;
"""

mysql_create: str = """
DROP DATABASE IF EXISTS test_fruits;
CREATE DATABASE test_fruits /*!40100 COLLATE 'utf8mb4_general_ci' */;
USE test_fruits;

CREATE TABLE IF NOT EXISTS fruit (
    pk_fruit   INTEGER     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT name_min_size CHECK (LENGTH(name) >= 4)
) ENGINE = INNODB;

INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');

CREATE TABLE IF NOT EXISTS juice_1 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    CONSTRAINT FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS juice_2 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    CONSTRAINT FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS animal (
    pk_animal       INTEGER     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(50) NOT NULL                UNIQUE,
    gender          CHAR(1)     NOT NULL,
    species         VARCHAR(50) NOT NULL,
    age             INTEGER     NOT NULL,
    CONSTRAINT name_min_size CHECK (LENGTH(name) >= 2),
    CONSTRAINT gener_domain  CHECK (gender = 'M' OR gender = 'F' OR gender = '-'),
    CONSTRAINT species_size  CHECK (LENGTH(species) >= 4)
) ENGINE = INNODB;

INSERT INTO animal (name, gender, species, age) VALUES ('mimosa'   , 'F', 'bos taurus'      , 4);
INSERT INTO animal (name, gender, species, age) VALUES ('rex'      , 'M', 'canis familiaris', 6);
INSERT INTO animal (name, gender, species, age) VALUES ('sylvester', 'M', 'felis catus'     , 8);
"""

mysql_drop: str = "DROP DATABASE IF EXISTS test_fruits;"

sqlite_db : SqliteTestConfig  = SqliteTestConfig ("test/fruits-ok.db", "test/fruits.db")
mysql_db  : MysqlTestConfig   = MysqlTestConfig  (mysql_create, mysql_drop, "root", "root", "127.0.0.1", 3306, "test_fruits")
mariadb_db: MariaDbTestConfig = MariaDbTestConfig(mysql_create, mysql_drop, "root", "root", "127.0.0.1", 3306, "test_fruits")

dbs: dict[str, DbTestConfig] = {"sqlite": sqlite_db, "mysql": mysql_db, "mariadb": mariadb_db}

run_on_dbs: list[DbTestConfig] = []

@applier(dbs)
def test_dbs(db: DbTestConfig) -> None:
    run_on_dbs.append(db)

def test_run_oks() -> None:
    assert run_on_dbs == [sqlite_db, mysql_db, mariadb_db]

@applier(dbs)
def test_fetchone(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        one: tuple[Any, ...] | None = c.fetchone()
        assert one == (2, "strawberry")

@applier(dbs)
def test_fetchall(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@applier(dbs)
def test_fetchmany(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        p1: Sequence[tuple[Any, ...]] = c.fetchmany(2)
        assert p1 == [(1, "orange"), (2, "strawberry")]
        p2: Sequence[tuple[Any, ...]] = c.fetchmany(2)
        assert p2 == [(3, "lemon")]
        p3: Sequence[tuple[Any, ...]] = c.fetchmany(2)
        assert p3 == []

@applier(dbs)
def test_fetchall_class(db: DbTestConfig) -> None:

    @dataclass_validate
    @dataclass(frozen = True)
    class Fruit:
        pk_fruit: int
        name: str

    conn: TransactedConnection = db.conn
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[Fruit] = c.fetchall_class(Fruit)
        assert all == [Fruit(1, "orange"), Fruit(2, "strawberry"), Fruit(3, "lemon")]

@applier(dbs)
def test_execute_insert(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO animal (name, gender, species, age) VALUES (?, ?, ?, ?)", ["bozo", "M", "bos taurus", 65])
        assert c.rowcount == 1
        c.commit()

    with conn as c:
        c.execute("SELECT pk_animal, name, gender, species, age FROM animal")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [ \
            (1, "mimosa", "F", "bos taurus", 4), \
            (2, "rex", "M", "canis familiaris", 6), \
            (3, "sylvester", "M", "felis catus", 8), \
            (4, "bozo", "M", "bos taurus", 65) \
        ]

@applier(dbs)
def test_executemany(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        data: list[list[Any]] = [ \
            ["bozo", "M", "bos taurus", 65], \
            ["1000xeks", "F", "bos taurus", 42], \
            ["sheik edu", "M", "musa acuminata", 36], \
        ]
        c.executemany("INSERT INTO animal (name, gender, species, age) VALUES (?, ?, ?, ?)", data)
        assert c.rowcount == 3
        c.commit()

    with conn as c:
        c.execute("SELECT pk_animal, name, gender, species, age FROM animal")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [ \
            (1, "mimosa", "F", "bos taurus", 4), \
            (2, "rex", "M", "canis familiaris", 6), \
            (3, "sylvester", "M", "felis catus", 8), \
            (4, "bozo", "M", "bos taurus", 65), \
            (5, "1000xeks", "F", "bos taurus", 42), \
            (6, "sheik edu", "M", "musa acuminata", 36) \
        ]

longscript_sqlite: str = """
CREATE TABLE IF NOT EXISTS tree (
    pk_tree INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;

INSERT INTO tree (name) VALUES ('acacia');
INSERT INTO tree (name) VALUES ('ginkgo');
"""

longscript_mysql_a: str = """
CREATE TABLE IF NOT EXISTS tree (
    pk_tree INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name    TEXT    NOT NULL UNIQUE,
    CONSTRAINT CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) ENGINE = INNODB;
"""

longscript_mysql_b: str = """
INSERT INTO tree (name) VALUES ('acacia');
INSERT INTO tree (name) VALUES ('ginkgo');
"""

@sqlite_db.decorator
def test_executescipt_sqlite() -> None:
    conn: TransactedConnection = sqlite_db.conn

    with conn as c:
        c.executescript(longscript_sqlite)
        c.commit()

    with conn as c:
        c.execute("SELECT pk_tree, name FROM tree")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [ \
            (1, "acacia"), \
            (2, "ginkgo") \
        ]

@mysql_db.decorator
def test_executescipt_mysql() -> None:
    conn: TransactedConnection = mysql_db.conn

    with conn as c:
        c.executescript(longscript_mysql_a)
        c.commit()

    with conn as c:
        c.executescript(longscript_mysql_b)
        c.commit()

    with conn as c:
        c.execute("SELECT pk_tree, name FROM tree")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [ \
            (1, "acacia"), \
            (2, "ginkgo") \
        ]

@mariadb_db.decorator
def test_executescipt_mariadb() -> None:
    conn: TransactedConnection = mariadb_db.conn

    with raises(NotImplementedError):
        with conn as c:
            c.executescript(longscript_mysql_a)

@applier(dbs)
def test_commit(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@applier(dbs)
def test_rollback(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.rollback()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@applier(dbs)
def test_transact_1(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    conn.transact(x)()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@applier(dbs)
def test_transact_2(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    @conn.transact
    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    x()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@applier(dbs)
def test_no_transaction(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(TransactionNotActiveException):
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

@applier(dbs)
def test_check_constraint_1(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('abc')")

@applier(dbs)
def test_check_constraint_2(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('123456789012345678901234567890123456789012345678901')")

@applier(dbs)
def test_foreign_key_constraint_on_orphan_insert(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (666)")

@applier(dbs)
def test_foreign_key_constraint_on_update_cascade(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (1)")
        c.commit()

    with conn as c:
        c.execute("UPDATE fruit SET pk_fruit = 777 WHERE pk_fruit = 1")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_1")
        t: tuple[Any, ...] | None = c.fetchone()
        assert t == (777, )

@applier(dbs)
def test_foreign_key_constraint_on_delete_cascade(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (1)")
        c.commit()

    with conn as c:
        c.execute("DELETE FROM fruit WHERE pk_fruit = 1")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_1 WHERE pk_fruit = 1")
        t: Sequence[tuple[Any, ...]] | None  = c.fetchone()
        assert t is None

@applier(dbs)
def test_foreign_key_constraint_on_update_restrict(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_2 (pk_fruit) VALUES (1)")
        c.commit()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("UPDATE fruit SET pk_fruit = 777 WHERE pk_fruit = 1")

    with conn as c:
        c.execute("SELECT pk_fruit FROM juice_2")
        t: tuple[Any, ...] | None = c.fetchone()
        assert t == (1, )

@applier(dbs)
def test_foreign_key_constraint_on_delete_restrict(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with conn as c:
        c.execute("INSERT INTO juice_2 (pk_fruit) VALUES (1)")
        c.commit()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("DELETE FROM fruit WHERE pk_fruit = 1")

    with conn as c:
        c.execute("SELECT a.pk_fruit FROM juice_2 a INNER JOIN fruit b ON a.pk_fruit = b.pk_fruit WHERE a.pk_fruit = 1")
        t: tuple[Any, ...] | None = c.fetchone()
        assert t == (1, )