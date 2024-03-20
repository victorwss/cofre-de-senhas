from typing import Sequence
from connection.conn import RAW_DATA, IntegrityViolationException, TransactionNotActiveException
from connection.trans import TransactedConnection
from pytest import raises
from ..fixtures import applier, DbTestConfig, dbs_f as dbs, sqlite_db_f as sqlite_db, mysql_db_f as mysql_db, mariadb_db_f as mariadb_db


run_on_dbs: list[DbTestConfig] = []


@applier(dbs)
def test_dbs(db: DbTestConfig) -> None:
    run_on_dbs.append(db)


def test_run_oks() -> None:
    assert run_on_dbs == [sqlite_db, mysql_db, mariadb_db]


def assert_db_ok(db: DbTestConfig) -> None:
    assert db in run_on_dbs, "Database connector failed to load."


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
        assert not c.wrapped.autocommit
        assert c.raw_connection.autocommit in [False, -1]          # type: ignore
        assert c.wrapped.raw_connection.autocommit in [False, -1]  # type: ignore
