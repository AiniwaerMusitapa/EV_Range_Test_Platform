import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="CAN Signal Ok-To-Go Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. Load data
# --------------------------------------------------
base_dir = Path(__file__).resolve().parents[1]
can_file = base_dir / "data" / "clean" / "can_signal_checked.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(can_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# --------------------------------------------------
# 3. Signal configuration
# --------------------------------------------------
signal_config = {
    "SOC (%)": {
        "column": "soc_percent",
        "threshold": 80,
        "threshold_type": "min",
        "label": "SOC (%)"
    },
    "Battery Voltage (V)": {
        "column": "battery_voltage_v",
        "threshold": 350,
        "threshold_type": "min",
        "label": "Battery Voltage (V)"
    },
    "Motor Temperature (°C)": {
        "column": "motor_temperature_c",
        "threshold": 70,
        "threshold_type": "max",
        "label": "Motor Temperature (°C)"
    },
    "Vehicle Speed (km/h)": {
        "column": "vehicle_speed_kmh",
        "threshold": 10,
        "threshold_type": "max",
        "label": "Vehicle Speed (km/h)"
    }
}

def build_failed_reason_breakdown(dataframe):
    failed = dataframe[dataframe["ok_to_go_status"] == "NOT_OK"].copy()
    reasons = []

    for reason_text in failed["failed_reason"]:
        if pd.isna(reason_text):
            continue

        for reason in str(reason_text).split(";"):
            reason = reason.strip()
            if reason and reason != "Ready for range test":
                reasons.append(reason)

    if not reasons:
        return pd.DataFrame(columns=["failed_reason", "count"])

    reason_df = pd.Series(reasons).value_counts().reset_index()
    reason_df.columns = ["failed_reason", "count"]
    return reason_df

def get_abnormal_points(dataframe, signal_name):
    config = signal_config[signal_name]
    column = config["column"]
    threshold = config["threshold"]
    threshold_type = config["threshold_type"]

    if threshold_type == "min":
        return dataframe[dataframe[column] < threshold].copy()
    else:
        return dataframe[dataframe[column] > threshold].copy()

# --------------------------------------------------
# 4. Sidebar
# --------------------------------------------------
st.sidebar.title("Monitor Control")

vehicle_options = sorted(df["vehicle_model"].unique())
status_options = sorted(df["ok_to_go_status"].unique())

selected_status = st.sidebar.multiselect(
    "Overall Status Filter",
    options=status_options,
    default=status_options
)

monitor_vehicle = st.sidebar.selectbox(
    "Vehicle for Signal Monitor",
    options=vehicle_options,
    index=0
)

selected_signal = st.sidebar.selectbox(
    "Signal to Monitor",
    options=list(signal_config.keys()),
    index=0
)

filtered_df = df[df["ok_to_go_status"].isin(selected_status)].copy()
monitor_df = filtered_df[filtered_df["vehicle_model"] == monitor_vehicle].copy()

if filtered_df.empty or monitor_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --------------------------------------------------
# 5. Header
# --------------------------------------------------
st.title("📡 CAN Signal Ok-To-Go Monitor Prototype")

st.markdown(
    """
    This dashboard simulates a CAN-style vehicle signal monitoring tool for EV range test preparation.  
    It applies **combined trigger conditions** to determine whether each simulated vehicle record is ready for range testing.
    """
)

st.info(
    "This project uses simulated CAN-style signal data for learning and portfolio demonstration purposes."
)

# --------------------------------------------------
# 6. Overall KPI
# --------------------------------------------------
st.subheader("Overall Readiness Summary")

total_records = len(filtered_df)
ok_count = (filtered_df["ok_to_go_status"] == "OK").sum()
not_ok_count = (filtered_df["ok_to_go_status"] == "NOT_OK").sum()
ok_rate = ok_count / total_records * 100

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total CAN Records", total_records)
k2.metric("OK Records", ok_count)
k3.metric("NOT_OK Records", not_ok_count)
k4.metric("Ok-To-Go Rate", f"{ok_rate:.1f}%")

# --------------------------------------------------
# 7. Latest vehicle snapshot
# --------------------------------------------------
st.subheader(f"Latest Signal Snapshot — {monitor_vehicle}")

latest_record = monitor_df.sort_values("timestamp").iloc[-1]

s1, s2, s3, s4, s5 = st.columns(5)

s1.metric("Latest Record", latest_record["record_id"])
s2.metric("SOC", f"{latest_record['soc_percent']:.1f}%")
s3.metric("Battery Voltage", f"{latest_record['battery_voltage_v']:.1f} V")
s4.metric("Vehicle Speed", f"{latest_record['vehicle_speed_kmh']:.1f} km/h")
s5.metric("Status", latest_record["ok_to_go_status"])

if latest_record["ok_to_go_status"] == "OK":
    st.success(f"Latest record `{latest_record['record_id']}` is ready for range testing.")
else:
    st.error(
        f"Latest record `{latest_record['record_id']}` is NOT ready. "
        f"Reason: {latest_record['failed_reason']}"
    )

# --------------------------------------------------
# 8. Trigger logic
# --------------------------------------------------
st.subheader("Ok-To-Go Trigger Logic")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("**SOC Rule**  \nSOC must be at least **80%**.")

with c2:
    st.markdown("**Speed Rule**  \nVehicle speed must be no more than **10 km/h**.")

with c3:
    st.markdown("**Voltage / Temperature**  \nBattery voltage and temperatures must be within limits.")

with c4:
    st.markdown("**Status Signals**  \nGPS OK, doors closed, brake released.")

st.divider()

# --------------------------------------------------
# 9. Status distribution and failed reasons
# --------------------------------------------------
left_col, right_col = st.columns([0.9, 1.1])

with left_col:
    st.subheader("Ok-To-Go Status Distribution")

    status_df = filtered_df["ok_to_go_status"].value_counts().reset_index()
    status_df.columns = ["ok_to_go_status", "count"]

    fig_status = px.pie(
        status_df,
        names="ok_to_go_status",
        values="count",
        hole=0.5,
        title="OK vs NOT_OK Distribution",
        color="ok_to_go_status",
        color_discrete_map={
            "OK": "#27AE60",
            "NOT_OK": "#E82127"
        }
    )

    fig_status.update_layout(height=420)
    st.plotly_chart(fig_status, use_container_width=True)

with right_col:
    st.subheader("Failed Trigger Breakdown")

    reason_df = build_failed_reason_breakdown(filtered_df)

    if reason_df.empty:
        st.success("No failed trigger conditions under the current filters.")
    else:
        fig_reason = px.bar(
            reason_df.head(8),
            x="count",
            y="failed_reason",
            orientation="h",
            text="count",
            title="Top Failed Trigger Conditions",
            labels={
                "count": "Count",
                "failed_reason": "Failed Trigger Condition"
            },
            color_discrete_sequence=["#E82127"]
        )

        fig_reason.update_traces(textposition="outside")
        fig_reason.update_layout(
            height=420,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=20, r=60, t=60, b=40)
        )

        st.plotly_chart(fig_reason, use_container_width=True)

        top_reason = reason_df.iloc[0]
        st.warning(
            f"Most frequent failed trigger: **{top_reason['failed_reason']}** "
            f"({top_reason['count']} records)."
        )

st.divider()

# --------------------------------------------------
# 10. Single-vehicle signal monitor
# --------------------------------------------------
st.subheader(f"Signal Monitor — {monitor_vehicle}")

signal_info = signal_config[selected_signal]
signal_column = signal_info["column"]
threshold = signal_info["threshold"]
threshold_type = signal_info["threshold_type"]
signal_label = signal_info["label"]

abnormal_df = get_abnormal_points(monitor_df, selected_signal)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Selected Signal", selected_signal)
m2.metric("Average Value", f"{monitor_df[signal_column].mean():.1f}")
m3.metric("Threshold", threshold)
m4.metric("Abnormal Points", len(abnormal_df))

fig_signal = px.line(
    monitor_df.sort_values("timestamp"),
    x="timestamp",
    y=signal_column,
    markers=True,
    title=f"{selected_signal} Trend for {monitor_vehicle}",
    labels={
        "timestamp": "Timestamp",
        signal_column: signal_label
    },
    color_discrete_sequence=["#2F80ED"]
)

if threshold_type == "min":
    annotation_text = f"Minimum Threshold: {threshold}"
else:
    annotation_text = f"Maximum Threshold: {threshold}"

fig_signal.add_hline(
    y=threshold,
    line_dash="dash",
    line_color="red",
    annotation_text=annotation_text
)

if not abnormal_df.empty:
    fig_abnormal = px.scatter(
        abnormal_df,
        x="timestamp",
        y=signal_column,
        hover_data=[
            "record_id",
            "vehicle_model",
            "ok_to_go_status",
            "failed_reason"
        ],
        color_discrete_sequence=["#E82127"]
    )

    for trace in fig_abnormal.data:
        trace.name = "Abnormal Point"
        trace.marker.size = 10
        fig_signal.add_trace(trace)

fig_signal.update_layout(
    height=520,
    margin=dict(l=20, r=20, t=70, b=40),
    showlegend=True
)

st.plotly_chart(fig_signal, use_container_width=True)

if abnormal_df.empty:
    st.success(f"No abnormal points detected for **{selected_signal}** on **{monitor_vehicle}**.")
else:
    st.error(
        f"{len(abnormal_df)} abnormal points detected for **{selected_signal}** on **{monitor_vehicle}**."
    )

with st.expander("View Abnormal Signal Points"):
    if abnormal_df.empty:
        st.write("No abnormal signal points.")
    else:
        display_cols = [
            "record_id",
            "timestamp",
            "vehicle_model",
            signal_column,
            "ok_to_go_status",
            "failed_reason"
        ]

        st.dataframe(
            abnormal_df[display_cols].sort_values("timestamp"),
            use_container_width=True
        )

st.divider()

# --------------------------------------------------
# 11. Vehicle-level readiness summary
# --------------------------------------------------
st.subheader("Vehicle-Level Readiness Summary")

vehicle_summary = (
    filtered_df.groupby("vehicle_model")
    .agg(
        total_records=("record_id", "count"),
        ok_records=("ok_to_go_status", lambda x: (x == "OK").sum()),
        not_ok_records=("ok_to_go_status", lambda x: (x == "NOT_OK").sum()),
        avg_soc=("soc_percent", "mean"),
        avg_motor_temp=("motor_temperature_c", "mean"),
        avg_battery_voltage=("battery_voltage_v", "mean"),
        avg_speed=("vehicle_speed_kmh", "mean")
    )
    .reset_index()
)

vehicle_summary["ok_rate_percent"] = (
    vehicle_summary["ok_records"] / vehicle_summary["total_records"] * 100
).round(1)

vehicle_summary["avg_soc"] = vehicle_summary["avg_soc"].round(1)
vehicle_summary["avg_motor_temp"] = vehicle_summary["avg_motor_temp"].round(1)
vehicle_summary["avg_battery_voltage"] = vehicle_summary["avg_battery_voltage"].round(1)
vehicle_summary["avg_speed"] = vehicle_summary["avg_speed"].round(1)

st.dataframe(
    vehicle_summary.sort_values("ok_rate_percent", ascending=False),
    use_container_width=True
)

with st.expander("View Checked CAN Signal Data"):
    st.dataframe(
        filtered_df.sort_values("timestamp"),
        use_container_width=True
    )

st.caption(
    "Built with Python, Pandas, Streamlit, and Plotly. "
    "CAN-style data is simulated for learning and portfolio purposes."
)