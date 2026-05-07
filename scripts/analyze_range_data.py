import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# 1. Set project paths
# --------------------------------------------------
base_dir = Path(__file__).resolve().parents[1]

clean_file = base_dir / "data" / "clean" / "range_test_clean.csv"
output_dir = base_dir / "outputs"
output_dir.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Load cleaned data
# --------------------------------------------------
df = pd.read_csv(clean_file)

print("Clean data loaded successfully.")
print("Data shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

# --------------------------------------------------
# 3. Basic overview
# --------------------------------------------------
print("\nBasic statistics:")
print(df.describe())

print("\nNumber of test records by vehicle model:")
print(df["vehicle_model"].value_counts())

# --------------------------------------------------
# 4. Average energy consumption by vehicle model
# --------------------------------------------------
avg_consumption = (
    df.groupby("vehicle_model")["energy_consumption_kwh_100km"]
    .mean()
    .round(2)
    .reset_index()
    .sort_values("energy_consumption_kwh_100km")
)

print("\nAverage energy consumption by model:")
print(avg_consumption)

avg_consumption.to_csv(
    output_dir / "avg_consumption_by_model.csv",
    index=False
)

plt.figure(figsize=(10, 6))

bars = plt.barh(
    avg_consumption["vehicle_model"],
    avg_consumption["energy_consumption_kwh_100km"],
    color="steelblue",
    edgecolor="black",
    alpha=0.85
)

plt.gca().invert_yaxis()

plt.title("Average Energy Consumption by Vehicle Model")
plt.xlabel("Energy Consumption (kWh/100km)")
plt.ylabel("Vehicle Model")

for bar in bars:
    width = bar.get_width()
    plt.text(
        width + 0.1,
        bar.get_y() + bar.get_height() / 2,
        f"{width:.2f}",
        va="center"
    )

plt.tight_layout()
plt.savefig(output_dir / "avg_consumption_by_model_barh.png", dpi=300)
plt.close()

# --------------------------------------------------
# 5. Actual range vs claimed range by vehicle model
# --------------------------------------------------
plt.figure(figsize=(10, 6))

models = df["vehicle_model"].unique()

for model in models:
    model_data = df[df["vehicle_model"] == model]
    plt.scatter(
        model_data["claimed_range_km"],
        model_data["actual_range_km"],
        label=model,
        alpha=0.7
    )

# Add y = x reference line
min_range = min(df["claimed_range_km"].min(), df["actual_range_km"].min())
max_range = max(df["claimed_range_km"].max(), df["actual_range_km"].max())

plt.plot(
    [min_range, max_range],
    [min_range, max_range],
    linestyle="--",
    color="black",
    label="Actual = Claimed"
)

plt.title("Actual Range vs Claimed Range by Vehicle Model")
plt.xlabel("Claimed Range (km)")
plt.ylabel("Actual Range (km)")
plt.legend()
plt.tight_layout()
plt.savefig(output_dir / "actual_vs_claimed_range_by_model.png", dpi=300)
plt.close()

# --------------------------------------------------
# 6. Temperature impact on energy consumption
# --------------------------------------------------
plt.figure(figsize=(10, 6))

models = df["vehicle_model"].unique()

for model in models:
    model_data = df[df["vehicle_model"] == model]
    plt.scatter(
        model_data["temperature_c"],
        model_data["energy_consumption_kwh_100km"],
        label=model,
        alpha=0.7
    )

plt.title("Temperature vs Energy Consumption by Vehicle Model")
plt.xlabel("Temperature (°C)")
plt.ylabel("Energy Consumption (kWh/100km)")
plt.legend()
plt.tight_layout()
plt.savefig(output_dir / "temperature_vs_consumption_by_model.png", dpi=300)
plt.close()

# --------------------------------------------------
# 7. Speed impact on energy consumption
# --------------------------------------------------
plt.figure(figsize=(10, 6))

models = df["vehicle_model"].unique()

for model in models:
    model_data = df[df["vehicle_model"] == model]
    plt.scatter(
        model_data["test_speed_kmh"],
        model_data["energy_consumption_kwh_100km"],
        label=model,
        alpha=0.7
    )

plt.title("Test Speed vs Energy Consumption by Vehicle Model")
plt.xlabel("Test Speed (km/h)")
plt.ylabel("Energy Consumption (kWh/100km)")
plt.legend()
plt.tight_layout()
plt.savefig(output_dir / "speed_vs_consumption_by_model.png", dpi=300)
plt.close()

# --------------------------------------------------
# 8. Speed band
# --------------------------------------------------
df["speed_band"] = pd.cut(
    df["test_speed_kmh"],
    bins=[60, 70, 80, 90, 100, 110, 120],
    labels=["60-70", "70-80", "80-90", "90-100", "100-110", "110-120"],
    include_lowest=True
)

speed_band_consumption = (
    df.groupby("speed_band", observed=False)["energy_consumption_kwh_100km"]
    .mean()
    .round(2)
    .reset_index()
)

plt.figure(figsize=(9, 6))

bars = plt.bar(
    speed_band_consumption["speed_band"],
    speed_band_consumption["energy_consumption_kwh_100km"],
    edgecolor="black",
    alpha=0.85
)

plt.title("Average Energy Consumption by Speed Band")
plt.xlabel("Test Speed Band (km/h)")
plt.ylabel("Average Energy Consumption (kWh/100km)")
plt.grid(axis="y", alpha=0.3)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.05,
        f"{height:.2f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()
plt.savefig(output_dir / "avg_consumption_by_speed_band.png", dpi=300)
plt.close()

# --------------------------------------------------
# 9. Temperature band
# --------------------------------------------------
df["temperature_band"] = pd.cut(
    df["temperature_c"],
    bins=[-10, 0, 10, 20, 30, 40],
    labels=["<0", "0-10", "10-20", "20-30", ">30"],
    include_lowest=True
)

temp_band_consumption = (
    df.groupby("temperature_band", observed=False)["energy_consumption_kwh_100km"]
    .mean()
    .round(2)
    .reset_index()
)

plt.figure(figsize=(9, 6))

bars = plt.bar(
    temp_band_consumption["temperature_band"],
    temp_band_consumption["energy_consumption_kwh_100km"],
    edgecolor="black",
    alpha=0.85
)

plt.title("Average Energy Consumption by Temperature Band")
plt.xlabel("Temperature Band (°C)")
plt.ylabel("Average Energy Consumption (kWh/100km)")
plt.grid(axis="y", alpha=0.3)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.05,
        f"{height:.2f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()
plt.savefig(output_dir / "avg_consumption_by_temperature_band.png", dpi=300)
plt.close()

# --------------------------------------------------
# 10. Simple insights
# --------------------------------------------------
best_efficiency = avg_consumption.iloc[0]
worst_efficiency = avg_consumption.iloc[-1]

print("\nSimple insights:")
print(
    f"Most efficient model in this simulated dataset: "
    f"{best_efficiency['vehicle_model']} "
    f"({best_efficiency['energy_consumption_kwh_100km']} kWh/100km)"
)

print(
    f"Highest consumption model in this simulated dataset: "
    f"{worst_efficiency['vehicle_model']} "
    f"({worst_efficiency['energy_consumption_kwh_100km']} kWh/100km)"
)

print("\nAnalysis completed. Output files saved to:")
print(output_dir)

