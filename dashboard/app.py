import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="EV Range Test Data Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# 2. Load data
# --------------------------------------------------
base_dir = Path(__file__).resolve().parents[1]
clean_file = base_dir / "data" / "clean" / "range_test_clean.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(clean_file)
    df["test_date"] = pd.to_datetime(df["test_date"])
    return df


df = load_data()

# --------------------------------------------------
# 3. Sidebar filters
# --------------------------------------------------
st.sidebar.title("Filters")

vehicle_options = sorted(df["vehicle_model"].unique())
city_options = sorted(df["city"].unique())
tire_options = sorted(df["tire_type"].unique())

selected_models = st.sidebar.multiselect(
    "Vehicle Model",
    options=vehicle_options,
    default=vehicle_options
)

selected_cities = st.sidebar.multiselect(
    "City",
    options=city_options,
    default=city_options
)

selected_tires = st.sidebar.multiselect(
    "Tire Type",
    options=tire_options,
    default=tire_options
)

filtered_df = df[
    (df["vehicle_model"].isin(selected_models)) &
    (df["city"].isin(selected_cities)) &
    (df["tire_type"].isin(selected_tires))
].copy()

# Avoid empty-filter crashes
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust the sidebar filters.")
    st.stop()

# --------------------------------------------------
# 4. Header section
# --------------------------------------------------
st.title("🚗 EV Range Test Data Platform")

st.markdown(
    """
    A prototype dashboard for simulated EV range test data analysis.  
    This project demonstrates a complete workflow from **data generation**, **data cleaning**, 
    **metric calculation**, **MySQL-ready data preparation**, and **interactive visualization**.
    """
)

st.info(
    "Note: This dashboard uses simulated EV range test data for learning and demonstration purposes. "
    "The purpose is to demonstrate the analysis workflow, not to make real-world claims about specific vehicles."
)

# --------------------------------------------------
# 5. KPI summary
# --------------------------------------------------
st.subheader("Overall Summary")

total_tests = len(filtered_df)
avg_consumption = filtered_df["energy_consumption_kwh_100km"].mean()
avg_actual_range = filtered_df["actual_range_km"].mean()
avg_claimed_range = filtered_df["claimed_range_km"].mean()
avg_range_error = filtered_df["range_error_percent"].mean()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Test Records", f"{total_tests}")
col2.metric("Avg Energy Consumption", f"{avg_consumption:.2f} kWh/100km")
col3.metric("Avg Actual Range", f"{avg_actual_range:.1f} km")
col4.metric("Avg Claimed Range", f"{avg_claimed_range:.1f} km")
col5.metric("Avg Range Error", f"{avg_range_error:.2f}%")

# --------------------------------------------------
# 6. Project highlights
# --------------------------------------------------
st.subheader("Project Highlights")

h1, h2, h3, h4 = st.columns(4)

with h1:
    st.markdown(
        """
        **Data Pipeline**  
        Raw Excel / CSV data → cleaning → metric calculation → SQL-ready dataset
        """
    )

with h2:
    st.markdown(
        """
        **Database Ready**  
        Cleaned range test records can be loaded into MySQL for structured analysis
        """
    )

with h3:
    st.markdown(
        """
        **Interactive Analysis**  
        Filter by vehicle model, city, and tire type
        """
    )

with h4:
    st.markdown(
        """
        **Range Insights**  
        Analyze energy consumption, actual range, claimed range, and range error
        """
    )

st.divider()

# --------------------------------------------------
# 7. Data preparation for charts
# --------------------------------------------------
model_consumption = (
    filtered_df.groupby("vehicle_model", as_index=False)["energy_consumption_kwh_100km"]
    .mean()
    .round(2)
    .sort_values("energy_consumption_kwh_100km", ascending=True)
)

range_error_df = (
    filtered_df.groupby("vehicle_model", as_index=False)["range_error_percent"]
    .mean()
    .round(2)
    .sort_values("range_error_percent", ascending=True)
)

range_summary = (
    filtered_df.groupby("vehicle_model", as_index=False)[
        ["actual_range_km", "claimed_range_km", "range_error_percent"]
    ]
    .mean()
    .round(2)
)

filtered_df["speed_band"] = pd.cut(
    filtered_df["test_speed_kmh"],
    bins=[60, 70, 80, 90, 100, 110, 120],
    labels=["60-70", "70-80", "80-90", "90-100", "100-110", "110-120"],
    include_lowest=True
)

speed_band_df = (
    filtered_df.groupby("speed_band", observed=False, as_index=False)["energy_consumption_kwh_100km"]
    .mean()
    .round(2)
)

filtered_df["temperature_band"] = pd.cut(
    filtered_df["temperature_c"],
    bins=[-10, 0, 10, 20, 30, 40],
    labels=["<0", "0-10", "10-20", "20-30", ">30"],
    include_lowest=True
)

temp_band_df = (
    filtered_df.groupby("temperature_band", observed=False, as_index=False)["energy_consumption_kwh_100km"]
    .mean()
    .round(2)
)

# --------------------------------------------------
# 8. Row 1: vehicle efficiency + range error
# --------------------------------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Vehicle Energy Efficiency")

    fig_consumption = px.bar(
        model_consumption,
        x="energy_consumption_kwh_100km",
        y="vehicle_model",
        orientation="h",
        text="energy_consumption_kwh_100km",
        title="Average Energy Consumption by Vehicle Model",
        labels={
            "energy_consumption_kwh_100km": "Energy Consumption (kWh/100km)",
            "vehicle_model": "Vehicle Model"
        },
        color_discrete_sequence=["#2F80ED"]
    )

    fig_consumption.update_traces(textposition="outside")
    fig_consumption.update_layout(
        height=420,
        yaxis={
            "categoryorder": "array",
            "categoryarray": model_consumption["vehicle_model"].tolist()
        },
        margin=dict(l=20, r=60, t=60, b=40)
    )

    st.plotly_chart(fig_consumption, use_container_width=True)

    best_model = model_consumption.iloc[0]
    worst_model = model_consumption.iloc[-1]

    st.success(
        f"Insight: In this simulated dataset, **{best_model['vehicle_model']}** has the lowest "
        f"average energy consumption at **{best_model['energy_consumption_kwh_100km']} kWh/100km**, "
        f"while **{worst_model['vehicle_model']}** has the highest."
    )

with right_col:
    st.subheader("Range Error Comparison")

    fig_error = px.bar(
        range_error_df,
        x="range_error_percent",
        y="vehicle_model",
        orientation="h",
        text="range_error_percent",
        title="Average Range Error by Vehicle Model",
        labels={
            "range_error_percent": "Range Error (%)",
            "vehicle_model": "Vehicle Model"
        },
        color_discrete_sequence=["#E82127"]
    )

    fig_error.update_traces(textposition="outside")
    fig_error.update_layout(
        height=420,
        yaxis={
            "categoryorder": "array",
            "categoryarray": range_error_df["vehicle_model"].tolist()
        },
        margin=dict(l=20, r=60, t=60, b=40)
    )

    st.plotly_chart(fig_error, use_container_width=True)

    lowest_error = range_error_df.iloc[-1]
    highest_error = range_error_df.iloc[0]

    st.warning(
        f"Insight: **{highest_error['vehicle_model']}** shows the largest negative average range error "
        f"at **{highest_error['range_error_percent']}%**, while **{lowest_error['vehicle_model']}** "
        f"is closest to its claimed range in this simulated dataset."
    )

st.divider()

# --------------------------------------------------
# 9. Row 2: actual vs claimed + condition analysis
# --------------------------------------------------
left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader("Actual Range vs Claimed Range")

    fig_range = px.scatter(
        filtered_df,
        x="claimed_range_km",
        y="actual_range_km",
        color="vehicle_model",
        hover_data=[
            "test_id",
            "city",
            "temperature_c",
            "test_speed_kmh",
            "tire_type",
            "energy_consumption_kwh_100km",
            "range_error_percent"
        ],
        title="Actual Range vs Claimed Range by Vehicle Model",
        labels={
            "claimed_range_km": "Claimed Range (km)",
            "actual_range_km": "Actual Range (km)",
            "vehicle_model": "Vehicle Model"
        },
    )

    min_range = min(
        filtered_df["claimed_range_km"].min(),
        filtered_df["actual_range_km"].min()
    )
    max_range = max(
        filtered_df["claimed_range_km"].max(),
        filtered_df["actual_range_km"].max()
    )

    fig_range.add_shape(
        type="line",
        x0=min_range,
        y0=min_range,
        x1=max_range,
        y1=max_range,
        line=dict(dash="dash", color="black", width=2)
    )

    fig_range.update_layout(
        height=520,
        margin=dict(l=20, r=20, t=60, b=40),
        legend_title_text="Vehicle Model"
    )

    st.plotly_chart(fig_range, use_container_width=True)

    st.info(
        "Insight: The dashed line represents Actual Range = Claimed Range. "
        "Points below the line indicate that the simulated actual range is lower than the claimed range."
    )

with right_col:
    st.subheader("Test Condition Impact")

    tab_speed, tab_temp = st.tabs(["Speed Band", "Temperature Band"])

    with tab_speed:
        fig_speed = px.bar(
            speed_band_df,
            x="speed_band",
            y="energy_consumption_kwh_100km",
            text="energy_consumption_kwh_100km",
            title="Average Energy Consumption by Speed Band",
            labels={
                "speed_band": "Speed Band (km/h)",
                "energy_consumption_kwh_100km": "Energy Consumption (kWh/100km)"
            },
            color_discrete_sequence=["#27AE60"]
        )

        fig_speed.update_traces(textposition="outside")
        fig_speed.update_layout(
            height=420,
            margin=dict(l=20, r=20, t=60, b=40)
        )

        st.plotly_chart(fig_speed, use_container_width=True)

        st.success(
            "Insight: Higher speed bands generally show higher average energy consumption "
            "in the simulated test data."
        )

    with tab_temp:
        fig_temp = px.bar(
            temp_band_df,
            x="temperature_band",
            y="energy_consumption_kwh_100km",
            text="energy_consumption_kwh_100km",
            title="Average Energy Consumption by Temperature Band",
            labels={
                "temperature_band": "Temperature Band (°C)",
                "energy_consumption_kwh_100km": "Energy Consumption (kWh/100km)"
            },
            color_discrete_sequence=["#9B51E0"]
        )

        fig_temp.update_traces(textposition="outside")
        fig_temp.update_layout(
            height=420,
            margin=dict(l=20, r=20, t=60, b=40)
        )

        st.plotly_chart(fig_temp, use_container_width=True)

        st.success(
            "Insight: Low-temperature conditions show higher average energy consumption "
            "in the simulated dataset."
        )

st.divider()

# --------------------------------------------------
# 10. Range summary table
# --------------------------------------------------
st.subheader("Vehicle-Level Range Summary")

st.dataframe(
    range_summary.sort_values("range_error_percent"),
    use_container_width=True
)

# --------------------------------------------------
# 11. Detailed data table
# --------------------------------------------------
with st.expander("View Filtered Test Data"):
    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# --------------------------------------------------
# 12. Footer
# --------------------------------------------------
st.caption(
    "Built with Python, Pandas, Streamlit, and Plotly. "
    "Data is simulated for portfolio and learning purposes."
)