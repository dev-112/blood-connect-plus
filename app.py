import matplotlib.pyplot as plt
import streamlit as st
from database import get_connection
import pandas as pd
from utils.matching import find_matching_donors

st.set_page_config(
    page_title="Blood Connect+",
    page_icon="🩸",
    layout="wide"
)

st.title("🩸 Blood Connect+")
st.caption("Connecting donors. Saving lives.")

st.divider()

st.header("Donor Registration")
st.write("Register a donor in the Blood Connect+ database.")

with st.form("donor_registration"):

    name = st.text_input("Full Name")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            value=18
        )

    with col2:
        blood_group = st.selectbox(
            "Blood Group",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        )

    city = st.text_input("City")
    phone = st.text_input("Phone Number")

    submitted = st.form_submit_button(
        "Register Donor",
        use_container_width=True
    )

    if submitted:

        if not name.strip() or not city.strip() or not phone.strip():
            st.warning("Please fill in all fields.")

        else:
            conn = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO donors
                    (name, age, blood_group, city, phone)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        name.strip(),
                        age,
                        blood_group,
                        city.strip(),
                        phone.strip()
                    )
                )

                conn.commit()

                st.success("Donor registered successfully!")

                cursor.close()

            except Exception as e:
                if conn:
                    conn.rollback()

                st.error("Registration failed.")
                st.code(str(e))

            finally:
                if conn:
                    conn.close()

st.divider()

st.header("🩸 Registered Donors")

try:
    conn = get_connection()

    query = """
        SELECT
            donor_id,
            name,
            age,
            blood_group,
            city,
            available
        FROM donors
        ORDER BY created_at DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    if df.empty:
        st.info("No donors registered yet.")

    else:
        st.metric("Total Registered Donors", len(df))

        search = st.text_input("Search donors by name or city")

        if search:
            df = df[
                df["name"].str.contains(search, case=False, na=False)
                | df["city"].str.contains(search, case=False, na=False)
            ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error("Could not retrieve donor records.")
    st.code(str(e))

st.divider()

st.header("🩸 Request Blood")
st.write("Submit a blood requirement.")

with st.form("blood_request_form"):

    requester_name = st.text_input("Recipient / Requester Name")

    col1, col2 = st.columns(2)

    with col1:
        required_group = st.selectbox(
            "Required Blood Group",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            key="request_blood_group"
        )

    with col2:
        units = st.number_input(
            "Units Required",
            min_value=1,
            max_value=20,
            value=1
        )

    hospital = st.text_input("Hospital Name")
    request_city = st.text_input("City")

    urgency = st.selectbox(
        "Urgency",
        ["Normal", "Urgent", "Critical"]
    )

    request_submitted = st.form_submit_button(
        "Submit Blood Request",
        use_container_width=True
    )

    if request_submitted:

        if not requester_name.strip() or not hospital.strip() or not request_city.strip():
            st.warning("Please complete all fields.")

        else:
            conn = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO blood_requests
                    (requester_name, blood_group, units,
                     hospital_name, city, urgency)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING request_id
                    """,
                    (
                        requester_name.strip(),
                        required_group,
                        units,
                        hospital.strip(),
                        request_city.strip(),
                        urgency
                    )
                )

                request_id = cursor.fetchone()[0]

                conn.commit()

                st.success(
                    f"Blood request submitted! Request ID: {request_id}"
                )

                cursor.close()

            except Exception as e:
                if conn:
                    conn.rollback()

                st.error("Could not submit request.")
                st.code(str(e))

            finally:
                if conn:
                    conn.close()

st.divider()

st.header("📋 Blood Requests")

try:
    conn = get_connection()

    requests_df = pd.read_sql_query(
        """
        SELECT
            request_id,
            requester_name,
            blood_group,
            units,
            hospital_name,
            city,
            urgency,
            status,
            created_at
        FROM blood_requests
        ORDER BY created_at DESC
        """,
        conn
    )

    conn.close()

    if requests_df.empty:
        st.info("No blood requests yet.")
    else:
        st.metric("Total Requests", len(requests_df))

        st.dataframe(
            requests_df,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error("Could not retrieve blood requests.")
    st.code(str(e))

st.divider()

st.header("🔍 Find Matching Donors")

try:
    conn = get_connection()

    requests_df = pd.read_sql_query(
        """
        SELECT request_id, requester_name, blood_group, city
        FROM blood_requests
        WHERE status = 'Pending'
        ORDER BY created_at DESC
        """,
        conn
    )

    if requests_df.empty:
        st.info("No pending requests available.")

    else:
        request_options = {
            f"#{row.request_id} | {row.requester_name} | "
            f"{row.blood_group} | {row.city}": row.request_id
            for row in requests_df.itertuples()
        }

        selected_request = st.selectbox(
            "Select a blood request",
            options=list(request_options.keys())
        )

        if st.button("Find Matching Donors"):
            request_id = request_options[selected_request]

            matches = find_matching_donors(conn, request_id)

            if matches:
                st.success(f"Found {len(matches)} potential matches!")

                match_df = pd.DataFrame(
                    matches,
                    columns=[
                        "Donor ID",
                        "Name",
                        "Blood Group",
                        "City"
                    ]
                )

                st.dataframe(
                    match_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.warning("No matching donors found.")

    conn.close()

except Exception as e:
    st.error("Matching operation failed.")
    st.code(str(e))


# BLOOD DEMAND ANALYSIS

st.divider()
st.header("📊 Blood Demand Analysis")

try:
    conn = get_connection()

    demand_df = pd.read_sql_query(
        """
        SELECT blood_group, city, urgency, created_at
        FROM blood_requests
        ORDER BY created_at
        """,
        conn
    )

    conn.close()

    if demand_df.empty:
        st.info("No request data available for analysis.")

    else:
        # 1. BLOOD GROUP-WISE DEMAND
        st.subheader("1. Blood Group-wise Demand")

        blood_counts = demand_df["blood_group"].value_counts().sort_index()

        fig, ax = plt.subplots(figsize=(9, 4))
        blood_counts.plot(kind="bar", ax=ax)

        ax.set_xlabel("Blood Group")
        ax.set_ylabel("Number of Requests")
        ax.set_title("Demand by Blood Group")
        ax.grid(axis="y", alpha=0.3)

        st.pyplot(fig)
        plt.close(fig)

        # 2. CITY-WISE DEMAND
        st.subheader("2. City-wise Demand")

        city_counts = demand_df["city"].value_counts()

        fig, ax = plt.subplots(figsize=(9, 4))
        city_counts.plot(kind="bar", ax=ax)

        ax.set_xlabel("City")
        ax.set_ylabel("Number of Requests")
        ax.set_title("Demand by City")
        ax.grid(axis="y", alpha=0.3)

        st.pyplot(fig)
        plt.close(fig)

        # 3. URGENCY-WISE DEMAND
        st.subheader("3. Urgency-wise Demand")

        urgency_counts = (
            demand_df["urgency"]
            .value_counts()
            .reindex(["Normal", "Urgent", "Critical"], fill_value=0)
        )

        fig, ax = plt.subplots(figsize=(8, 4))
        urgency_counts.plot(kind="bar", ax=ax)

        ax.set_xlabel("Urgency Level")
        ax.set_ylabel("Number of Requests")
        ax.set_title("Demand by Urgency")
        ax.grid(axis="y", alpha=0.3)

        st.pyplot(fig)
        plt.close(fig)

        # 4. MONTHLY DEMAND TRENDS
        st.subheader("4. Monthly Demand Trends")

        demand_df["created_at"] = pd.to_datetime(
            demand_df["created_at"]
        )

        monthly_counts = (
            demand_df
            .set_index("created_at")
            .resample("MS")
            .size()
        )

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(
            monthly_counts.index,
            monthly_counts.values,
            marker="o"
        )

        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Requests")
        ax.set_title("Monthly Blood Request Trends")
        ax.grid(alpha=0.3)

        fig.autofmt_xdate()
        st.pyplot(fig)
        plt.close(fig)

except Exception as e:
    st.error("Unable to generate demand analysis.")
    st.code(str(e))


st.caption("Blood Connect+ | Prototype")