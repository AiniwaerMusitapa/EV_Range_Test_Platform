import pandas as pd
import numpy as np
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
raw_dir = base_dir / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

vehicle_specs = {
    "Tesla Model 3": {"battery": 60, "base_consumption": 13.2, "claimed_range": 606},
    "Tesla Model Y": {"battery": 75, "base_consumption": 15.0, "claimed_range": 688},
    "BYD Seal": {"battery": 82, "base_consumption": 14.5, "claimed_range": 700},
    "BYD Atto 3": {"battery": 60, "base_consumption": 15.2, "claimed_range": 510},
    "NIO ET5": {"battery": 75, "base_consumption": 14.8, "claimed_range": 560},
    "XPeng P7": {"battery": 80, "base_consumption": 14.3, "claimed_range": 702},
    "Zeekr 001": {"battery": 100, "base_consumption": 16.0, "claimed_range": 741},
}

cities = ["Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Hangzhou"]
tire_types = ["Summer", "All-season", "Eco"]

rows = []

for i in range(160):
    model = np.random.choice(list(vehicle_specs.keys()))
    spec = vehicle_specs[model]

    city = np.random.choice(cities)
    tire_type = np.random.choice(tire_types)

    temperature = round(np.random.uniform(-5, 38), 1)
    test_speed = round(np.random.uniform(60, 120), 1)

    battery_capacity = round(
        np.random.normal(spec["battery"], 2.5),
        1
    )

    start_soc = round(np.random.uniform(88, 100), 1)
    end_soc = round(np.random.uniform(8, 20), 1)
    soc_used = start_soc - end_soc

    base_consumption = spec["base_consumption"]

    # Speed impact: higher speed increases consumption
    speed_penalty = max(0, test_speed - 80) * 0.06

    # Temperature impact: cold and very hot conditions increase consumption
    cold_penalty = max(0, 10 - temperature) * 0.10
    hot_penalty = max(0, temperature - 30) * 0.06

    # Tire impact
    if tire_type == "Eco":
        tire_penalty = -0.4
    elif tire_type == "All-season":
        tire_penalty = 0.2
    else:
        tire_penalty = 0.0

    # Random test noise
    noise = np.random.normal(0, 0.5)

    energy_consumption = (
        base_consumption
        + speed_penalty
        + cold_penalty
        + hot_penalty
        + tire_penalty
        + noise
    )

    energy_consumption = max(8, energy_consumption)
    energy_consumption = round(energy_consumption, 2)

    usable_energy = battery_capacity * (soc_used / 100)

    distance_km = round(
        usable_energy / energy_consumption * 100,
        1
    )

    energy_used = round(usable_energy, 2)

    actual_range = round(
        battery_capacity / energy_consumption * 100,
        1
    )

    # Claimed range is usually more optimistic than simulated actual range
    claimed_range = round(
        spec["claimed_range"] * np.random.normal(1.0, 0.03),
        1
    )

    range_error_percent = round(
        (actual_range - claimed_range) / claimed_range * 100,
        2
    )

    rows.append({
        "test_id": f"T{i+1:04d}",
        "vehicle_model": model,
        "test_date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=np.random.randint(0, 90)),
        "city": city,
        "temperature_c": temperature,
        "tire_type": tire_type,
        "test_speed_kmh": test_speed,
        "battery_capacity_kwh": battery_capacity,
        "start_soc_percent": start_soc,
        "end_soc_percent": end_soc,
        "distance_km": distance_km,
        "energy_used_kwh": energy_used,
        "energy_consumption_kwh_100km": energy_consumption,
        "claimed_range_km": claimed_range,
        "actual_range_km": actual_range,
        "range_error_percent": range_error_percent
    })

df = pd.DataFrame(rows)

# Add a few missing values for cleaning practice
df.loc[5, "temperature_c"] = np.nan
df.loc[12, "tire_type"] = np.nan
df.loc[25, "test_speed_kmh"] = np.nan

output_path = raw_dir / "range_test_raw.xlsx"
df.to_excel(output_path, index=False)

print(f"Sample raw data created: {output_path}")
print(df.head())