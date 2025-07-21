# app.py
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from seed_gauges import seed_gauges
from usgs_fetch import fetch_and_store_readings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Ensure tables exist and gauges are seeded
seed_gauges()

app = Flask(__name__)

def job_fetch():
    try:
        fetch_and_store_readings()
        logging.info("✅ fetch_and_store_readings completed.")
    except Exception as e:
        logging.error(f"❌ Error in fetch_and_store_readings: {e}")

if __name__ == "__main__":
    job_fetch()  # run once at startup

    scheduler = BackgroundScheduler()
    scheduler.add_job(job_fetch, 'interval', minutes=10)
    scheduler.start()
    logging.info("Scheduler started: fetching every 10 minutes.")

    app.run(host="0.0.0.0", port=5000)


