import json
import os
import random

from country_state_city import City, State
from database import get_connection


random.seed(42)


def get_locations():
    # Load Indian city/state pairs once and cache them locally.
    cache_file = "indian_locations.json"

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as file:
            locations = json.load(file)

        # Use the cache only if it has the expected dictionary format.
        if locations and isinstance(locations[0], dict):
            return locations

    states = State.get_states_of_country("IN")
    locations = []

    for state in states:
        cities = City.get_cities_of_state("IN", state.iso_code)

        for city in cities:
            locations.append({
                "city": city.name,
                "state": state.name
            })

    if not locations:
        raise ValueError("No Indian city data found.")

    with open(cache_file, "w", encoding="utf-8") as file:
        json.dump(locations, file, ensure_ascii=False, indent=2)

    return locations


blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
blood_group_weights = [22, 5, 18, 5, 8, 3, 30, 9]

first_names = [
    "Aarav", "Ishita", "Rohan", "Ananya",
    "Kabir", "Meera", "Arjun", "Sara",
    "Vihaan", "Diya", "Aditya", "Aditi",
    "Rahul", "Neha", "Karan", "Priya"
]

last_names = [
    "Sharma", "Patil", "Deshmukh", "Joshi",
    "Kulkarni", "Mehta", "Shah", "Verma",
    "Pawar", "Singh"
]


def random_health_response():
    return random.choices(
        [True, False, None],
        weights=[15, 65, 20]
    )[0]


def generate_donors():
    locations = get_locations()
    print(f"Loaded {len(locations)} Indian city/state combinations.")
    print("Generating 100 synthetic donors...")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for i in range(100):
            name = (
                f"Demo {random.choice(first_names)} "
                f"{random.choice(last_names)}"
            )
            age = random.randint(18, 60)

            blood_group = random.choices(
                blood_groups,
                weights=blood_group_weights
            )[0]

            location = random.choice(locations)
            city = location["city"]
            state = location["state"]
            available = random.choice([True, True, True, False])

            # Fictional contact number for demonstration only.
            phone = f"000000{random.randint(1000, 9999)}"

            cursor.execute(
                '''
                INSERT INTO donors
                    (name, age, blood_group, city, state, phone, available)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING donor_id
                ''',
                (
                    name, age, blood_group,
                    city, state, phone, available
                )
            )

            donor_id = cursor.fetchone()[0]

            cursor.execute(
                '''
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
                ''',
                (
                    donor_id,
                    random_health_response(),
                    random_health_response(),
                    random_health_response(),
                    random_health_response(),
                    random_health_response(),
                    random_health_response(),
                    True
                )
            )

            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1}/100 donors...")

        conn.commit()
        print("100 synthetic donors and health records inserted successfully!")

    except Exception as e:
        conn.rollback()
        print("Error generating donor data:", e)
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    generate_donors()
