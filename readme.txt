# Blood Connect+

**A database-driven blood donor management and matching platform.**

Blood Connect+ is a web-based prototype developed as part of our First Year Engineering Design and Innovation (EDI) project. It aims to simplify blood donor management, blood request handling, and donor matching through a centralized platform.

The application uses Python and Streamlit for its interface, PostgreSQL for data storage, and rule-based logic for matching blood requests with compatible donors.

## Features

- **Donor Registration:** Register donors with their basic details, blood group, and location.
- **Location Selection:** Select Indian states and cities through dropdown menus.
- **Donor Health Screening:** Collect optional self-reported health information with consent.
- **Donor Directory:** View, search, and filter registered donor records.
- **Blood Requests:** Create and maintain blood requests with details such as blood group, units, hospital, location, and urgency.
- **Donor Matching:** Identify available donors based on blood-group compatibility and matching city and state.
- **Demand Analytics:** Visualize blood request trends by blood group, location, urgency, and month.
- **Synthetic Data Generation:** Populate the database with sample donor and request records for testing and demonstration.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend / Dashboard | Streamlit |
| Programming Language | Python |
| Database | PostgreSQL |
| Database Connectivity | psycopg2, SQLAlchemy |
| Data Processing | Pandas |
| Visualizations | Matplotlib |
| Location Data | country-state-city |
| Environment Management | python-dotenv |

## Project Structure

```text
Blood-Connect/
│
├── app.py                  # Main Streamlit application
├── database.py             # Database connection functions
├── analytics.py            # Analytics and data processing
├── generate_data.py        # Synthetic blood request generation
├── generate_donors.py      # Synthetic donor generation
│
├── utils/
│   └── matching.py         # Donor matching logic
│
├── pages/
│   └── 2_Analytics.py      # Analytics dashboard
│
├── indian_locations.json   # Cached Indian location data
├── .env                    # Local database configuration
├── .gitignore
└── requirements.txt
```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd Blood-Connect
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit psycopg2-binary pandas python-dotenv sqlalchemy matplotlib country-state-city
```

### 4. Configure PostgreSQL

- Install and start PostgreSQL.
- Create a database for the project.
- Create the required tables: `donors`, `blood_requests`, `notifications`, and `donor_health_screening`.
- Ensure the tables include the columns expected by the application, including the `state` columns in `donors` and `blood_requests`.

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_NAME=blood_connect
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

Replace the example values with your local PostgreSQL configuration.

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Generating Sample Data

The project includes scripts to generate synthetic donor and blood request records.

Run them in this order:

```bash
python generate_donors.py
python generate_data.py
```

The scripts generate 100 sample donor records and 100 sample blood requests each time they are executed.

**Note:** These scripts append records to the database. Clear existing sample records before running them again if you want a fresh dataset.

## Important Notes

- This is an academic prototype intended for demonstration and experimentation.
- The generated records are synthetic and do not represent real donors or patients.
- Donor health information is self-reported and should not be treated as a medical eligibility assessment.
- Blood-group matching is simplified for demonstration. Actual transfusion decisions require professional blood-bank testing, compatibility checks, and clinical oversight.
- The prototype does not replace hospitals, blood banks, or authorized medical services.

## Future Scope

Potential improvements include:

- Automated donor notifications.
- More advanced blood demand analysis and prediction.
- Improved security and role-based access.
- Integration with authorized blood banks and healthcare institutions.

## Project Information

**Project:** Blood Connect+  
**Domain:** Healthcare Technology / Database Management  
**Academic Project:** First Year Engineering – Design and Innovation (EDI)

