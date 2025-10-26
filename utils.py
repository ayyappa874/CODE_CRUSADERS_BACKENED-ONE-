import sqlite3
import os

def init_db(db_path):
    if os.path.exists(db_path):
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)')
    c.execute('CREATE TABLE groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, owner_id INTEGER)')
    c.execute('CREATE TABLE polls (id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER, title TEXT)')
    c.execute('CREATE TABLE poll_options (id INTEGER PRIMARY KEY AUTOINCREMENT, poll_id INTEGER, option_text TEXT)')
    c.execute('CREATE TABLE votes (id INTEGER PRIMARY KEY AUTOINCREMENT, poll_id INTEGER, option_id INTEGER, user_id INTEGER)')
    conn.commit()
    conn.close()

def query_db(db_path, query, args=(), one=False):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    if one:
        return dict(rv[0]) if rv else None
    return [dict(r) for r in rv]

def execute_db(db_path, query, args=()):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last = cur.lastrowid
    conn.close()
    return last
