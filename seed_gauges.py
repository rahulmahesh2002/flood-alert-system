from db_config import get_connection

# Demo gauge stations to seed on first run
DEFAULT_GAUGES = [
    ("01646500", "Black River at Dexter, NY", 43.599167, -75.759167, 10.0, 12.0),
    ("02054000", "Mississippi River at NOLA", 29.935000, -90.130000, 15.0, 18.0),
    ("03339000", "Susquehanna at Wilkes-Barre, PA", 41.273611, -75.881944, 8.0, 10.0),
]

def seed_gauges():
    """
    If the gauges table is empty, insert DEFAULT_GAUGES.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM gauges;")
    count = cur.fetchone()["cnt"]
    if count == 0:
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
