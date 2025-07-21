# seed_gauges.py
import sqlite3
from db_config import get_connection

DEFAULT_GAUGES = [
    ("01646500", "Black River at Dexter, NY", 43.599167, -75.759167, 10.0, 12.0),
    ("02054000", "Mississippi River at NOLA", 29.935000, -90.130000, 15.0, 18.0),
    ("03339000", "Susquehanna at Wilkes-Barre, PA", 41.273611, -75.881944, 8.0, 10.0),
]

def init_db():
    """
    Create tables if they don't exist, by running schema.sql.
    """
    conn = get_connection()
    sql = open("schema.sql", "r").read()
    conn.executescript(sql)
    conn.close()

def seed_gauges():
    """
    Call init_db(), then insert DEFAULT_GAUGES if gauges table is empty.
    """
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM gauges;")
    if cur.fetchone()["cnt"] == 0:
        cur.executemany(
            """
            INSERT INTO gauges
              (site_id, name, latitude, longitude, action_stage_ft, flood_stage_ft)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            DEFAULT_GAUGES
        )
        conn.commit()
    conn.close()

