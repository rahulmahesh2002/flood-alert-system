import streamlit as st

# 0. Ensure the SQLite schema is created and default gauges are seeded
from seed_gauges import seed_gauges
seed_gauges()

# 1. Now safe to import data‑loading and clustering functions
from cluster import get_gauge_data, label_status, cluster_gauges
import pandas as pd
import pydeck as pdk
from db_config import get_connection

st.set_page_config(page_title="Flood‑Alert Dashboard", layout="wide")
st.title("🌊 Community Flood‑Alert Dashboard")

# 2. Load & label
data = get_gauge_data()
df = pd.DataFrame(data)
df["status"] = df.apply(label_status, axis=1)

# 3. Pop‑up alerts on status change
if "prev_statuses" not in st.session_state:
    st.session_state.prev_statuses = {}
for _, row in df.iterrows():
    sid, new = row["site_id"], row["status"]
    old = st.session_state.prev_statuses.get(sid)
    if old and new != old:
        st.toast(f"⚠️ {row['name']}: {old} → {new}", icon="🚨")
    st.session_state.prev_statuses[sid] = new

# 4. Map visualization
color_map = {"Normal":[0,255,0], "Watch":[255,255,0], "Warning":[255,0,0]}
df["color"] = df["status"].map(color_map)
mid_lat, mid_lon = df.latitude.mean(), df.longitude.mean()

st.subheader("Gauge Status Map")
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=mid_lat, longitude=mid_lon, zoom=5
    ),
    layers=[pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude","latitude"],
        get_color="color",
        get_radius=5000,
        pickable=True
    )]
))

# 5. Cluster listing
clusters = cluster_gauges()
if clusters:
    st.subheader("At‑Risk Gauge Clusters")
    for cid, sites in clusters.items():
        names = df[df.site_id.isin(sites)]["name"].tolist()
        st.write(f"• Cluster {cid}: {names}")

st.markdown("---")

# 6. Time‑series viewer for last 48 hours
st.subheader("Gauge Time‑Series")
site_ids = df.site_id.tolist()
sel = st.selectbox(
    "Select a gauge",
    options=site_ids,
    format_func=lambda s: df[df.site_id==s]["name"].iloc[0]
)

conn = get_connection()
ts_df = pd.read_sql_query(
    """
    SELECT timestamp, water_level_ft
    FROM readings
    WHERE site_id = ? AND timestamp >= datetime('now','-48 hours')
    ORDER BY timestamp
    """,
    conn,
    params=(sel,)
)
conn.close()

if ts_df.empty:
    st.warning("No readings in the past 48 hours for this gauge.")
else:
    st.line_chart(ts_df.set_index("timestamp")["water_level_ft"])
    g = df[df.site_id==sel].iloc[0]
    st.write(
        f"**Action Stage:** {g['action_stage_ft']} ft  "
        f"**Flood Stage:** {g['flood_stage_ft']} ft"
    )


if ts_df.empty:
    st.warning("No readings in the past 48 hours for this gauge.")
else:
    st.line_chart(ts_df.set_index("timestamp")["water_level_ft"])
    g = df[df.site_id==sel].iloc[0]
    st.write(f"**Action Stage:** {g['action_stage_ft']} ft  **Flood Stage:** {g['flood_stage_ft']} ft")

