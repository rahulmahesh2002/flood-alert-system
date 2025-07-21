# flood-alert-system

A simple, real‑time flood‑warning system that:

1. **Pulls live river‑level data** from the USGS every 10 minutes  
2. **Checks** each reading against “watch” and “warning” thresholds  
3. **Groups nearby at‑risk stations** into zones  
4. **Shows** an interactive web map with green/yellow/red markers  
5. **Pops up alerts** and plots 48‑hour water‑level graphs in your browser  

---

## 🚀 Why This Matters

Rivers can rise quickly, and official bulletins sometimes lag by hours. This dashboard gives communities **minutes of extra warning**, so they can stay safe.

---

## 🔧 Tech Stack

- **Python**: logic, data fetching, clustering  
- **Flask + APScheduler**: schedules and runs data collection jobs  
- **MySQL**: stores a full history of readings (append‑only)  
- **pandas**: checks water levels against thresholds  
- **scikit‑learn (DBSCAN)**: groups at‑risk stations into zones  
- **Streamlit + pydeck**: builds the interactive dashboard and map  
- **dotenv**: keeps your database password safe in a `.env` file  

---
