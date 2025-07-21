# usgs_fetch.py
# Fetch the latest instantaneous water‑level reading from USGS

import requests
import pandas as pd

USGS_URL = "https://waterservices.usgs.gov/nwis/iv/"

def fetch_latest_reading(site_id: str):
    """
    Query USGS for the most recent gauge-height (parameterCd=00065).
    Returns a tuple: (timestamp: pd.Timestamp, water_level_ft: float)
    """
    params = {
        "format": "json",
        "sites": site_id,
        "parameterCd": "00065"
    }
    resp = requests.get(USGS_URL, params=params)
    resp.raise_for_status()
    data = resp.json()

    # Navigate JSON to the list of values
    series = data["value"]["timeSeries"]
    if not series:
        raise ValueError(f"No data returned for site {site_id}")

    values = series[0]["values"][0]["value"]
    if not values:
        raise ValueError(f"No value entries for site {site_id}")

    latest = values[-1]
    timestamp = pd.to_datetime(latest["dateTime"])
    water_level = float(latest["value"])
    return timestamp, water_level




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