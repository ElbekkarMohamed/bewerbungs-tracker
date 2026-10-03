import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "tracker.db"
SCHEMA = BASE_DIR / "schema.sql"


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(SCHEMA.read_text(encoding="utf-8"))
    db.close()