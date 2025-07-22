# cluster.py
# Pull gauge info+latest reading, label status, and cluster at‑risk gauges

from db_config import get_connection
from sklearn.cluster import DBSCAN
import numpy as np

def get_gauge_data():
    """
    Fetch gauge metadata (incl. name) and latest reading from MySQL.
    Returns a list of dicts:
      [{site_id, name, latitude, longitude,
        action_stage_ft, flood_stage_ft, water_level_ft}, ...]
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT g.site_id, g.name,
           g.latitude, g.longitude,
           g.action_stage_ft, g.flood_stage_ft,
           r.water_level_ft
    FROM gauges AS g
    JOIN (
      SELECT site_id, water_level_ft
      FROM readings
      WHERE (site_id, timestamp) IN (
        SELECT site_id, MAX(timestamp)
        FROM readings
        GROUP BY site_id
      )
    ) AS r ON g.site_id = r.site_id;
    """
    # the inner most query gets the site_id according to latest timesatmp
    # the query above it gets the water level according to site_id
    # the last query completes the join to get all the rel data
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def label_status(gauge):
    """
    Given one gauge dict, return its status:
    - "Warning" if level ≥ flood_stage_ft
    - "Watch"   if level ≥ action_stage_ft
    - "Normal"  otherwise
    """
    lvl = gauge["water_level_ft"]
    if lvl >= gauge["flood_stage_ft"]:
        return "Warning"
    if lvl >= gauge["action_stage_ft"]:
        return "Watch"
    return "Normal"

def cluster_gauges(eps=0.01):
    """
    Cluster all gauges labeled "Watch" or "Warning" by geographic proximity.
    Uses DBSCAN on (latitude, longitude). Returns:
      { cluster_id: [site_id, ...], ... }
    """
    data = get_gauge_data()
    at_risk = [g for g in data if label_status(g) in ("Watch", "Warning")]
    if not at_risk:
        return {}

    coords = np.array([[g["latitude"], g["longitude"]] for g in at_risk])
    db = DBSCAN(eps=eps, min_samples=1).fit(coords)
    labels = db.labels_

    clusters = {}
    for lbl, gauge in zip(labels, at_risk):
        clusters.setdefault(int(lbl), []).append(gauge["site_id"])
    return clusters

if __name__ == "__main__":
    clusters = cluster_gauges()
    if clusters:
        print("Clusters of at-risk gauges:")
        for cid, sites in clusters.items():
            print(f" Cluster {cid}: {sites}")
    else:
        print("No gauges in Watch or Warning status.")
