import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).with_name("Library.db")

TABLES = {
    "author": {"title": "authors", "sql_table": "Author", "id": "authID", "fields": [
        {"name": "authLName", "label": "Last Name", "letters_only": True},
        {"name": "authFName", "label": "First Name", "letters_only": True},
        {"name": "authMName", "label": "Middle Name", "letters_only": True},
    ]},

    "book": {"title": "books", "sql_table": "Book", "id": "bookID", "fields": [
        {"name": "bookTitle", "label": "Title", "type": "text"},
        {"name": "bookCopies", "label": "Copies", "type": "number"},
        {"name": "authID", "label": "Author", "type": "choice", "choice": "author", "choice_id": "authID", "choice_label": "authFName"},
    ]},

    "student": {"title": "students", "sql_table": "Student", "id": "studID", "fields": [
            {"name": "studFName", "label": "First Name", "letters_only": True},
            {"name": "studMName", "label": "Middle Name", "letters_only": True},
            {"name": "studLName", "label": "Last Name", "letters_only": True},
        ]},

}


def connect():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS Author (
                authID INTEGER PRIMARY KEY AUTOINCREMENT,
                authLName TEXT NOT NULL,
                authFName TEXT NOT NULL,
                authMName TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Book (
                bookID INTEGER PRIMARY KEY AUTOINCREMENT,
                bookTitle TEXT NOT NULL,
                bookCopies INTEGER NOT NULL,
                authID INTEGER NOT NULL,
                FOREIGN KEY (authID) REFERENCES Author(authID)
            );

            CREATE TABLE IF NOT EXISTS Student (
                studID INTEGER PRIMARY KEY AUTOINCREMENT,
                studFName TEXT NOT NULL,
                studMName TEXT NOT NULL,
                studLName TEXT NOT NULL
            );

        """)


class Database:
    """Same pattern for each entity: INSERT, SELECT, UPDATE, DELETE."""
    def add(self, table, info, values):
        names = [field["name"] for field in info["fields"]]
        sql = f"INSERT INTO {info['sql_table']} ({', '.join(names)}) VALUES ({', '.join('?' for _ in values)})"
        with connect() as db:
            db.execute(sql, values)

    def list(self, table, info, search=""):
        sql = f"SELECT * FROM {info['sql_table']}"
        values = []
        if search:
            if search.isdigit():
                sql += f" WHERE {info['id']}=?"
                values = [int(search)]
            else:
                names = [field["name"] for field in info["fields"]]
                sql += " WHERE " + " OR ".join(
                    f"CAST({name} AS TEXT) LIKE ?" for name in names
                )
                values = [f"%{search}%"] * len(names)
        sql += f" ORDER BY {info['id']} DESC"
        with connect() as db:
            return db.execute(sql, values).fetchall()

    def update(self, table, info, record_id, values):
        names = [field["name"] for field in info["fields"]]
        sets = ", ".join(f"{name}=?" for name in names)
        with connect() as db:
            db.execute(f"UPDATE {info['sql_table']} SET {sets} WHERE {info['id']}=?", [*values, record_id])

    def delete(self, table, info, record_id):
        with connect() as db:
            db.execute(f"DELETE FROM {info['sql_table']} WHERE {info['id']}=?", (record_id,))
            count = db.execute(f"SELECT COUNT(*) FROM {info['sql_table']}").fetchone()[0]
            if count == 0:
                db.execute("DELETE FROM sqlite_sequence WHERE name=?", (info["sql_table"],))

    def choices(self, table):
        info = TABLES[table]
        with connect() as db:
            return db.execute(f"SELECT * FROM {info['sql_table']} ORDER BY {info['id']}").fetchall()


DB = Database()
