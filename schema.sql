-- Create gauges table (station metadata & thresholds)
CREATE TABLE IF NOT EXISTS gauges (
    site_id           TEXT PRIMARY KEY,
    name              TEXT,
    latitude          REAL,
    longitude         REAL,
    action_stage_ft   REAL,
    flood_stage_ft    REAL
);

-- Create readings table (append‑only water levels)
CREATE TABLE IF NOT EXISTS readings (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id           TEXT,
    timestamp         TEXT,     -- ISO datetime string
    water_level_ft    REAL,
    FOREIGN KEY (site_id) REFERENCES gauges(site_id)
);

