import matplotlib.pyplot as plt
import streamlit as st
from database import get_connection, get_engine
import pandas as pd
from utils.matching import find_matching_donors
from country_state_city import State, City

st.set_page_config(
    page_title="Blood Connect+",
    page_icon="🩸",
    layout="wide"
)

@st.cache_data
def get_indian_states():
    return sorted(
        State.get_states_of_country("IN"),
        key=lambda state: state.name
    )


@st.cache_data
def get_indian_cities(state_code):
    cities = City.get_cities_of_state("IN", state_code)
    return sorted(set(city.name for city in cities))


INDIA_STATES = get_indian_states()

STATE_CODES = {
    state.name: state.iso_code
    for state in INDIA_STATES
}

STATE_NAMES = list(STATE_CODES.keys())



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

donor_state = st.selectbox(
    "State",
    STATE_NAMES,
    key="donor_state"
)

donor_city_options = get_indian_cities(STATE_CODES[donor_state])

city = st.selectbox(
    "City",
    donor_city_options,
    key="donor_city"
)

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

    phone = st.text_input("Phone Number")

    st.subheader("Health Information")
    st.caption(
        "Optional self-reported information for authorised "
        "personnel. This is not a medical eligibility assessment."
    )

    col1, col2 = st.columns(2)

    with col1:
        diabetes = st.selectbox(
            "Diagnosed with diabetes?",
            ["Not disclosed", "Yes", "No"]
        )

        hypertension = st.selectbox(
            "Diagnosed with hypertension?",
            ["Not disclosed", "Yes", "No"]
        )

        heart_condition = st.selectbox(
            "Known heart condition?",
            ["Not disclosed", "Yes", "No"]
        )

    with col2:
        current_medication = st.selectbox(
            "Currently taking medication?",
            ["Not disclosed", "Yes", "No"]
        )

        recent_illness = st.selectbox(
            "Recent illness?",
            ["Not disclosed", "Yes", "No"]
        )

        recent_surgery = st.selectbox(
            "Recent surgery?",
            ["Not disclosed", "Yes", "No"]
        )

    consent = st.checkbox(
        "I consent to storing this information "
        "and sharing it with authorised personnel."
    )

    submitted = st.form_submit_button(
        "Register Donor",
        use_container_width=True
    )

    if submitted:

        if not name.strip() or not city.strip() or not phone.strip():
            st.warning("Please fill in all required fields.")

        elif not consent:
            st.warning("Consent is required to store health information.")

        else:
            conn = None
            cursor = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                # Register donor
                cursor.execute(
                    """
                    INSERT INTO donors
                    (name, age, blood_group, city, state, phone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING donor_id
                    """,
                    (
                        name.strip(),
                        age,
                        blood_group,
                        city.strip(),
                        donor_state,
                        phone.strip()
                    )
                )

                donor_id = cursor.fetchone()[0]

                # Store health information
                def to_bool(value):
                    if value == "Yes":
                        return True
                    elif value == "No":
                        return False
                    return None

                cursor.execute(
                    """
                    INSERT INTO donor_health_screening
                    (
                        donor_id,
                        diabetes,
                        hypertension,
                        heart_condition,
                        current_medication,
                        recent_illness,
                        recent_surgery,
                        consent_to_share
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        donor_id,
                        to_bool(diabetes),
                        to_bool(hypertension),
                        to_bool(heart_condition),
                        to_bool(current_medication),
                        to_bool(recent_illness),
                        to_bool(recent_surgery),
                        consent
                    )
                )

                conn.commit()

                st.success("Donor registered successfully!")

            except Exception as e:
                if conn:
                    conn.rollback()

                st.error("Registration failed.")
                st.code(str(e))

            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()


st.divider()

st.header("🩸 Registered Donors")

try:
    query = """
        SELECT
            d.donor_id,
            d.name,
            d.age,
            d.blood_group,
            d.city,
            d.state,
            d.available,

            CASE
                WHEN h.diabetes IS NULL THEN 'Not disclosed'
                WHEN h.diabetes THEN 'Yes'
                ELSE 'No'
            END AS diabetes,

            CASE
                WHEN h.hypertension IS NULL THEN 'Not disclosed'
                WHEN h.hypertension THEN 'Yes'
                ELSE 'No'
            END AS hypertension,

            CASE
                WHEN h.heart_condition IS NULL THEN 'Not disclosed'
                WHEN h.heart_condition THEN 'Yes'
                ELSE 'No'
            END AS heart_condition,

            CASE
                WHEN h.current_medication IS NULL THEN 'Not disclosed'
                WHEN h.current_medication THEN 'Yes'
                ELSE 'No'
            END AS current_medication,

            CASE
                WHEN h.recent_illness IS NULL THEN 'Not disclosed'
                WHEN h.recent_illness THEN 'Yes'
                ELSE 'No'
            END AS recent_illness,

            CASE
                WHEN h.recent_surgery IS NULL THEN 'Not disclosed'
                WHEN h.recent_surgery THEN 'Yes'
                ELSE 'No'
            END AS recent_surgery

        FROM donors d
        LEFT JOIN donor_health_screening h
            ON d.donor_id = h.donor_id

        ORDER BY d.created_at DESC
    """

    engine = get_engine()
    try:
        df = pd.read_sql_query(query, engine)
    finally:
        engine.dispose()

    if df.empty:
        st.info("No donors registered yet.")

    else:
        st.metric("Total Registered Donors", len(df))

        search = st.text_input("Search donors by name or city")

        
        if search:
            df = df[
                df["name"].str.contains(search, case=False, na=False)
                | df["city"].str.contains(search, case=False, na=False)
                | df["state"].str.contains(search, case=False, na=False)
            ]

        st.subheader("Filter by Health Information")

        health_columns = {
            "Diabetes": "diabetes",
            "Hypertension": "hypertension",
            "Heart Condition": "heart_condition",
            "Current Medication": "current_medication",
            "Recent Illness": "recent_illness",
            "Recent Surgery": "recent_surgery"
        }

        col1, col2, col3 = st.columns(3)

        for index, (label, column) in enumerate(health_columns.items()):
            with [col1, col2, col3][index % 3]:
                selected = st.selectbox(
                    label,
                    ["All", "Yes", "No", "Not disclosed"],
                    key=f"filter_{column}"
                )

                if selected != "All":
                    df = df[df[column] == selected]

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

request_state = st.selectbox(
    "State",
    STATE_NAMES,
    key="request_state"
)

request_city_options = get_indian_cities(STATE_CODES[request_state])

request_city = st.selectbox(
    "City",
    request_city_options,
    key="request_city"
)

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
                     hospital_name, city, state, urgency)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING request_id
                    """,
                    (
                        requester_name.strip(),
                        required_group,
                        units,
                        hospital.strip(),
                        request_city.strip(),
                        request_state,
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
    requests_query = """
        SELECT
            request_id,
            requester_name,
            blood_group,
            units,
            hospital_name,
            city,
            state,
            urgency,
            status,
            created_at
        FROM blood_requests
        ORDER BY created_at DESC
    """

    engine = get_engine()
    try:
        requests_df = pd.read_sql_query(requests_query, engine)
    finally:
        engine.dispose()

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
    pending_query = """
        SELECT request_id, requester_name, blood_group, city, state
        FROM blood_requests
        WHERE status = 'Pending'
        ORDER BY created_at DESC
    """

    engine = get_engine()
    try:
        requests_df = pd.read_sql_query(pending_query, engine)
    finally:
        engine.dispose()

    if requests_df.empty:
        st.info("No pending requests available.")

    else:
        conn = get_connection()

        request_options = {
            f"#{row.request_id} | {row.requester_name} | "
            f"{row.blood_group} | {row.city}, {row.state}": row.request_id
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
                        "City",
                        "State"
                    ]
                )

                st.dataframe(
                    match_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.warning("No matching donors found.")

        if 'conn' in locals() and conn is not None:
            conn.close()

except Exception as e:
    if 'conn' in locals() and conn is not None:
        conn.close()
    st.error("Matching operation failed.")
    st.code(str(e))


# BLOOD DEMAND ANALYSIS

st.divider()
st.header("📊 Blood Demand Analysis")

try:
    demand_query = """
        SELECT blood_group, city, state, urgency, created_at
        FROM blood_requests
        ORDER BY created_at
    """

    engine = get_engine()
    try:
        demand_df = pd.read_sql_query(demand_query, engine)
    finally:
        engine.dispose()

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