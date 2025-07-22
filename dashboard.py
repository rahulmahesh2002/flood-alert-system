# dashboard.py
# Streamlit app: map, clusters, pop-up alerts, and time-series viewer

import streamlit as st
import pandas as pd
import pydeck as pdk
from cluster import get_gauge_data, label_status, cluster_gauges
from db_config import get_connection

st.set_page_config(page_title="Flood Alert Dashboard", layout="wide")
st.title("🌊 Community Flood‑Alert Dashboard")

# 1. Load & annotate gauge data
data = get_gauge_data()
df = pd.DataFrame(data) # converted it into a py dataframe
df["status"] = df.apply(label_status, axis=1) # adds status acc to function label_status 
# since axis = 1,data inserted rowwise
# 2. Pop‑up alerts on status change
if "prev_statuses" not in st.session_state:
    st.session_state.prev_statuses = {}

# loops through each row
# It detects changes in status for each site and shows a toast alert if the status has changed since the last check.
for _, row in df.iterrows():
    sid, new = row.site_id, row.status
    old = st.session_state.prev_statuses.get(sid)
    if old and new != old:
        st.toast(f"⚠️ {row.name}: {old} → {new}", icon="🚨")
    st.session_state.prev_statuses[sid] = new

# 3. Map + clusters
color_map = {"Normal": [0,255,0], "Watch": [255,255,0], "Warning": [255,0,0]}
df["color"] = df["status"].map(color_map)
mid_lat, mid_lon = df.latitude.mean(), df.longitude.mean()

st.subheader("Gauge Status Map")
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(latitude=mid_lat, longitude=mid_lon, zoom=5),
    layers=[pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude","latitude"],
        get_color="color",
        get_radius=5000,
        pickable=True
    )]
))

clusters = cluster_gauges()
if clusters:
    st.subheader("At‑Risk Gauge Clusters")
    for cid, sites in clusters.items():
        names = df[df.site_id.isin(sites)]["name"].tolist()
        st.write(f"• Cluster {cid}: {names}")

st.markdown("---")

# 4. Time‑Series Viewer
st.subheader("Gauge Time‑Series")
site_ids = df.site_id.tolist()
sel = st.selectbox(
    "Select a gauge",
    options=site_ids,
    format_func=lambda s: df.loc[df.site_id==s, "name"].values[0]
)

# Fetch last 48h of readings
conn = get_connection()
query = """
SELECT timestamp, water_level_ft
FROM readings
WHERE site_id = %s AND timestamp >= NOW() - INTERVAL 48 HOUR
ORDER BY timestamp;
"""
ts_df = pd.read_sql(query, conn, params=(sel,))
conn.close()

if ts_df.empty:
    st.warning("No readings in the past 48 hours for this gauge.")
else:
    # Display line chart (thresholds shown in legend text)
    st.line_chart(ts_df.rename(columns={"water_level_ft":"Water Level (ft)"}).set_index("timestamp"))
    g = df[df.site_id==sel].iloc[0]
    # gets the first row of the seected site_id
    st.write(f"**Action Stage:** {g.action_stage_ft} ft  **Flood Stage:** {g.flood_stage_ft} ft")
