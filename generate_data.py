
import random
from datetime import datetime, timedelta

from database import get_connection

random.seed(42)

blood_groups = [
    "A+", "A-", "B+", "B-",
    "AB+", "AB-", "O+", "O-"
]

# Deliberately synthetic request distribution
blood_group_weights = [22, 5, 18, 5, 8, 3, 30, 9]

urgencies = ["Normal", "Urgent", "Critical"]
urgency_weights = [60, 30, 10]

first_names = [
    "Aarav", "Ishita", "Rohan", "Ananya",
    "Kabir", "Meera", "Arjun", "Sara",
    "Vihaan", "Diya"
]

hospital_names = [
    "City General Hospital",
    "Central Medical Centre",
    "Unity Hospital",
    "LifeCare Hospital",
    "Community Hospital"
]

conn = get_connection()
cursor = conn.cursor()

try:
    # Get city-state combinations from registered synthetic donors
    cursor.execute("""
        SELECT DISTINCT city, state
        FROM donors
        WHERE city IS NOT NULL AND state IS NOT NULL
    """)

    locations = cursor.fetchall()

    if not locations:
        raise ValueError(
            "No donor locations found. Run generate_donors.py first."
        )

    for i in range(100):

        requester = f"Demo User {random.choice(first_names)}"

        group = random.choices(
            blood_groups,
            weights=blood_group_weights
        )[0]

        units = random.randint(1, 4)
        hospital = random.choice(hospital_names)

        city, state = random.choice(locations)

        urgency = random.choices(
            urgencies,
            weights=urgency_weights
        )[0]

        # Random date within the last 12 months
        days_ago = random.randint(0, 364)
        created_at = datetime.now() - timedelta(days=days_ago)

        cursor.execute(
            """
            INSERT INTO blood_requests
            (
                requester_name,
                blood_group,
                units,
                hospital_name,
                city,
                state,
                urgency,
                status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending', %s)
            """,
            (
                requester,
                group,
                units,
                hospital,
                city,
                state,
                urgency,
                created_at
            )
        )

    conn.commit()

    print("100 synthetic blood requests inserted successfully!")

except Exception as e:
    conn.rollback()
    print("Error generating request data:", e)

finally:
    cursor.close()
    conn.close()
