import sqlite3
from connection.conn import TransactedConnection
from connection.sqlite3conn import Sqlite3ConnectionWrapper

cf = TransactedConnection(lambda: Sqlite3ConnectionWrapper(sqlite3.connect("banco.db")))