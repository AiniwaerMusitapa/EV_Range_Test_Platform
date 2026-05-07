import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Set project paths
# --------------------------------------------------
base_dir = Path(__file__).resolve().parents[1]
raw_file = base_dir / "data" / "raw" / "can_signal_raw.csv"
clean_dir = base_dir / "data" / "clean"
clean_dir.mkdir(parents=True, exist_ok=True)

output_file = clean_dir / "can_signal_checked.csv"

# --------------------------------------------------
# 2. Load CAN signal data
# --------------------------------------------------
df = pd.read_csv(raw_file)

print("CAN signal data loaded.")
print("Data shape:", df.shape)

# --------------------------------------------------
# 3. Define Ok-To-Go checking function
# --------------------------------------------------
def check_ok_to_go(row):
    failed_reasons = []

    # Rule 1: SOC should be high enough for range test
    if row["soc_percent"] < 80:
        failed_reasons.append("SOC below 80%")

    # Rule 2: Vehicle should be stationary or near stationary before test
    if row["vehicle_speed_kmh"] > 10:
        failed_reasons.append("Vehicle speed above 10 km/h")

    # Rule 3: Battery voltage should be within acceptable range
    if row["battery_voltage_v"] < 350:
        failed_reasons.append("Battery voltage too low")

    # Rule 4: Motor temperature should not be too high
    if row["motor_temperature_c"] > 70:
        failed_reasons.append("Motor temperature too high")

    # Rule 5: Battery temperature should be within a safe preparation range
    if row["battery_temperature_c"] < 10 or row["battery_temperature_c"] > 45:
        failed_reasons.append("Battery temperature out of range")

    # Rule 6: GPS signal should be available
    if row["gps_signal_status"] != "OK":
        failed_reasons.append("GPS signal not OK")

    # Rule 7: Doors should be closed
    if row["door_status"] != "CLOSED":
        failed_reasons.append("Door not closed")

    # Rule 8: Brake should be released for Ok-To-Go state
    if row["brake_pedal_status"] != "RELEASED":
        failed_reasons.append("Brake pedal pressed")

    if len(failed_reasons) == 0:
        return "OK", "Ready for range test"
    else:
        return "NOT_OK", "; ".join(failed_reasons)

# --------------------------------------------------
# 4. Apply Ok-To-Go logic
# --------------------------------------------------
results = df.apply(check_ok_to_go, axis=1)

df["ok_to_go_status"] = results.apply(lambda x: x[0])
df["failed_reason"] = results.apply(lambda x: x[1])

# --------------------------------------------------
# 5. Export checked data
# --------------------------------------------------
df.to_csv(output_file, index=False)

# --------------------------------------------------
# 6. Print summary
# --------------------------------------------------
print("\nOk-To-Go check completed.")
print("Output file:", output_file)

print("\nStatus count:")
print(df["ok_to_go_status"].value_counts())

print("\nTop failed reasons:")
print(
    df[df["ok_to_go_status"] == "NOT_OK"]["failed_reason"]
    .value_counts()
    .head(10)
)

print("\nPreview:")
print(df.head())