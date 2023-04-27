import sqlite3
from connection.conn import TransactedConnection
from connection.sqlite3conn import Sqlite3ConnectionWrapper
from decorators.tracer import Logger

cf = TransactedConnection(lambda: Sqlite3ConnectionWrapper(sqlite3.connect("cofre.db")))
log = Logger.for_print_fn()