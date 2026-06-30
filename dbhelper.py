"""
============================================================
 GENERIC DATABASE HELPER — adapt this on exam day
============================================================
This file has 3 tables that mirror almost any CRUD exam shape:

  GROUP   -> a simple master table              (e.g. "Events")
  PERSON  -> a master table that references GROUP (e.g. "Participants")
  ENTRY   -> a transaction table that references PERSON,
             and stores a COMPUTED value         (e.g. "Registration")

HOW TO ADAPT ON TEST DAY:
  1. Rename the table names in init_database() to match the real spec.
  2. Rename the columns in each CREATE TABLE to match the real data
     dictionary (keep the same ORDER as the real spec to reduce mistakes).
  3. Find-and-replace every function name + column name throughout this
     file (Ctrl+H in most editors) to match — e.g. Group -> Event,
     groupID -> evCode, groupName -> evName, etc.
  4. The pattern (open conn -> cursor -> execute -> commit -> close)
     never changes. Don't rewrite logic, just rename.
============================================================
"""
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash


def connect():
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_path, 'database.db')
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row['groupName']
    return connection


def init_database():
    """Creates all tables if they don't already exist. Safe to call every time the app starts."""
    conn = connect()
    cur = conn.cursor()

    # ---- TABLE 1: GROUP (rename to your first master entity, e.g. Events) ----
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Group_ (
            groupID    INTEGER PRIMARY KEY AUTOINCREMENT,
            groupName  TEXT NOT NULL,
            groupDate  DATE NOT NULL,
            groupPlace TEXT NOT NULL,
            groupFee   DECIMAL(10,2) NOT NULL
        )
    ''')

    # ---- TABLE 2: PERSON (rename to your 2nd entity, e.g. Participants) ----
    # Has a Foreign Key (groupID) pointing back to TABLE 1.
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Person (
            personID   INTEGER PRIMARY KEY AUTOINCREMENT,
            groupID    INTEGER NOT NULL,
            personFName TEXT NOT NULL,
            personLName TEXT NOT NULL,
            personRate  DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (groupID) REFERENCES Group_(groupID)
        )
    ''')

    # ---- TABLE 3: ENTRY (rename to your transaction entity, e.g. Registration) ----
    # Has a Foreign Key (personID) pointing back to TABLE 2.
    # Stores a value (entryAmount) that gets COMPUTED in app.py before saving.
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Entry (
            entryID     INTEGER PRIMARY KEY AUTOINCREMENT,
            personID    INTEGER NOT NULL,
            entryDate   DATE NOT NULL,
            entryAmount DECIMAL(10,2) NOT NULL,
            entryMode   TEXT NOT NULL,
            FOREIGN KEY (personID) REFERENCES Person(personID)
        )
    ''')

    # ---- TABLE 4: USERS (account system — login, register, profile CRUD) ----
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            userID    INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT NOT NULL UNIQUE,
            password  TEXT NOT NULL,
            firstName TEXT NOT NULL,
            lastName  TEXT NOT NULL,
            email     TEXT NOT NULL UNIQUE
        )
    ''')

    # Seed one default account so login still works the very first time you run this,
    # before anyone has registered. Exam instructions usually say "Login as: Local Admin" —
    # this is that account. Safe to run every time: only inserts if it's not already there.
    cur.execute("SELECT * FROM Users WHERE username='admin'")
    if cur.fetchone() is None:
        cur.execute('''
            INSERT INTO Users (username, password, firstName, lastName, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', generate_password_hash('admin'), 'Local', 'Admin', 'admin@example.com'))

    conn.commit()
    conn.close()


def getall(table):
    """Generic 'SELECT * FROM table' helper. Works for any table name you pass in."""
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    conn.close()
    return rows


# ============================================================
# GROUP  (Create / Read / Update / Delete)
# ============================================================
def add_group(groupName, groupDate, groupPlace, groupFee):
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO Group_ (groupName, groupDate, groupPlace, groupFee)
        VALUES (?, ?, ?, ?)
    ''', (groupName, groupDate, groupPlace, groupFee))
    conn.commit()
    conn.close()

def get_all_groups():
    return getall('Group_')

def get_group(groupID):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Group_ WHERE groupID=?", (groupID,))
    row = cur.fetchone()
    conn.close()
    return row

def update_group(groupID, groupName, groupDate, groupPlace, groupFee):
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        UPDATE Group_
        SET groupName=?, groupDate=?, groupPlace=?, groupFee=?
        WHERE groupID=?
    ''', (groupName, groupDate, groupPlace, groupFee, groupID))
    conn.commit()
    conn.close()

def delete_group(groupID):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM Group_ WHERE groupID=?", (groupID,))
    conn.commit()
    conn.close()


# ============================================================
# PERSON  (Create / Read / Update / Delete)
# ============================================================
def add_person(groupID, personFName, personLName, personRate):
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO Person (groupID, personFName, personLName, personRate)
        VALUES (?, ?, ?, ?)
    ''', (groupID, personFName, personLName, personRate))
    conn.commit()
    conn.close()

def get_all_persons():
    return getall('Person')

def get_person(personID):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Person WHERE personID=?", (personID,))
    row = cur.fetchone()
    conn.close()
    return row

def update_person(personID, groupID, personFName, personLName, personRate):
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        UPDATE Person
        SET groupID=?, personFName=?, personLName=?, personRate=?
        WHERE personID=?
    ''', (groupID, personFName, personLName, personRate, personID))
    conn.commit()
    conn.close()

def delete_person(personID):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM Person WHERE personID=?", (personID,))
    conn.commit()
    conn.close()


# ============================================================
# ENTRY  (Create + Read only — most "transaction" tables in these
# exams only need adding + viewing, not editing/deleting. Add
# update_entry/delete_entry yourself if the real spec asks for them —
# just copy the pattern from PERSON above.)
# ============================================================
def add_entry(personID, entryDate, entryAmount, entryMode):
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO Entry (personID, entryDate, entryAmount, entryMode)
        VALUES (?, ?, ?, ?)
    ''', (personID, entryDate, entryAmount, entryMode))
    conn.commit()
    conn.close()

def get_all_entries():
    """Returns every entry, newest first — most specs ask for latest-to-oldest."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Entry ORDER BY entryID DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_entries_joined(groupID=None):
    """
    THE MONITORING QUERY.
    Joins Entry -> Person -> Group_ so one row has everything the
    monitoring/report page needs to display: group name, person's
    full name, entry date, entry amount.

    Pass a groupID to filter to just that group; pass None to get everything.
    This is the function your /monitoring route will call.
    """
    conn = connect()
    cur = conn.cursor()
    if groupID:
        cur.execute('''
            SELECT Entry.entryID, Entry.entryDate, Entry.entryAmount, Entry.entryMode,
                   Person.personFName, Person.personLName, Person.personRate,
                   Group_.groupID, Group_.groupName, Group_.groupFee
            FROM Entry
            JOIN Person ON Entry.personID = Person.personID
            JOIN Group_  ON Person.groupID  = Group_.groupID
            WHERE Group_.groupID = ?
            ORDER BY Entry.entryID DESC
        ''', (groupID,))
    else:
        cur.execute('''
            SELECT Entry.entryID, Entry.entryDate, Entry.entryAmount, Entry.entryMode,
                   Person.personFName, Person.personLName, Person.personRate,
                   Group_.groupID, Group_.groupName, Group_.groupFee
            FROM Entry
            JOIN Person ON Entry.personID = Person.personID
            JOIN Group_  ON Person.groupID  = Group_.groupID
            ORDER BY Entry.entryID DESC
        ''')
    rows = cur.fetchall()
    conn.close()
    return rows


# ============================================================
# USERS  (account system: register / login / view / update / delete)
# ============================================================
def add_user(username, password_hash, firstName, lastName, email):
    """Creates a new account. Caller must hash the password BEFORE calling this
    (see generate_password_hash in app.py's register route) — never store plain text."""
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO Users (username, password, firstName, lastName, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, password_hash, firstName, lastName, email))
    conn.commit()
    conn.close()

def get_all_users():
    return getall('Users')

def get_user_by_id(userID):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE userID=?", (userID,))
    row = cur.fetchone()
    conn.close()
    return row

def get_user_by_username(username):
    """Used by the login route to look up the stored password hash for comparison."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def get_user_by_email(email):
    """Used during registration to check an email isn't already taken."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    return row

def update_user(userID, firstName, lastName, email, username):
    """Updates profile fields. Does NOT touch the password — see update_user_password."""
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        UPDATE Users
        SET firstName=?, lastName=?, email=?, username=?
        WHERE userID=?
    ''', (firstName, lastName, email, username, userID))
    conn.commit()
    conn.close()

def update_user_password(userID, password_hash):
    """Separate function on purpose — only call this when the user actually
    typed a new password, so editing a profile doesn't accidentally wipe it."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET password=? WHERE userID=?", (password_hash, userID))
    conn.commit()
    conn.close()

def delete_user(userID):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM Users WHERE userID=?", (userID,))
    conn.commit()
    conn.close()
