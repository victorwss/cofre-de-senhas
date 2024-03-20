from typing import Any, Callable
from dataclasses import dataclass
import json
from dacite import Config, from_dict
from .sqlite3conn import SqliteConnectionData
from .mariadbconn import MariadbConnectionData
from .mysqlconn import MysqlConnectionData
from .conn import BadDatabaseConfigException
from .trans import ConnectionData, TransactedConnection


def _raise_it(database_name: str) -> ConnectionData:
    raise BadDatabaseConfigException("Bad or unknown database type " + database_name)


def _read_all(fn: str) -> str:
    import os
    with open(os.getcwd() + "/" + fn, "r", encoding = "utf-8") as f:
        return f.read()


@dataclass(frozen = True)
class DatabaseConfig:
    flavor: str
    properties: dict[str, Any]

    def connect(self) -> TransactedConnection:
        a: Callable[[], ConnectionData] = lambda: SqliteConnectionData .create(**self.properties)
        b: Callable[[], ConnectionData] = lambda: MariadbConnectionData.create(**self.properties)
        c: Callable[[], ConnectionData] = lambda: MysqlConnectionData  .create(**self.properties)
        x: Callable[[], ConnectionData] = lambda: _raise_it(self.flavor)
        d: dict[str, Callable[[], ConnectionData]] = {
            "sqlite" : a,  # noqa: E203
            "mariadb": b,  # noqa: E203
            "mysql"  : c   # noqa: E203
        }
        cd: ConnectionData = d.get(self.flavor, x)()
        return cd.connect()

    @staticmethod
    def from_json(json_props: str) -> "DatabaseConfig":
        d: dict[str, Any] = json.loads(json_props)
        return from_dict(data_class = DatabaseConfig, data = d, config = Config(strict = True))

    @staticmethod
    def from_file(file_name: str) -> "DatabaseConfig":
        return DatabaseConfig.from_json(_read_all(file_name))
