import sqlite3

def get_connection():
    """
    Connect to the local SQLite database (database.db).
    Enables dict‑style row access via row_factory.
    """
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

