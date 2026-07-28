import os
import sys
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

# Setup API Client with Cache and Retry
def get_openmeteo_client():
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    return openmeteo_requests.Client(session=retry_session)

# Extract Data from Open-Meteo
def extract_data(openmeteo_client):
    print("Fetching data from Open-Meteo API...")
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    # Coordinates
    city_names = ["Jakarta Kota", "Bekasi", "Bandung", "Yogyakarta", "Surabaya"]
    params = {
	"latitude": [-6.1959, -6.2398, -6.9172, -7.8012, -7.2587],
	"longitude": [106.827, 106.9757, 107.6198, 110.3605, 112.7535],
	"hourly": ["pm10", "pm2_5", "carbon_monoxide", "carbon_dioxide", "dust", "uv_index", "nitrogen_dioxide"],
    "timezone": "Asia/Jakarta"
    }

    responses = openmeteo_client.weather_api(url, params=params)
    all_city_data = []

    for i, response in enumerate(responses):
        city = city_names[i]
        hourly = response.Hourly()

        start_time = pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert("Asia/Jakarta")
        end_time = pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert("Asia/Jakarta")
        interval = pd.Timedelta(seconds=hourly.Interval())

        data_range = pd.date_range(start=start_time, end=end_time, freq=interval, inclusive="left")

        city_df = pd.DataFrame({
            "time": data_range,
            "city_name": city,
            "pm10": hourly.Variables(0).ValuesAsNumpy(),
            "pm2_5": hourly.Variables(1).ValuesAsNumpy(),
            "carbon_monoxide": hourly.Variables(2).ValuesAsNumpy(),
            "carbon_dioxide": hourly.Variables(3).ValuesAsNumpy(),
            "dust": hourly.Variables(4).ValuesAsNumpy(),
            "uv_index": hourly.Variables(5).ValuesAsNumpy(),
            "nitrogen_dioxide": hourly.Variables(6).ValuesAsNumpy()
        })

        all_city_data.append(city_df)

    df_concat = pd.concat(all_city_data, ignore_index=True)
    return df_concat

# Transform & CLean Data
def transform_data(df):
    print("Cleaning and Transforming Data...")

    df_clean = df.dropna(subset=['pm10', 'pm2_5'], how='all').copy()
    df_clean['time'] = pd.to_datetime(df_clean['time'])
    return df_clean

# Load to Supabase
def load_supabase(df, engine, schema_name="air_quality", table_name="fact_air_quality"):
    print("Uploading data to Supabase...")

    records = df.to_dict(orient='records')
    if not records:
        print("No records to insert")
        return
    metadata = sa.MetaData(schema=schema_name)
    table = sa.Table(table_name, metadata, autoload_with=engine)

    stmt = insert(table).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['time', 'city_name'],
        set_={
            'pm10': stmt.excluded.pm10,
            'pm2_5': stmt.excluded.pm2_5,
            'carbon_monoxide': stmt.excluded.carbon_monoxide,
            'carbon_dioxide': stmt.excluded.carbon_dioxide,
            'dust': stmt.excluded.dust,
            'uv_index': stmt.excluded.uv_index,
            'nitrogen_dioxide': stmt.excluded.nitrogen_dioxide
        }
    )

    with engine.begin() as conn:
        conn.execute(upsert_stmt)

    print("Upsert Successful")

# Main Execution Pipeline
def main():
    print("Starting Air Quality Pipeline")

    DB_PASSWORD = os.environ.get("SUPABASE_PASSWORD")
    if not DB_PASSWORD:
        print("Error: SUPABASE_PASSWORD environment variable not found")
        sys.exit(1)

    connection_url = sa.engine.URL.create(
        drivername="postgresql+psycopg2",
        username="postgres.jrmbgwfllqgaomytcbnb",
        password=DB_PASSWORD,
        host="aws-1-ap-south-1.pooler.supabase.com",
        port="6543",
        database="postgres"
    )
    engine = sa.create_engine(connection_url)

    client = get_openmeteo_client()
    df_raw = extract_data(client)
    df_clean = transform_data(df_raw)

    load_supabase(df_clean, engine, schema_name="air_quality", table_name="fact_air_quality")
    print("Pipeline executed successfully")


if __name__ == "__main__":
    main()