

import random
from database import get_connection

random.seed(42)

blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
blood_group_weights = [22, 5, 18, 5, 8, 3, 30, 9]

cities = [
    "Pune", "Mumbai", "Nashik",
    "Nagpur", "Sangli", "Kolhapur"
]

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

conn = get_connection()
cursor = conn.cursor()

for i in range(100):
    name = f"Demo {random.choice(first_names)} {random.choice(last_names)}"
    age = random.randint(18, 60)

    blood_group = random.choices(
        blood_groups,
        weights=blood_group_weights
    )[0]

    city = random.choice(cities)
    available = random.choice([True, True, True, False])

    # Fictional contact number for demonstration only
    phone = f"000000{random.randint(1000, 9999)}"

    cursor.execute("""
        INSERT INTO donors
        (name, age, blood_group, city, phone, available)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        name, age, blood_group,
        city, phone, available
    ))

conn.commit()
cursor.close()
conn.close()

print("100 synthetic donor records inserted successfully!")
