# Blood Connect+

**A database-driven blood donor management and matching platform.**

Blood Connect+ is a web-based prototype developed as part of our First Year Engineering Design and Innovation (EDI) project. It aims to simplify blood donor management, blood request handling, and donor matching through a centralized platform.

The application uses Python and Streamlit for its interface, PostgreSQL for data storage, and rule-based logic for matching blood requests with compatible donors.

---

## Features

- **Donor Registration** – Register donors with their basic details, blood group, and location.
- **Location Selection** – Select Indian states and cities through dropdown menus.
- **Donor Health Screening** – Collect optional self-reported health information with consent.
- **Donor Directory** – View, search, and filter registered donor records.
- **Blood Requests** – Create and manage blood requests with details such as blood group, units, hospital, location, and urgency.
- **Donor Matching** – Identify available donors based on blood-group compatibility and matching city and state.
- **Demand Analytics** – Visualize blood request trends by blood group, location, urgency, and month.
- **Synthetic Data Generation** – Populate the database with sample donor and request records for testing and demonstration.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend / Dashboard | Streamlit |
| Programming Language | Python |
| Database | PostgreSQL |
| Database Connectivity | psycopg2, SQLAlchemy |
| Data Processing | Pandas |
| Visualization | Matplotlib |
| Location Data | country-state-city |
| Environment Management | python-dotenv |

---

## Project Structure

```text
Blood-Connect/
│
├── app.py
├── analytics.py
├── database.py
├── generate_data.py
├── generate_donors.py
│
├── pages/
│   └── 2_Analytics.py
│
├── utils/
│   └── matching.py
│
├── indian_locations.json
├── .env
├── .gitignore
└── requirements.txt
```

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Blood-Connect
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit psycopg2-binary pandas python-dotenv sqlalchemy matplotlib country-state-city
```

### 4. Configure the database

- Install and start PostgreSQL.
- Create a database for the project.
- Create the following tables:
  - `donors`
  - `blood_requests`
  - `notifications`
  - `donor_health_screening`
- Ensure the `donors` and `blood_requests` tables include their respective `state` columns.

Create a `.env` file in the root directory:

```env
DB_HOST=localhost
DB_NAME=blood_connect
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

Replace the example values with your PostgreSQL credentials