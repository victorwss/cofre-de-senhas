from typing import Sequence
from connection.conn import RAW_DATA, IntegrityViolationException
from connection.trans import TransactedConnection
from pytest import raises
from ..fixtures import assert_dbf_ok, dbs_f, applier, DbTestConfig


run_on_dbs: list[DbTestConfig] = []


@applier(dbs_f)
def test_dbs(db: DbTestConfig) -> None:
    run_on_dbs.append(db)


@applier(dbs_f, assert_dbf_ok)
def test_check_constraint_1(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('abc')")


@applier(dbs_f, assert_dbf_ok)
def test_check_constraint_2(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO fruit (name) VALUES ('123456789012345678901234567890123456789012345678901')")


@applier(dbs_f, assert_dbf_ok)
def test_foreign_key_constraint_on_orphan_insert(db: DbTestConfig) -> None:
    conn: TransactedConnection = db.conn

    with raises(IntegrityViolationException):
        with conn as c:
            c.execute("INSERT INTO juice_1 (pk_fruit) VALUES (666)")


@applier(dbs_f, assert_dbf_ok)
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


@applier(dbs_f, assert_dbf_ok)
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


@applier(dbs_f, assert_dbf_ok)
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


@applier(dbs_f, assert_dbf_ok)
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
