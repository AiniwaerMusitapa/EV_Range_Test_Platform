USE ev_range_test_db;

-- 1. Check total records
SELECT COUNT(*) AS total_records
FROM range_tests;

-- 2. Test record count by vehicle model
SELECT
    vehicle_model,
    COUNT(*) AS test_count
FROM range_tests
GROUP BY vehicle_model
ORDER BY test_count DESC;

-- 3. Average energy consumption by vehicle model
SELECT
    vehicle_model,
    ROUND(AVG(energy_consumption_kwh_100km), 2) AS avg_energy_consumption
FROM range_tests
GROUP BY vehicle_model
ORDER BY avg_energy_consumption ASC;

-- 4. Actual range vs claimed range by vehicle model
SELECT
    vehicle_model,
    ROUND(AVG(actual_range_km), 2) AS avg_actual_range,
    ROUND(AVG(claimed_range_km), 2) AS avg_claimed_range,
    ROUND(AVG(actual_range_km - claimed_range_km), 2) AS avg_range_gap_km,
    ROUND(AVG(range_error_percent), 2) AS avg_range_error_percent
FROM range_tests
GROUP BY vehicle_model
ORDER BY avg_range_error_percent ASC;

-- 5. Average energy consumption by speed band
SELECT
    CASE
        WHEN test_speed_kmh >= 60 AND test_speed_kmh < 70 THEN '60-70'
        WHEN test_speed_kmh >= 70 AND test_speed_kmh < 80 THEN '70-80'
        WHEN test_speed_kmh >= 80 AND test_speed_kmh < 90 THEN '80-90'
        WHEN test_speed_kmh >= 90 AND test_speed_kmh < 100 THEN '90-100'
        WHEN test_speed_kmh >= 100 AND test_speed_kmh < 110 THEN '100-110'
        WHEN test_speed_kmh >= 110 AND test_speed_kmh <= 120 THEN '110-120'
        ELSE 'Other'
    END AS speed_band,
    ROUND(AVG(energy_consumption_kwh_100km), 2) AS avg_energy_consumption,
    COUNT(*) AS test_count
FROM range_tests
GROUP BY speed_band
ORDER BY
    CASE speed_band
        WHEN '60-70' THEN 1
        WHEN '70-80' THEN 2
        WHEN '80-90' THEN 3
        WHEN '90-100' THEN 4
        WHEN '100-110' THEN 5
        WHEN '110-120' THEN 6
        ELSE 7
    END;

-- 6. Average energy consumption by temperature band
SELECT
    CASE
        WHEN temperature_c < 0 THEN '<0'
        WHEN temperature_c >= 0 AND temperature_c < 10 THEN '0-10'
        WHEN temperature_c >= 10 AND temperature_c < 20 THEN '10-20'
        WHEN temperature_c >= 20 AND temperature_c < 30 THEN '20-30'
        WHEN temperature_c >= 30 THEN '>30'
        ELSE 'Unknown'
    END AS temperature_band,
    ROUND(AVG(energy_consumption_kwh_100km), 2) AS avg_energy_consumption,
    COUNT(*) AS test_count
FROM range_tests
GROUP BY temperature_band
ORDER BY
    CASE temperature_band
        WHEN '<0' THEN 1
        WHEN '0-10' THEN 2
        WHEN '10-20' THEN 3
        WHEN '20-30' THEN 4
        WHEN '>30' THEN 5
        ELSE 6
    END;

-- 7. Top 10 highest energy consumption records
SELECT
    test_id,
    vehicle_model,
    city,
    temperature_c,
    test_speed_kmh,
    tire_type,
    energy_consumption_kwh_100km
FROM range_tests
ORDER BY energy_consumption_kwh_100km DESC
LIMIT 10;