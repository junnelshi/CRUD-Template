import sqlite3
from pathlib import Path

from django.db.models import sql

DB_FILE = Path(__file__).with_name("Event.db")

TABLES = {
    "participant": {"title": "participants", "sql_table": "Participant", "id": "partID", "fields": [
            {"name": "evCode", "label": "Event", "type": "choice", "choice": "event", "choice_id": "evCode", "choice_label": "evName"},
            {"name": "partFName", "label": "First Name", "letters_only": True},
            {"name": "partLName", "label": "Last Name", "letters_only": True},
            {"name": "partDRate", "label": "Discount Rate", "type": "decimal"},
    ]},

    "event": {"title": "events", "sql_table": "Event", "id": "evCode", "fields": [
            {"name": "evName", "label": "Event Name", "letters_only": True},
            {"name": "evDate", "label": "Event Date", "type": "date"},
            {"name": "evVenue", "label": "Event Venue", "type": "text"},
            {"name": "evRFee", "label": "Registration Fee", "type": "decimal"},
    ]},

    "registration": {"title": "registrations", "sql_table": "Registration", "id": "regCode", "fields": [
            {"name": "partID", "label": "Participant", "type": "choice", "choice": "participant", "choice_id": "partID", "choice_label": "partFName", "choice_display": ["partFName", "partLName"]},
            {"name": "regDate", "label": "Registration Date", "type": "date"},
            {"name": "regFPaid", "label": "Fee Paid", "type": "decimal"},
            {"name": "regPMode", "label": "Discount Rate", "type": "text"},
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
            CREATE TABLE IF NOT EXISTS Participant (
                partID INTEGER PRIMARY KEY AUTOINCREMENT,
                evCode INTEGER NOT NULL,
                partFName TEXT NOT NULL,
                partLName TEXT NOT NULL,
                partDRate DECIMAL NOT NULL,
                FOREIGN KEY (evCode) REFERENCES Event(evCode)
            );
            CREATE TABLE IF NOT EXISTS Event (
                evCode INTEGER PRIMARY KEY AUTOINCREMENT,
                evName TEXT NOT NULL,
                evDate DATE NOT NULL,
                evVenue TEXT NOT NULL,
                evRFee DECIMAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Registration (
                regCode INTEGER PRIMARY KEY AUTOINCREMENT,
                partID INTEGER NOT NULL,
                regDate DATE NOT NULL,
                regFPaid DECIMAL NOT NULL,
                regPMode TEXT NOT NULL,
                FOREIGN KEY (partID) REFERENCES Participant(partID)
            );

        """)


class Database:
    """Same pattern for each entity: INSERT, SELECT, UPDATE, DELETE."""
    
    def registration_fee(self, participant_id):
        sql = """
        SELECT Event.evRFee, Participant.partDRate
        FROM Participant
        JOIN Event ON Event.evCode = Participant.evCode
        WHERE Participant.partID = ?
        """

        with connect() as db:
            row = db.execute(sql, (participant_id,)).fetchone()

        if row is None:
            return None

        return round(float(row["evRFee"]) - float(row["partDRate"]), 2)


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
