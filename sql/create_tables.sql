CREATE DATABASE IF NOT EXISTS ev_range_test_db;

USE ev_range_test_db;

DROP TABLE IF EXISTS range_tests;

CREATE TABLE range_tests (
    test_id VARCHAR(20) PRIMARY KEY,
    vehicle_model VARCHAR(100),
    test_date DATE,
    city VARCHAR(100),
    temperature_c DECIMAL(5,2),
    tire_type VARCHAR(50),
    test_speed_kmh DECIMAL(6,2),
    battery_capacity_kwh DECIMAL(6,2),
    start_soc_percent DECIMAL(5,2),
    end_soc_percent DECIMAL(5,2),
    distance_km DECIMAL(8,2),
    energy_used_kwh DECIMAL(8,2),
    energy_consumption_kwh_100km DECIMAL(6,2),
    claimed_range_km DECIMAL(8,2),
    actual_range_km DECIMAL(8,2),
    range_error_percent DECIMAL(6,2),
    soc_used_percent DECIMAL(5,2)
);