# app.py
# Flask app + APScheduler job to fetch & store readings every 10 minutes

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from usgs_fetch import fetch_latest_reading
from db_config import get_connection
import logging # which is used to record events like errors, warnings, and general info while the program runs.
# logging is used for logging.info,error etc to understand the flow of pgrm
# Basic console logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s") # this will display themsg output in the given format

app = Flask(__name__)

def fetch_and_store():
    conn = get_connection() # This is from bd_config.py
    cursor = conn.cursor()

    # Get all configured gauge IDs
    cursor.execute("SELECT site_id FROM gauges;") # sql query to get the site_id
    sites = [row[0] for row in cursor.fetchall()] # since cursor.fetchall() gets the query result and keep in tuple form, we know tuple carry data like ((data1,)) even if onlyone data eist, so we need to collect row[0] of each row we iterate !
    # now sites contain all the sites in list format

    for site_id in sites:
        try:
            ts, level = fetch_latest_reading(site_id) # returns timestamp, and water level
            logging.info(f"Fetched {level:.2f} ft for site {site_id} @ {ts}")
            # level:2f exist to limit decimals to 2, eg: {level:.2f} → "9.24" 
            # Insert into readings
            cursor.execute(
                "INSERT INTO readings (site_id, timestamp, water_level_ft) VALUES (%s, %s, %s)",
                (site_id, ts.to_pydatetime(), level)
            )
            conn.commit() # saves the changes made to table after executing query
            logging.info(f"Inserted reading for site {site_id}")
        except Exception as e:
            logging.error(f"Error fetching/storing {site_id}: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    # Run once immediately
    fetch_and_store()

    # Schedule every 10 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store, trigger="interval", minutes=10)
    # scheduler has 3 trigger tyes -interval(specific minutes),date - spec date,cron - spec day
    scheduler.start()
    logging.info("Scheduler started: fetching every 10 minutes.")

    # Keep Flask alive (no routes needed)
    app.run(host="0.0.0.0", port=5000)
