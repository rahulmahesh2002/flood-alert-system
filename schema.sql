-- Create the database (if not already created)
CREATE DATABASE IF NOT EXISTS flood_alert;
USE flood_alert;

-- Table 1: Gauge Metadata and Thresholds
CREATE TABLE IF NOT EXISTS gauges (
    site_id           VARCHAR(20) PRIMARY KEY,
    name              VARCHAR(100),
    latitude          DOUBLE,
    longitude         DOUBLE,
    action_stage_ft   FLOAT,
    flood_stage_ft    FLOAT
);

-- Table 2: Water Level Readings
CREATE TABLE IF NOT EXISTS readings (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    site_id           VARCHAR(20),
    timestamp         DATETIME,
    water_level_ft    FLOAT,
    FOREIGN KEY (site_id) REFERENCES gauges(site_id)
);
