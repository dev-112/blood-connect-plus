

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import get_connection


# COLOUR PALETTE

BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#263746"
GRID_COLOR = "#E8EEF1"



def show_analytics():

    st.title("📊 Blood Demand Analytics")
    st.caption(
        "Analysis of blood requests across groups, "
        "cities, urgency levels and time."
    )

    st.info(
        "This dashboard currently uses synthetic "
        "demonstration data, not actual blood demand."
    )

    # FETCH DATA
    conn = get_connection()

    try:
        demand_df = pd.read_sql_query(
            """
            SELECT blood_group, city, urgency, created_at
            FROM blood_requests
            """,
            conn
        )
    finally:
        conn.close()

    if demand_df.empty:
        st.warning("No data available for analysis.")
        return

    demand_df["created_at"] = pd.to_datetime(
        demand_df["created_at"]
    )

    demand_df["city"] = demand_df["city"].fillna("Unknown")

    # SUMMARY METRICS
    total_requests = len(demand_df)
    total_cities = demand_df["city"].nunique()

    top_group = (
        demand_df["blood_group"].value_counts().idxmax()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Requests", total_requests)
    col2.metric("Cities Covered", total_cities)
    col3.metric("Most Requested Group", top_group)

    st.divider()

    # CHART 1: BLOOD GROUP DEMAND
    st.subheader("Blood Group-wise Demand")

    blood_counts = (
        demand_df["blood_group"]
        .value_counts()
        .reindex(
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            fill_value=0
        )
    )

    st.bar_chart(
        blood_counts,
        x_label="Blood Group",
        y_label="Number of Requests",
        color="#287C80"
    )

    # CHART 2 AND 3: CITY AND URGENCY
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("City-wise Demand")

        city_counts = demand_df["city"].value_counts()

        st.bar_chart(
            city_counts,
            x_label="City",
            y_label="Number of Requests",
            color="#48A6A0"
        )

    with col2:
        st.subheader("Urgency-wise Demand")

        urgency_counts = (
            demand_df["urgency"]
            .value_counts()
            .reindex(["Normal", "Urgent", "Critical"], fill_value=0)
        )

        st.bar_chart(
            urgency_counts,
            x_label="Urgency",
            y_label="Number of Requests",
            color="#355C7D"
        )

    st.divider()

    # CHART 4: MONTHLY DEMAND TRENDS
    st.subheader("Monthly Demand Trends")

    monthly_counts = (
        demand_df
        .set_index("created_at")
        .resample("MS")
        .size()
    )

    st.line_chart(
        monthly_counts,
        x_label="Month",
        y_label="Number of Requests",
        color="#287C80"
    )
