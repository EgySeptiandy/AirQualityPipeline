# Automated Air Quality Index (AQI) Data Pipeline & Live Dashboard

An end-to-end, automated time-series Data Engineering pipeline that extracts multi-city air quality data, cleanses and transforms the payload, and loads it into a PostgreSQL Data Warehouse using an **idempotent Upsert strategy**.

The entire pipeline is orchestrated seamlessly via **GitHub Actions (Cron Jobs)** and visualized through an interactive **Streamlit Live Dashboard**.

---

## System Architecture

```text
[ Open-Meteo API (FlatBuffers Binary) ]
                  │
                  ▼
      [ Python ETL Pipeline ]  <─── [ GitHub Actions Cron Job (Every 6 Hours) ]
                  │
                  ▼
       [ Supabase PostgreSQL ] (Schema: `air_quality`, Upsert Strategy)
                  │
                  ▼
     [ Streamlit Live Dashboard ]
```

---

## Key Technical Highlights

* **High-Performance Ingestion:** Utilizes the **Open-Meteo Python SDK** with **FlatBuffers binary serialization** for fast, lightweight data extraction across multiple geolocation coordinates simultaneously.
* **Resilient Requests:** Integrated `requests_cache` and `retry_requests` with exponential backoff to gracefully handle transient network failures.
* **Idempotent Upsert Strategy:** Built custom PostgreSQL `ON CONFLICT (time, city_name) DO UPDATE` logic via **SQLAlchemy** to eliminate duplicate data during automated scheduled runs.
* **Database Isolation:** Implemented multi-tenant database design using a custom PostgreSQL schema (`air_quality.fact_air_quality`) on Supabase.
* **Zero-Touch Automation:** Fully automated continuous data ingestion using **GitHub Actions Workflows**, secured with GitHub Repository Secrets.

---

## Tech Stack

* **Programming Language:** Python 3.10
* **Data Processing & ETL:** Pandas, NumPy, Open-Meteo SDK
* **Database & ORM:** PostgreSQL (Supabase Cloud), SQLAlchemy, Psycopg2
* **Orchestration / Automation:** GitHub Actions (`cron` scheduled triggers)
* **Visualization & UI:** Streamlit, Plotly Express

---

## Database Schema (`air_quality.fact_air_quality`)

| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `time` | `TIMESTAMPTZ` | `PRIMARY KEY` | Measurement timestamp (Asia/Jakarta timezone) |
| `city_name` | `VARCHAR(50)` | `PRIMARY KEY` | Target city name |
| `pm2_5` | `FLOAT4` | - | Particulate Matter < 2.5 µg/m³ concentration |
| `pm10` | `FLOAT4` | - | Particulate Matter < 10 µg/m³ concentration |
| `carbon_monoxide`| `FLOAT4` | - | Carbon Monoxide level |
| `carbon_dioxide` | `FLOAT4` | - | Carbon Dioxide level |
| `nitrogen_dioxide`| `FLOAT4` | - | Nitrogen Dioxide level |
| `dust` | `FLOAT4` | - | Atmospheric dust level |
| `uv_index` | `FLOAT4` | - | Ultraviolet index |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Data ingestion timestamp |

> **Note:** The combination of `(time, city_name)` serves as a *Composite Primary Key* to enforce record uniqueness.

---

## Getting Started Locally

### 1. Clone Repository & Install Dependencies
```bash
git clone [https://github.com/EgySeptiandy/AirQualityPipeline.git](https://github.com/EgySeptiandy/AirQualityPipeline.git)
cd AirQualityPipeline
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
SUPABASE_PASSWORD=your_supabase_password_here
```

### 3. Run ETL Pipeline Manually
```bash
python etl_pipeline.py
```

### 4. Launch Streamlit Dashboard
```bash
streamlit run app.py
```
