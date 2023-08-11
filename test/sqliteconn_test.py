import os
import shutil
import sqlite3
from connection.sqlite3conn import Sqlite3ConnectionWrapper
from connection.conn import TransactedConnection, TransactionNotActiveException
from pytest import raises
from dataclasses import dataclass
from validator import dataclass_validate

create = """
CREATE TABLE IF NOT EXISTS fruit (
    pk_fruit        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;
INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');
""";

def register_sqlite() -> TransactedConnection:
    try:
        os.remove("test/test.db")
    except FileNotFoundError as x:
        pass
    shutil.copy2("test/test-ok.db", "test/test.db")
    return TransactedConnection(lambda: Sqlite3ConnectionWrapper(sqlite3.connect("test/test.db")))

def test_fetchone() -> None:
    conn: TransactedConnection = register_sqlite()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit WHERE pk_fruit = 2")
        one: tuple[Any, ...] = c.fetchone()
        assert one == (2, "strawberry")

def test_fetchall() -> None:
    conn: TransactedConnection = register_sqlite()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: list[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

def test_fetchall_class() -> None:

    @dataclass_validate
    @dataclass(frozen = True)
    class Fruit:
        pk_fruit: int
        name: str

    conn: TransactedConnection = register_sqlite()
    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: list[tuple[Any, ...]] = c.fetchall_class(Fruit)
        assert len(all) == 3
        assert all[0].pk_fruit == 1
        assert all[0].name == "orange"
        assert all[1].pk_fruit == 2
        assert all[1].name == "strawberry"
        assert all[2].pk_fruit == 3
        assert all[2].name == "lemon"

def test_commit() -> None:
    conn: TransactedConnection = register_sqlite()

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.commit()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: list[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

def test_rollback() -> None:
    conn: TransactedConnection = register_sqlite()

    with conn as c:
        c.execute("INSERT INTO fruit (name) VALUES ('grape')")
        c.rollback()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: list[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon")]

def test_transact_1() -> None:
    conn: TransactedConnection = register_sqlite()

    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    conn.transact(x)()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: list[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

def test_transact_2() -> None:
    conn: TransactedConnection = register_sqlite()

    @conn.transact
    def x() -> None:
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")

    x()

    with conn as c:
        c.execute("SELECT pk_fruit, name FROM fruit")
        all: list[tuple[Any, ...]] = c.fetchall()
        assert all == [(1, "orange"), (2, "strawberry"), (3, "lemon"), (4, "grape")]

def test_no_transaction() -> None:
    conn: TransactedConnection = register_sqlite()
    with raises(TransactionNotActiveException):
        conn.execute("INSERT INTO fruit (name) VALUES ('grape')")