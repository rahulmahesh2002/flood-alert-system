# seed_gauges.py
from db_config import get_connection

DEFAULT_GAUGES = [
    ("01646500", "Black River at Dexter, NY",   43.599167, -75.759167, 10.0, 12.0),
    ("02054000", "Mississippi River at NOLA",   29.935000, -90.130000, 15.0, 18.0),
    ("03339000", "Susquehanna at Wilkes‑Barre",  41.273611, -75.881944,  8.0, 10.0),
]

def seed_gauges():
    conn = get_connection()
    cur = conn.cursor()
    # Only insert if the table is empty
    cur.execute("SELECT COUNT(*) FROM gauges")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO gauges (site_id, name, latitude, longitude, action_stage_ft, flood_stage_ft) VALUES (?, ?, ?, ?, ?, ?)",
            DEFAULT_GAUGES
        )
        conn.commit()
    conn.close()
