from typing import Any, Callable
from dataclasses import dataclass
import json
from dacite import Config, from_dict
from .sqlite3conn import SqliteConnectionData
from .mariadbconn import MariadbConnectionData
from .mysqlconn import MysqlConnectionData
from .conn import BadDatabaseConfigException
from .trans import ConnectionData, TransactedConnection

def _raiseit(database_name: str) -> ConnectionData:
    raise BadDatabaseConfigException("Bad or unknown database type " + database_name)

def _read_all(fn: str) -> str:
    import os
    with open(os.getcwd() + "/" + fn, "r", encoding = "utf-8") as f:
        return f.read()

@dataclass
class _DatabaseConfig:
    database_name: str
    properties: dict[str, Any]

    def connect(self) -> TransactedConnection:
        database_name: str = self.database_name
        a: Callable[[], ConnectionData] = lambda: SqliteConnectionData .create(**self.properties)
        b: Callable[[], ConnectionData] = lambda: MariadbConnectionData.create(**self.properties)
        c: Callable[[], ConnectionData] = lambda: MysqlConnectionData  .create(**self.properties)
        x: Callable[[], ConnectionData] = lambda: _raiseit(database_name)
        d: dict[str, Callable[[], ConnectionData]] = { \
            "sqlite" : a, \
            "mariadb": b, \
            "mysql"  : c  \
        }
        cd: ConnectionData = d.get(database_name, x)()
        return cd.connect()

def connect_with_json(json_props: str) -> TransactedConnection:
    d: dict[str, Any] = json.loads(json_props)
    dc: _DatabaseConfig = from_dict(data_class = _DatabaseConfig, data = d, config = Config(strict = True))
    return dc.connect()

def connect_from_file(file_name: str) -> TransactedConnection:
    return connect_with_json(_read_all(file_name))