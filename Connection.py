import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv("LOCAL_DB_PATH", "local.db")

@contextmanager
def get_local_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()