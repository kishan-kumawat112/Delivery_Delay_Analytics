
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Delivery Delay Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# 2. PROFESSIONAL DASHBOARD STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4F7FB;
        color: #172B4D;
    }

    h1, h2, h3 {
        color: #17365D !important;
    }

    p, label, .stMarkdown {
        color: #243B53;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #DCE5F0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 3px 10px rgba(20, 50, 90, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #52657A !important;
    }

    [data-testid="stMetricValue"] {
        color: #17365D !important;
    }

    [data-testid="stSidebar"] {
        background-color: #E9EFF7;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 8px;
    }

    [data-testid="stTabs"] button {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 3. LOAD THE CLEANED DATASET
# --------------------------------------------------
st.sidebar.title("⚙️ Dashboard Controls")

DATA_PATH = (
    Path(__file__).resolve().parent
    / "Data"
    / "cleaned_delivery_dataset.csv"
)


@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    required_columns = [
        "Order_ID",
        "Order_Date",
        "Promised_Date",
        "Actual_Delivery_Date",
        "Warehouse",
        "Carrier",
        "Route",
        "Product_Type",
        "Quantity",
        "Shipping_Mode",
        "Distance_KM",
    ]

    missing_columns = [
        col for col in required_columns if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Convert date columns into datetime format.
    date_columns = [
        "Order_Date",
        "Promised_Date",
        "Actual_Delivery_Date",
    ]

    for col in date_columns:
        data[col] = pd.to_datetime(data[col], errors="coerce")

    # Convert numerical columns.
    for col in ["Quantity", "Distance_KM"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Calculate delivery delay in days.
    data["Delivery_Delay_Days"] = (
        data["Actual_Delivery_Date"] - data["Promised_Date"]
    ).dt.days

    # Classify delivery status.
    data["Delivery_Status"] = "Unknown"

    valid_delay = data["Delivery_Delay_Days"].notna()

    data.loc[
        valid_delay & (data["Delivery_Delay_Days"] > 0),
        "Delivery_Status",
    ] = "Late"

    data.loc[
        valid_delay & (data["Delivery_Delay_Days"] == 0),
        "Delivery_Status",
    ] = "On Time"

    data.loc[
        valid_delay & (data["Delivery_Delay_Days"] < 0),
        "Delivery_Status",
    ] = "Early"

    return data


if not DATA_PATH.exists():
    st.error(
        "Dataset not found. Please check that "
        "'data/cleaned_delivery_dataset.csv' exists "
        "inside your project folder."
    )
    st.code(str(DATA_PATH))
    st.stop()

try:
    df = load_data(str(DATA_PATH))
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()


if df.empty:
    st.warning("Your dataset is empty.")
    st.stop()


# --------------------------------------------------
# 4. SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.subheader("Filter Orders")

valid_dates = df["Order_Date"].dropna()

if valid_dates.empty:
    st.error("No valid Order_Date values were found.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    start_date, end_date = min_date, max_date
else:
    start_date, end_date = date_range

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")
    st.stop()

filtered_df = df[
    df["Order_Date"].dt.date.between(start_date, end_date)
].copy()


def add_multiselect_filter(column, label):
    options = sorted(
        filtered_df[column].dropna().astype(str).unique().tolist()
    )

    selected = st.sidebar.multiselect(
        label,
        options=options,
        default=options,
    )

    return selected


carrier_options = add_multiselect_filter("Carrier", "Carrier")
warehouse_options = add_multiselect_filter("Warehouse", "Warehouse")
shipping_options = add_multiselect_filter(
    "Shipping_Mode", "Shipping Mode"
)

filtered_df = filtered_df[
    filtered_df["Carrier"].astype(str).isin(carrier_options)
    & filtered_df["Warehouse"].astype(str).isin(warehouse_options)
    & filtered_df["Shipping_Mode"].astype(str).isin(shipping_options)
].copy()

st.sidebar.caption(f"Filtered orders: {len(filtered_df):,}")
st.sidebar.caption(f"Original records: {len(df):,}")


# --------------------------------------------------
# 5. DASHBOARD HEADER
# --------------------------------------------------
st.title("📦 Delivery Delay & Operations Analytics")

st.markdown(
    "Analyze delivery performance, shipping modes, carriers, "
    "warehouses, and monthly delivery trends."
)

st.caption(
    f"Showing orders from {start_date} to {end_date}"
)


# --------------------------------------------------
# 6. CREATE FOUR DASHBOARD TABS
# --------------------------------------------------
tab_overview, tab_performance, tab_trends, tab_data = st.tabs(
    [
        "📊 Overview",
        "🏭 Performance",
        "📈 Trends & Insights",
        "📁 Data Explorer",
    ]
)


# --------------------------------------------------
# 7. KPI CALCULATIONS
# --------------------------------------------------
total_orders = len(filtered_df)

late_orders = (
    filtered_df["Delivery_Status"] == "Late"
).sum()

on_time_orders = (
    filtered_df["Delivery_Status"] == "On Time"
).sum()

early_orders = (
    filtered_df["Delivery_Status"] == "Early"
).sum()

late_percentage = (
    late_orders / total_orders * 100 if total_orders else 0
)

on_time_percentage = (
    on_time_orders / total_orders * 100 if total_orders else 0
)

early_percentage = (
    early_orders / total_orders * 100 if total_orders else 0
)

late_delays = filtered_df.loc[
    filtered_df["Delivery_Status"] == "Late",
    "Delivery_Delay_Days",
].dropna()

average_late_delay = (
    late_delays.mean() if not late_delays.empty else 0
)

max_delay = (
    late_delays.max() if not late_delays.empty else 0
)


# --------------------------------------------------
# 8. OVERVIEW TAB
# --------------------------------------------------
with tab_overview:
    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Late Orders", f"{late_orders:,}")
    col3.metric("On-Time Orders", f"{on_time_orders:,}")
    col4.metric("Late Delivery Rate", f"{late_percentage:.2f}%")

    st.divider()

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Delivery Status Distribution")

        status_counts = (
            filtered_df["Delivery_Status"]
            .value_counts()
            .reindex(
                ["On Time", "Late", "Early", "Unknown"],
                fill_value=0,
            )
            .rename_axis("Delivery Status")
            .reset_index(name="Orders")
        )

        if status_counts["Orders"].sum() > 0:
            fig_status = px.pie(
                status_counts,
                names="Delivery Status",
                values="Orders",
                hole=0.55,
                title="Order Status Breakdown",
                color="Delivery Status",
                color_discrete_map={
                    "On Time": "#2EAD73",
                    "Late": "#E45858",
                    "Early": "#4C8BF5",
                    "Unknown": "#9AA5B1",
                },
            )

            fig_status.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )

            fig_status.update_layout(
                margin=dict(t=60, b=20, l=20, r=20),
                legend_title_text="Delivery Status",
            )

            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No delivery status data available.")

    with right_col:
        st.subheader("Delivery Summary")

        st.metric("On-Time Delivery Rate", f"{on_time_percentage:.2f}%")
        st.metric("Early Delivery Rate", f"{early_percentage:.2f}%")
        st.metric("Average Delay (Late Orders)", f"{average_late_delay:.2f} days")
        st.metric("Maximum Delay", f"{max_delay:.0f} days")

    st.info(
        "Use the sidebar filters to explore specific dates, "
        "carriers, warehouses, and shipping modes."
    )


# --------------------------------------------------
# 9. PERFORMANCE TAB
# --------------------------------------------------
with tab_performance:
    st.subheader("Carrier, Warehouse & Shipping Performance")

    if filtered_df.empty:
        st.warning("No orders match the selected filters.")
    else:
        performance_columns = st.columns(2)

        # Carrier performance
        with performance_columns[0]:
            st.markdown("#### Late Delivery Rate by Carrier")

            carrier_stats = (
                filtered_df.groupby("Carrier", dropna=False)
                .agg(
                    Total_Orders=("Delivery_Status", "size"),
                    Late_Orders=(
                        "Delivery_Status",
                        lambda values: (values == "Late").sum(),
                    ),
                )
                .reset_index()
            )

            carrier_stats["Late_Rate"] = (
                carrier_stats["Late_Orders"]
                / carrier_stats["Total_Orders"]
                * 100
            )

            carrier_stats = carrier_stats.sort_values(
                "Late_Rate", ascending=False
            )

            fig_carrier = px.bar(
                carrier_stats,
                x="Carrier",
                y="Late_Rate",
                color="Late_Rate",
                text="Late_Rate",
                hover_data=["Total_Orders", "Late_Orders"],
                title="Carrier Late Rate (%)",
                color_continuous_scale="Reds",
            )

            fig_carrier.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
            )

            fig_carrier.update_layout(
                yaxis_title="Late Delivery Rate (%)",
                xaxis_title="Carrier",
                coloraxis_showscale=False,
            )

            st.plotly_chart(fig_carrier, use_container_width=True)

        # Warehouse performance
        with performance_columns[1]:
            st.markdown("#### Late Delivery Rate by Warehouse")

            warehouse_stats = (
                filtered_df.groupby("Warehouse", dropna=False)
                .agg(
                    Total_Orders=("Delivery_Status", "size"),
                    Late_Orders=(
                        "Delivery_Status",
                        lambda values: (values == "Late").sum(),
                    ),
                )
                .reset_index()
            )

            warehouse_stats["Late_Rate"] = (
                warehouse_stats["Late_Orders"]
                / warehouse_stats["Total_Orders"]
                * 100
            )

            warehouse_stats = warehouse_stats.sort_values(
                "Late_Rate", ascending=False
            )

            fig_warehouse = px.bar(
                warehouse_stats,
                x="Warehouse",
                y="Late_Rate",
                color="Late_Rate",
                text="Late_Rate",
                hover_data=["Total_Orders", "Late_Orders"],
                title="Warehouse Late Rate (%)",
                color_continuous_scale="Oranges",
            )

            fig_warehouse.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
            )

            fig_warehouse.update_layout(
                yaxis_title="Late Delivery Rate (%)",
                xaxis_title="Warehouse",
                coloraxis_showscale=False,
            )

            st.plotly_chart(fig_warehouse, use_container_width=True)

        # Shipping mode performance
        st.markdown("#### Late Delivery Rate by Shipping Mode")

        shipping_stats = (
            filtered_df.groupby("Shipping_Mode", dropna=False)
            .agg(
                Total_Orders=("Delivery_Status", "size"),
                Late_Orders=(
                    "Delivery_Status",
                    lambda values: (values == "Late").sum(),
                ),
            )
            .reset_index()
        )

        shipping_stats["Late_Rate"] = (
            shipping_stats["Late_Orders"]
            / shipping_stats["Total_Orders"]
            * 100
        )

        shipping_stats = shipping_stats.sort_values(
            "Late_Rate", ascending=False
        )

        fig_shipping = px.bar(
            shipping_stats,
            x="Shipping_Mode",
            y="Late_Rate",
            color="Shipping_Mode",
            text="Late_Rate",
            hover_data=["Total_Orders", "Late_Orders"],
            title="Shipping Mode Late Rate (%)",
        )

        fig_shipping.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
        )

        fig_shipping.update_layout(
            yaxis_title="Late Delivery Rate (%)",
            xaxis_title="Shipping Mode",
            showlegend=False,
        )

        st.plotly_chart(fig_shipping, use_container_width=True)


# --------------------------------------------------
# 10. TRENDS & INSIGHTS TAB
# --------------------------------------------------
with tab_trends:
    st.subheader("Monthly Delivery Trends")

    monthly_data = filtered_df.dropna(
        subset=["Order_Date"]
    ).copy()

    if monthly_data.empty:
        st.info("No valid order dates available for trend analysis.")
    else:
        monthly_data["Month"] = (
            monthly_data["Order_Date"].dt.to_period("M").astype(str)
        )

        monthly_stats = (
            monthly_data.groupby("Month")
            .agg(
                Total_Orders=("Delivery_Status", "size"),
                Late_Orders=(
                    "Delivery_Status",
                    lambda values: (values == "Late").sum(),
                ),
            )
            .reset_index()
        )

        monthly_stats["Late_Rate"] = (
            monthly_stats["Late_Orders"]
            / monthly_stats["Total_Orders"]
            * 100
        )

        fig_monthly = px.line(
            monthly_stats,
            x="Month",
            y="Late_Rate",
            markers=True,
            text="Late_Rate",
            title="Monthly Late Delivery Rate",
            hover_data=["Total_Orders", "Late_Orders"],
        )

        fig_monthly.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="top center",
        )

        fig_monthly.update_layout(
            xaxis_title="Month",
            yaxis_title="Late Delivery Rate (%)",
        )

        st.plotly_chart(fig_monthly, use_container_width=True)

        st.markdown("#### Monthly Summary")

        display_monthly = monthly_stats.copy()
        display_monthly["Late_Rate"] = (
            display_monthly["Late_Rate"].round(2)
        )

        st.dataframe(
            display_monthly,
            use_container_width=True,
            hide_index=True,
        )
    
    # Day 7: Advanced Business Insights
    st.divider()
    st.subheader("🔍 Advanced Business Insights")

    # Carrier Risk Analysis
    st.markdown("### 1. Carrier Risk Analysis")

    carrier_analysis = (
        filtered_df.groupby("Carrier")
        .agg(
            Total_Orders=("Order_ID", "count"),
            Late_Orders=(
                "Delivery_Status",
                lambda s: (s == "Late").sum()
            )
        )
        .reset_index()
    )

    carrier_analysis["Late_Rate"] = (
        carrier_analysis["Late_Orders"]
        / carrier_analysis["Total_Orders"]
        * 100
    )

    carrier_analysis = carrier_analysis.sort_values(
        "Late_Rate", ascending=False
    )

    st.dataframe(
        carrier_analysis.style.format(
            {"Late_Rate": "{:.2f}%"}
        ),
        use_container_width=True,
        hide_index=True
    )

    
    # 2. Warehouse Performance Ranking
    st.markdown("### 2. Warehouse Performance Ranking")

    warehouse_analysis = (
        filtered_df.groupby("Warehouse")
        .agg(
            Total_Orders=("Order_ID", "count"),
            Late_Orders=(
                "Delivery_Status",
                lambda s: (s == "Late").sum()
            )
        )
        .reset_index()
    )

    warehouse_analysis["Late_Rate"] = (
        warehouse_analysis["Late_Orders"]
        / warehouse_analysis["Total_Orders"]
        * 100
    )

    warehouse_analysis = warehouse_analysis.sort_values(
        "Late_Rate", ascending=False
    )

    st.dataframe(
        warehouse_analysis.style.format(
            {"Late_Rate": "{:.2f}%"}
        ),
        use_container_width=True,
        hide_index=True
    )



    
    # 3. Distance vs. Delivery Delay
    st.markdown("### 3. Distance vs. Delivery Delay")

    distance_data = filtered_df.dropna(
        subset=["Distance_KM", "Delivery_Delay_Days"]
    ).copy()

    if len(distance_data) >= 2:
        fig_distance = px.scatter(
            distance_data,
            x="Distance_KM",
            y="Delivery_Delay_Days",
            color="Delivery_Status",
            hover_data=["Order_ID", "Carrier", "Warehouse"],
            title="Delivery Distance vs. Delay Days",
            labels={
                "Distance_KM": "Distance (KM)",
                "Delivery_Delay_Days": "Delay (Days)"
            },
            color_discrete_map={
                "Late": "#E45858",
                "On Time": "#2EAD73",
                "Early": "#4C8BF5",
                "Unknown": "#9AA5B1"
            }
        )

        fig_distance.add_hline(
            y=0,
            line_dash="dash",
            annotation_text="Promised delivery date"
        )

        st.plotly_chart(
            fig_distance,
            use_container_width=True
        )

        correlation = distance_data[
            ["Distance_KM", "Delivery_Delay_Days"]
        ].corr().iloc[0, 1]

        if pd.notna(correlation):
            st.metric(
                "Distance–Delay Correlation",
                f"{correlation:.2f}"
            )

            if correlation > 0.3:
                st.info(
                    "Longer distances show a positive relationship "
                    "with delay in this dataset."
                )
            elif correlation < -0.3:
                st.info(
                    "Longer distances show a negative relationship "
                    "with delay in this dataset."
                )
            else:
                st.info(
                    "The linear relationship between distance and "
                    "delay is weak in this dataset."
                )

            st.caption(
                "Correlation does not prove that distance causes delays."
            )
    else:
        st.info("Not enough valid data for distance analysis.")



    
    #Top 3 Problem Areas
    st.divider()
    st.subheader("Top 3 Problem Areas")

    # Find the 3 carriers with the highest late-delivery rates
    top_carriers = (
        filtered_df.groupby("Carrier")
        .agg(
            Total_Orders=("Order_ID", "count"),
            Late_Orders=(
                "Delivery_Status",
                lambda s: (s == "Late").sum()
            )
        )
        .reset_index()
    )

    top_carriers["Late_Rate"] = (
        top_carriers["Late_Orders"]
        / top_carriers["Total_Orders"] * 100
    )

    top_carriers = top_carriers.sort_values(
        "Late_Rate", ascending=False
    ).head(3)

    st.markdown("#### Carriers Needing Attention")
    st.dataframe(
        top_carriers.style.format(
            {"Late_Rate": "{:.2f}%"}
        ),
        use_container_width=True,
        hide_index=True
    )

    # Find the 3 warehouses with the highest late-delivery rates
    top_warehouses = (
        filtered_df.groupby("Warehouse")
        .agg(
            Total_Orders=("Order_ID", "count"),
            Late_Orders=(
                "Delivery_Status",
                lambda s: (s == "Late").sum()
            )
        )
        .reset_index()
    )

    top_warehouses["Late_Rate"] = (
        top_warehouses["Late_Orders"]
        / top_warehouses["Total_Orders"] * 100
    )

    top_warehouses = top_warehouses.sort_values(
        "Late_Rate", ascending=False
    ).head(3)

    st.markdown("#### Warehouses Needing Attention")
    st.dataframe(
        top_warehouses.style.format(
            {"Late_Rate": "{:.2f}%"}
        ),
        use_container_width=True,
        hide_index=True
    )


    
    # Step 2: Automatic Business Recommendations
    st.divider()
    st.subheader("Automatic Business Recommendations")

    # Overall late-delivery rate
    total_orders = len(filtered_df)

    if total_orders > 0:
        late_orders = (
            filtered_df["Delivery_Status"] == "Late"
        ).sum()

        overall_late_rate = (
            late_orders / total_orders
        ) * 100

        st.metric(
            "Overall Late Delivery Rate",
            f"{overall_late_rate:.2f}%"
        )

        # Recommendation based on overall performance
        if overall_late_rate > 25:
            st.warning(
                "High late-delivery rate: review carrier "
                "performance, warehouse operations, and routes."
            )
        elif overall_late_rate > 15:
            st.info(
                "Moderate late-delivery rate: investigate "
                "the main sources of delivery delays."
            )
        else:
            st.success(
                "Late-delivery rate is relatively low. "
                "Continue monitoring performance."
            )

        # Carrier recommendation
        if not top_carriers.empty:
            worst_carrier = top_carriers.iloc[0]

            st.markdown("#### Carrier Recommendation")
            st.write(
                f"Review **{worst_carrier['Carrier']}**, "
                f"which has a late-delivery rate of "
                f"**{worst_carrier['Late_Rate']:.2f}%** "
                "in the selected data."
            )

        # Warehouse recommendation
        if not top_warehouses.empty:
            worst_warehouse = top_warehouses.iloc[0]

            st.markdown("#### Warehouse Recommendation")
            st.write(
                f"Investigate operations at "
                f"**{worst_warehouse['Warehouse']}**, "
                f"which has a late-delivery rate of "
                f"**{worst_warehouse['Late_Rate']:.2f}%** "
                "in the selected data."
            )

    else:
        st.info(
            "No orders match the selected filters. "
            "Change the filters to generate recommendations."
        )
    
    # Step 3: Download Business Insights Report
    st.divider()
    st.subheader("Download Business Insights Report")

    report_rows = []

    if total_orders > 0:
        report_rows.append({
            "Insight": "Overall Late Delivery Rate",
            "Category": "Overall",
            "Late_Rate_Percent": round(
                overall_late_rate, 2
            ),
            "Total_Orders": total_orders,
            "Late_Orders": int(late_orders)
        })

    for _, row in carrier_analysis.iterrows():
        report_rows.append({
            "Insight": "Carrier Performance",
            "Category": row["Carrier"],
            "Late_Rate_Percent": round(
                row["Late_Rate"], 2
            ),
            "Total_Orders": int(row["Total_Orders"]),
            "Late_Orders": int(row["Late_Orders"])
        })

    for _, row in warehouse_analysis.iterrows():
        report_rows.append({
            "Insight": "Warehouse Performance",
            "Category": row["Warehouse"],
            "Late_Rate_Percent": round(
                row["Late_Rate"], 2
            ),
            "Total_Orders": int(row["Total_Orders"]),
            "Late_Orders": int(row["Late_Orders"])
        })

    if report_rows:
        report_df = pd.DataFrame(report_rows)

        report_csv = report_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Business Insights CSV",
            data=report_csv,
            file_name="delivery_business_insights.csv",
            mime="text/csv"
        )
    else:
        st.info("No report data is available for the selected filters.")

    
    st.divider()
    st.subheader("Business Insights & Recommendations")

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.metric("Late Delivery Rate", f"{late_percentage:.2f}%")

        if late_percentage > 25:
            st.warning(
                "Late delivery rate is above 25%. "
                "Investigate delays and improve delivery planning."
            )
        else:
            st.success(
                "Late delivery rate is at or below 25%. "
                "Continue monitoring delivery performance."
            )

        if not late_delays.empty:
            st.write(
                f"Late orders take an average of "
                f"{average_late_delay:.2f} extra days."
            )

    with insight_col2:
        if not filtered_df.empty:
            carrier_insights = (
                filtered_df.groupby("Carrier")
                .agg(
                    Orders=("Delivery_Status", "size"),
                    Late_Orders=(
                        "Delivery_Status",
                        lambda values: (values == "Late").sum(),
                    ),
                )
            )

            carrier_insights = carrier_insights[
                carrier_insights["Orders"] > 0
            ]

            if not carrier_insights.empty:
                carrier_insights["Late_Rate"] = (
                    carrier_insights["Late_Orders"]
                    / carrier_insights["Orders"]
                    * 100
                )

                worst_carrier = carrier_insights["Late_Rate"].idxmax()

                st.write(
                    f"**Carrier needing attention:** {worst_carrier} "
                    f"({carrier_insights.loc[worst_carrier, 'Late_Rate']:.2f}% "
                    "late rate)."
                )

            warehouse_insights = (
                filtered_df.groupby("Warehouse")
                .agg(
                    Orders=("Delivery_Status", "size"),
                    Late_Orders=(
                        "Delivery_Status",
                        lambda values: (values == "Late").sum(),
                    ),
                )
            )

            warehouse_insights = warehouse_insights[
                warehouse_insights["Orders"] > 0
            ]

            if not warehouse_insights.empty:
                warehouse_insights["Late_Rate"] = (
                    warehouse_insights["Late_Orders"]
                    / warehouse_insights["Orders"]
                    * 100
                )

                worst_warehouse = warehouse_insights["Late_Rate"].idxmax()

                st.write(
                    f"**Warehouse needing attention:** {worst_warehouse} "
                    f"({warehouse_insights.loc[worst_warehouse, 'Late_Rate']:.2f}% "
                    "late rate)."
                )

    st.markdown("#### Recommended Actions")

    st.markdown(
        """
        - Investigate carriers and warehouses with higher late delivery rates.
        - Review route planning and estimated delivery times.
        - Compare Standard, Express, and Same Day shipping performance.
        - Monitor monthly trends to identify recurring delivery problems.
        - Review the quality of missing or unknown dataset values.
        """
    )


# --------------------------------------------------
# 11. DATA EXPLORER TAB
# --------------------------------------------------
with tab_data:
    st.subheader("Dataset Overview")

    st.write(f"**Filtered records:** {len(filtered_df):,}")
    st.write(f"**Total original records:** {len(df):,}")

    st.markdown("#### Filtered Dataset Preview")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    

    st.markdown("#### Dataset Information")

    info_col1, info_col2, info_col3 = st.columns(3)

    info_col1.metric("Rows", f"{filtered_df.shape[0]:,}")
    info_col2.metric("Columns", f"{filtered_df.shape[1]:,}")
    info_col3.metric(
        "Missing Cells",
        f"{int(filtered_df.isna().sum().sum()):,}",
    )

    with st.expander("View Missing Values by Column"):
        missing_summary = (
            filtered_df.isna()
            .sum()
            .rename("Missing Values")
            .reset_index()
            .rename(columns={"index": "Column"})
        )

        st.dataframe(
            missing_summary,
            use_container_width=True,
            hide_index=True,
        )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Dataset (CSV)",
        data=csv_data,
        file_name="filtered_delivery_dataset.csv",
        mime="text/csv",
    )


# --------------------------------------------------
# 12. FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Delivery Delay & Operations Analytics | "
    "Built with Python, Pandas, Streamlit and Plotly"
)
