BLOOD_COMPATIBILITY = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"]
}



def find_matching_donors(conn, request_id):

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT blood_group, city, state
        FROM blood_requests
        WHERE request_id = %s
        """,
        (request_id,)
    )

    request = cursor.fetchone()

    if not request:
        cursor.close()
        return []

    blood_group, city, state = request

    compatible_groups = BLOOD_COMPATIBILITY[blood_group]

    cursor.execute(
        """
        SELECT donor_id, name, blood_group, city, state
        FROM donors
        WHERE blood_group = ANY(%s)
        AND LOWER(TRIM(city)) = LOWER(TRIM(%s))
        AND LOWER(TRIM(state)) = LOWER(TRIM(%s))
        AND available = TRUE
        """,
        (compatible_groups, city, state)
    )

    donors = cursor.fetchall()

    cursor.close()

    return donors
