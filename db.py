import sqlite3
from pathlib import Path
from flask import g

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "tracker.db"
SCHEMA = BASE_DIR / "schema.sql"


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(SCHEMA.read_text(encoding="utf-8"))
    db.close()

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()