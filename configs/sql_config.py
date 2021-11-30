CREATE_DATABASE = "CREATE DATABASE IF NOT EXISTS web_scraper"
USE = "USE web_scraper"

CREATE_EARTHQUAKES = "CREATE TABLE IF NOT EXISTS earthquake_events (" \
                   "id INT NOT NULL AUTO_INCREMENT," \
                   "event_key VARCHAR(32) UNIQUE," \
                   "magnitude FLOAT," \
                   "magnitude_uncertainty FLOAT," \
                   "magnitude_units VARCHAR(8)," \
                   "location VARCHAR(45)," \
                   "location_uncertainty_km FLOAT," \
                   "depth_km FLOAT," \
                   "depth_uncertainty_km FLOAT," \
                   "origin_time DATETIME," \
                   "num_of_stations INT," \
                   "num_of_phases INT," \
                   "minimum_distance_km FLOAT," \
                   "travel_time_residual_sec INT," \
                   "azimuthal_gap_deg INT," \
                   "fe_region_id INT," \
                   "review_status_id INT," \
                   "catalog_id INT," \
                   "contributor_id INT," \
                   "PRIMARY KEY (id)," \
                   "FOREIGN KEY (fe_region_id) REFERENCES fe_region(id) ON DELETE CASCADE," \
                   "FOREIGN KEY (review_status_id) REFERENCES review_status(id) ON DELETE CASCADE," \
                   "FOREIGN KEY (catalog_id) REFERENCES catalog(id) ON DELETE CASCADE," \
                   "FOREIGN KEY (contributor_id) REFERENCES contributor(id) ON DELETE CASCADE" \
                   ")"

CREATE_REVIEW = "CREATE TABLE IF NOT EXISTS review_status (" \
                   "id INT NOT NULL AUTO_INCREMENT," \
                   "review_status VARCHAR(15) UNIQUE," \
                   "PRIMARY KEY (id)" \
                   ")"

CREATE_CONTRIBUTOR = "CREATE TABLE IF NOT EXISTS contributor (" \
                   "id INT NOT NULL AUTO_INCREMENT," \
                   "contributor VARCHAR(15) UNIQUE," \
                   "PRIMARY KEY (id)" \
                   ")"

CREATE_FE_REGION = "CREATE TABLE IF NOT EXISTS fe_region (" \
                   "id INT NOT NULL AUTO_INCREMENT," \
                   "fe_region VARCHAR(64) UNIQUE," \
                   "PRIMARY KEY (id)" \
                   ")"

CREATE_CATALOG = "CREATE TABLE IF NOT EXISTS catalog (" \
                   "id INT NOT NULL AUTO_INCREMENT," \
                   "catalog VARCHAR(15) UNIQUE," \
                   "PRIMARY KEY (id)" \
                   ")"

INSERT_STR = "INSERT IGNORE INTO {table} ({column}) VALUES ('{value}')"

SELECT_ID = "SELECT id FROM {table} WHERE {field}='{value}'"

SELECT_EVENT_KEY_BY_TIME = 'SELECT event_key FROM earthquake_events WHERE origin_time > "{time}"'

TIME_DELTA = 2

HOST = 'localhost'

