from typing import Any
from connection.trans import TransactedConnection
from connection.load import connect_from_file


def connect() -> TransactedConnection:
    return connect_from_file("cofre.json")