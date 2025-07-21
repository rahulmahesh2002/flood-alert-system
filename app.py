from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from seed_gauges import seed_gauges
from usgs_fetch import fetch_and_store_readings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

# Seed default gauges if needed
seed_gauges()

app = Flask(__name__)

def job_fetch():
    """
    Fetch & store USGS readings for all gauges.
    """
    try:
        fetch_and_store_readings()
        logging.info("✅ fetch_and_store_readings completed.")
    except Exception as e:
        logging.error(f"❌ Error in fetch_and_store_readings: {e}")

if __name__ == "__main__":
    # Run once at startup
    job_fetch()

    # Schedule every 10 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_fetch, 'interval', minutes=10)
    scheduler.start()
    logging.info("Scheduler started: fetching every 10 minutes.")

    # Keep the Flask app alive (no HTTP endpoints needed)
    app.run(host="0.0.0.0", port=5000)

