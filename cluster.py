from db_config import get_connection
from sklearn.cluster import DBSCAN
import numpy as np

def get_gauge_data():
    """
    Return a list of dicts with each gauge's metadata and latest reading.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT g.site_id, g.name, g.latitude, g.longitude,
               g.action_stage_ft, g.flood_stage_ft,
               r.water_level_ft
        FROM gauges AS g
        JOIN readings AS r
          ON g.site_id = r.site_id
        WHERE r.timestamp = (
            SELECT MAX(timestamp)
            FROM readings
            WHERE site_id = g.site_id
        );
    """)
    rows = cur.fetchall()
    conn.close()
    # sqlite3.Row behaves like a dict
    return [dict(row) for row in rows]

def label_status(g):
    """
    Label a gauge as Normal/Watch/Warning based on thresholds.
    """
    lvl = g["water_level_ft"]
    if lvl >= g["flood_stage_ft"]:
        return "Warning"
    if lvl >= g["action_stage_ft"]:
        return "Watch"
    return "Normal"

def cluster_gauges(eps=0.01):
    """
    Cluster all Watch/Warning gauges by geographic proximity using DBSCAN.
    Returns {cluster_id: [site_id,...], ...}.
    """
    data = get_gauge_data()
    at_risk = [g for g in data if label_status(g) in ("Watch", "Warning")]
    if not at_risk:
        return {}
    coords = np.array([[g["latitude"], g["longitude"]] for g in at_risk])
    labels = DBSCAN(eps=eps, min_samples=1).fit_predict(coords)
    clusters = {}
    for lbl, g in zip(labels, at_risk):
        clusters.setdefault(int(lbl), []).append(g["site_id"])
    return clusters

