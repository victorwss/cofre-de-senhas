from pytest import mark, raises
from connection.conn import RAW_DATA, BadDatabaseConfigException
from connection.load import DatabaseConfig
from json.decoder import JSONDecodeError
from dacite.exceptions import UnexpectedDataError, WrongTypeError
from validator import TypeValidationError


fpath: str = "test/conn/"
files_ok: list[str] = [f"{fpath}test-sqlite.json", f"{fpath}test-mysql.json", f"{fpath}test-mariadb.json"]
files_bad: list[str] = [f"{fpath}testX-banana.json", f"{fpath}test-bad-sqlite.json", f"{fpath}test-bad-mysql.json", f"{fpath}test-bad-mariadb.json"]
do_not_exist: str = f"{fpath}do-not-exist.json"
futebol: str = f"{fpath}testX-futebol.json"
bad_flavor: str = f"{fpath}testX-42.json"
gibberish: str = f"{fpath}testX-gibberish.json"


def _read_all(fn: str) -> str:
    import os
    with open(os.getcwd() + "/" + fn, "r", encoding = "utf-8") as f:
        return f.read()


def test_simple_create() -> None:
    x: DatabaseConfig = DatabaseConfig("test", {"a": "b", "c": 555})
    assert x.flavor == "test"
    assert x.properties == {"a": "b", "c": 555}


def test_bad_create_1() -> None:
    with raises(TypeValidationError):
        DatabaseConfig(42, {"a": "b", "c": 555})  # type: ignore


def test_bad_create_2() -> None:
    with raises(TypeValidationError):
        DatabaseConfig("foo", [])  # type: ignore


def test_bad_create_3() -> None:
    with raises(TypeError):
        DatabaseConfig()  # type: ignore


@mark.parametrize("file_name", files_ok)
def test_from_json_ok(file_name: str) -> None:
    json: str = _read_all(file_name)
    d: DatabaseConfig = DatabaseConfig.from_json(json)
    with d.connect() as c:
        c.execute("SELECT 1")
        t: tuple[RAW_DATA, ...] | None = c.fetchone()
        assert t == (1, )


@mark.parametrize("file_name", files_ok)
def test_from_json_file_ok(file_name: str) -> None:
    d: DatabaseConfig = DatabaseConfig.from_file(file_name)
    with d.connect() as c:
        c.execute("SELECT 1")
        t: tuple[RAW_DATA, ...] | None = c.fetchone()
        assert t == (1, )


def test_from_json_file_bad_file() -> None:
    with raises(FileNotFoundError):
        DatabaseConfig.from_file(do_not_exist)


def test_from_json_bad_format() -> None:
    json: str = _read_all(futebol)
    with raises(UnexpectedDataError):
        DatabaseConfig.from_json(json)


def test_from_json_file_bad_format() -> None:
    with raises(UnexpectedDataError):
        DatabaseConfig.from_file(futebol)


def test_from_json_bad_flavor_type() -> None:
    json: str = _read_all(bad_flavor)
    with raises(WrongTypeError):
        DatabaseConfig.from_json(json)


def test_from_json_file_bad_flavor_type() -> None:
    with raises(WrongTypeError):
        DatabaseConfig.from_file(bad_flavor)


def test_from_json_bad_json() -> None:
    json: str = _read_all(gibberish)
    with raises(JSONDecodeError):
        DatabaseConfig.from_json(json)


def test_from_json_file_bad_json() -> None:
    with raises(JSONDecodeError):
        DatabaseConfig.from_file(gibberish)


@mark.parametrize("file_name", files_bad)
def test_from_json_bad_config_props(file_name: str) -> None:
    d: DatabaseConfig = DatabaseConfig.from_file(file_name)
    with raises(BadDatabaseConfigException):
        d.connect()


@mark.parametrize("file_name", files_bad)
def test_from_json_file_bad_config_props(file_name: str) -> None:
    json: str = _read_all(file_name)
    d: DatabaseConfig = DatabaseConfig.from_json(json)
    with raises(BadDatabaseConfigException):
        d.connect()
