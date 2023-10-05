import sqlite3
from typing import Any, Callable, Sequence
from connection.sqlite3conn import ConnectionData
from connection.conn import IntegrityViolationException, TransactionNotActiveException
from connection.trans import TransactedConnection
from decorators.single import Single
from pytest import raises
from dataclasses import dataclass
from validator import dataclass_validate
from ..db_test_util import DbTestConfig

db: DbTestConfig = DbTestConfig("test/fruits-ok.db", "test/fruits.db")

create = """
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
    species         TEXT    NOt NULL             CHECK (LENGTH(species) >= 4 AND LENGTH(species) <= 50),
    age             INTEGER NOT NULL
) STRICT;

INSERT INTO animal (name, gender, species, age) VALUES ('mimosa'   , 'F', 'bos taurus'      , 4);
INSERT INTO animal (name, gender, species, age) VALUES ('rex'      , 'M', 'canis familiaris', 6);
INSERT INTO animal (name, gender, species, age) VALUES ('sylvester', 'M', 'felis catus'     , 8);
""";

@db.decorator
def test_fetchone() -> None:
    conn: TransactedConnection = db.new_connection()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        one: tuple[Any, ...] | None = c.fetchone()
        assert one == (2, "strawberry")

@db.decorator
def test_fetchall() -> None:
    conn: TransactedConnection = db.new_connection()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@db.decorator
def test_fetchmany() -> None:
    conn: TransactedConnection = db.new_connection()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        p1: Sequence[tuple[Any, ...]] = c.fetchmany(2)
        assert p1 == [(1, "orange"), (2, "strawberry")]
        p2: Sequence[tuple[Any, ...]] = c.fetchmany(2)
        assert p2 == [(3, "lemon")]
        p3: Sequence[tuple[Any, ...]] = c.fetchmany(2)
        assert p3 == []

@db.decorator
def test_fetchall_class() -> None:

    @dataclass_validate
    @dataclass(frozen = True)
    class Fruit:
        pk_fruit: int
        name: str

    conn: TransactedConnection = db.new_connection()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[Fruit] = c.fetchall_class(Fruit)
        assert all == [Fruit(1, "orange"), Fruit(2, "strawberry"), Fruit(3, "lemon")]

@db.decorator
def test_execute_insert() -> None:
    conn: TransactedConnection = db.new_connection()

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

@db.decorator
def test_executemany() -> None:
    conn: TransactedConnection = db.new_connection()

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

script: str = """
CREATE TABLE IF NOT EXISTS tree (
    pk_tree INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;

INSERT INTO tree (name) VALUES ('acacia');
INSERT INTO tree (name) VALUES ('ginkgo');
"""

@db.decorator
def test_executescipt() -> None:

    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.executescript(script)
        c.commit()

    with conn as c:
        c.execute("SELECT pk_tree, name FROM tree")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [ \
            (1, "acacia"), \
            (2, "ginkgo") \
        ]

@db.decorator
def test_commit() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@db.decorator
def test_rollback() -> None:
    conn: TransactedConnection = db.new_connection()

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.rollback()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

@db.decorator
def test_transact_1() -> None:
    conn: TransactedConnection = db.new_connection()

    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    conn.transact(x)()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@db.decorator
def test_transact_2() -> None:
    conn: TransactedConnection = db.new_connection()

    @conn.transact
    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    x()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: Sequence[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

@db.decorator
def test_no_transaction() -> None:
    conn: TransactedConnection = db.new_connection()
    with raises(TransactionNotActiveException):
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

@db.decorator
def test_check_constraint_1() -> None:
    conn: TransactedConnection = db.new_connection()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('abc')")

@db.decorator
def test_check_constraint_2() -> None:
    conn: TransactedConnection = db.new_connection()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('123456789012345678901234567890123456789012345678901')")

@db.decorator
def test_foreign_key_constraint_on_orphan_insert() -> None:
    conn: TransactedConnection = db.new_connection()

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (666)")

@db.decorator
def test_foreign_key_constraint_on_update_cascade() -> None:
    conn: TransactedConnection = db.new_connection()

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

@db.decorator
def test_foreign_key_constraint_on_delete_cascade() -> None:
    conn: TransactedConnection = db.new_connection()

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

@db.decorator
def test_foreign_key_constraint_on_update_restrict() -> None:
    conn: TransactedConnection = db.new_connection()

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

@db.decorator
def test_foreign_key_constraint_on_delete_restrict() -> None:
    conn: TransactedConnection = db.new_connection()

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