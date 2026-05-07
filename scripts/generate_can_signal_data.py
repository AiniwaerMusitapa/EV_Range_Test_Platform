import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------
# 1. Set project paths
# --------------------------------------------------
base_dir = Path(__file__).resolve().parents[1]
raw_dir = base_dir / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

output_file = raw_dir / "can_signal_raw.csv"

# --------------------------------------------------
# 2. Generate simulated CAN-style signal data
# --------------------------------------------------
np.random.seed(42)

vehicle_models = [
    "Tesla Model 3",
    "Tesla Model Y",
    "BYD Seal",
    "BYD Atto 3",
    "NIO ET5",
    "XPeng P7",
    "Zeekr 001"
]

rows = []

for i in range(200):
    vehicle_model = np.random.choice(vehicle_models)

    timestamp = pd.Timestamp("2026-04-01 08:00:00") + pd.Timedelta(seconds=i * 5)

    # Most test preparation records are low-speed or stationary
    vehicle_speed_kmh = round(np.random.normal(3, 2), 1)
    vehicle_speed_kmh = max(0, vehicle_speed_kmh)

    soc_percent = round(np.random.normal(88, 6), 1)
    soc_percent = min(max(soc_percent, 40), 100)

    battery_voltage_v = round(np.random.normal(385, 12), 1)
    battery_current_a = round(np.random.normal(8, 5), 1)

    motor_temperature_c = round(np.random.normal(45, 8), 1)
    battery_temperature_c = round(np.random.normal(28, 5), 1)

    gps_signal_status = np.random.choice(
        ["OK", "WEAK", "LOST"],
        p=[0.88, 0.09, 0.03]
    )

    door_status = np.random.choice(
        ["CLOSED", "OPEN"],
        p=[0.94, 0.06]
    )

    brake_pedal_status = np.random.choice(
        ["RELEASED", "PRESSED"],
        p=[0.85, 0.15]
    )

    hvac_status = np.random.choice(
        ["OFF", "ON"],
        p=[0.7, 0.3]
    )

    # Add a few intentional abnormal cases
    if i in [25, 80, 140]:
        soc_percent = round(np.random.uniform(45, 65), 1)

    if i in [40, 120]:
        gps_signal_status = "LOST"

    if i in [60, 150]:
        door_status = "OPEN"

    if i in [95, 160]:
        motor_temperature_c = round(np.random.uniform(75, 90), 1)

    if i in [110, 170]:
        battery_voltage_v = round(np.random.uniform(310, 330), 1)

    rows.append({
        "record_id": f"CAN{i+1:04d}",
        "timestamp": timestamp,
        "vehicle_model": vehicle_model,
        "vehicle_speed_kmh": vehicle_speed_kmh,
        "soc_percent": soc_percent,
        "battery_voltage_v": battery_voltage_v,
        "battery_current_a": battery_current_a,
        "motor_temperature_c": motor_temperature_c,
        "battery_temperature_c": battery_temperature_c,
        "gps_signal_status": gps_signal_status,
        "door_status": door_status,
        "brake_pedal_status": brake_pedal_status,
        "hvac_status": hvac_status
    })

df = pd.DataFrame(rows)

df.to_csv(output_file, index=False)

print("Simulated CAN signal data generated.")
print("Data shape:", df.shape)
print("Output file:", output_file)
print(df.head())