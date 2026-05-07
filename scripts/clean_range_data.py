import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]

raw_file = base_dir / "data" / "raw" / "range_test_raw.xlsx"
clean_dir = base_dir / "data" / "clean"
clean_dir.mkdir(parents=True, exist_ok=True)

# Read raw Excel file
df = pd.read_excel(raw_file)

print("Raw data shape:", df.shape)
print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Basic data type conversion
df["test_date"] = pd.to_datetime(df["test_date"], errors="coerce")

# Fill missing values
df["temperature_c"] = df["temperature_c"].fillna(df["temperature_c"].median())
df["test_speed_kmh"] = df["test_speed_kmh"].fillna(df["test_speed_kmh"].median())
df["tire_type"] = df["tire_type"].fillna("Unknown")

# Remove duplicate test records if any
df = df.drop_duplicates(subset=["test_id"])

# Recalculate important metrics to make sure values are consistent
df["soc_used_percent"] = df["start_soc_percent"] - df["end_soc_percent"]

df["energy_consumption_kwh_100km"] = (
    df["energy_used_kwh"] / df["distance_km"] * 100
).round(2)

df["range_error_percent"] = (
    (df["actual_range_km"] - df["claimed_range_km"]) / df["claimed_range_km"] * 100
).round(2)

# Basic validation rules
df = df[df["distance_km"] > 0]
df = df[df["battery_capacity_kwh"] > 0]
df = df[df["soc_used_percent"] > 0]

print("\nMissing values after cleaning:")
print(df.isnull().sum())

print("\nClean data shape:", df.shape)
print("\nPreview:")
print(df.head())

output_file = clean_dir / "range_test_clean.csv"
df.to_csv(output_file, index=False)

print(f"\nClean data saved to: {output_file}")