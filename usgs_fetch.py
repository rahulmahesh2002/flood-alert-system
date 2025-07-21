import requests
import pandas as pd
from db_config import get_connection

USGS_URL = "https://waterservices.usgs.gov/nwis/iv/"

def fetch_latest_reading(site_id: str):
    """
    Call USGS API for gauge-height (parameterCd=00065).
    Returns (timestamp_iso: str, water_level_ft: float).
    """
    params = {"format": "json", "sites": site_id, "parameterCd": "00065"}
    resp = requests.get(USGS_URL, params=params)
    resp.raise_for_status()
    series = resp.json()["value"]["timeSeries"]
    if not series or not series[0]["values"][0]["value"]:
        raise ValueError(f"No data for site {site_id}")
    latest = series[0]["values"][0]["value"][-1]
    ts = pd.to_datetime(latest["dateTime"]).isoformat()
    lvl = float(latest["value"])
    return ts, lvl

def fetch_and_store_readings():
    """
    Fetch latest reading for each seeded gauge and insert into readings.
    """
    conn = get_connection()
    cur = conn.cursor()
    # get all site_ids
    cur.execute("SELECT site_id FROM gauges;")
    sites = [row["site_id"] for row in cur.fetchall()]
    for site in sites:
        try:
            ts, lvl = fetch_latest_reading(site)
            cur.execute(
                "INSERT INTO readings (site_id, timestamp, water_level_ft) VALUES (?, ?, ?);",
                (site, ts, lvl)
            )
            conn.commit()
        except Exception as e:
            print(f"[fetch error] {site}: {e}")
    conn.close()





"""

import requests  # For making HTTP requests to get data from the USGS website
import pandas as pd  # For handling date and time in a convenient format

# USGS Instantaneous Values Web Service URL
USGS_URL = "https://waterservices.usgs.gov/nwis/iv/"

def fetch_latest_reading(site_id: str):

    Queries USGS for the most recent gauge-height (water level) reading.
    ParameterCd 00065 refers to 'Gage height, feet'.
    
    Returns:
        A tuple with:
        - timestamp (as pandas Timestamp)
        - water_level_ft (as float in feet)
    

    # Define query parameters
    params = {
        "format": "json",        # Ask USGS for JSON formatted response
        "sites": site_id,        # The site ID to query for water data
        "parameterCd": "00065"   # Parameter 00065 = water level in feet (gauge height)
    }

    # Make the GET request to USGS
    resp = requests.get(USGS_URL, params=params)
    
    # If request failed (e.g. 404 or 500), raise an error
    resp.raise_for_status()
    
    # Parse the response JSON into a Python dictionary
    data = resp.json()

    # Navigate to the actual list of data series in the JSON
    series = data["value"]["timeSeries"]
    
    # If the list is empty, it means no data is available for that site
    if not series:
        raise ValueError(f"No data returned for site {site_id}")

    # Get the list of actual recorded values (timestamps and readings)
    values = series[0]["values"][0]["value"]
    
    # If the list of values is empty, no readings are present
    if not values:
        raise ValueError(f"No value entries for site {site_id}")

    # Take the latest (most recent) reading from the values list
    latest = values[-1]

    # Convert the dateTime string into a pandas Timestamp
    timestamp = pd.to_datetime(latest["dateTime"])

    # Convert the water level value (as string) to float
    water_level = float(latest["value"])

    # Return the latest timestamp and corresponding water level
    return timestamp, water_level


"""
