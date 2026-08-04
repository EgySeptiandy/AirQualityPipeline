import os
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Air Quality Monitoring Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# Database Connection and Data Fetching
@st.cache_data(ttl=300)
def load_data():
    DB_PASSWORD = os.environ.get("SUPABASE_PASSWORD")
    if not DB_PASSWORD:
        return pd.DataFrame(), "SUPABASE_PASSWORD environtment variable is missing"
    
    try:
        connection_url = sa.engine.URL.create(
            drivername="postgresql+psycopg2",
            username="postgres.jrmbgwfllqgaomytcbnb",
            password=DB_PASSWORD,
            host="aws-1-ap-south-1.pooler.supabase.com",
            port=6543,
            database="postgres"
        )
        engine = sa.create_engine(connection_url)

        query = "SELECT * FROM air_quality.fact_air_quality ORDER BY time DESC LIMIT 500;"
        df = pd.read_sql(query, engine)
        
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

def get_aqi_status(pm25_val):
    if pm25_val <= 12.0:
        return "Baik (Good)", "🟢"
    elif pm25_val <= 35.4:
        return "Sedang (Moderate)", "🟡"
    elif pm25_val <= 55.4:
        return "Sensitif (Unhealthy for Sensitive)", "🟠"
    else:
        return "Tidak Sehat (Unhealthy)", "🔴"

# Main Dashboard UI

st.title("Automated Air Quality Index (AQI) Live Dashboard")
st.caption("Real-Time Automated Time-Series Pipeline via Github Actions & Supabase")

df, error_msg = load_data()

if error_msg:
    st.error(f" Connection/Query Error: {error_msg}")
elif df.empty:
    st.warning("`air_quality.fact_air_quality` table is empty")
else:

    # Cities Latest Metric Cards
    st.subheader("Latest Air Quality Status (PM 2.5)")
    latest_time = df['time'].max()
    df_latest = df[df['time'] == latest_time]

    cols = st.columns(len(df_latest))
    for idx, (_, row) in enumerate(df_latest.iterrows()):
        status, emoji = get_aqi_status(row['pm2_5'])
        with cols[idx]:
            st.metric(
                label=f"{emoji} {row['city_name']}",
                value=f"{row['pm2_5']:.1f} µg/m³",
                delta=f"PM10: {row['pm10']:.1f}"
            )
            st.caption(f"Status: **{status}**")

    st.markdown("---")

    # Cities Trend Chart
    st.subheader("Air Pollution Trend (PM2.5) for the last 3 days")

    selected_cities = st.multiselect(
        "Choose City:",
        options=df['city_name'].unique(),
        default=df['city_name'].unique()
    )

    df_filtered = df[df['city_name'].isin(selected_cities)]

    fig = px.line(
        df_filtered,
        x='time',
        y='pm2_5',
        color='city_name',
        title='PM2.5 (µg/m³) over Time',
        labels={'time': 'Time (WIB)', 'pm2_5': 'PM2.5 (µg/m³)', 'city_name': 'City'}
    )
    st.plotly_chart(fig, width='stretch')

    # Raw Data Expander
    with st.expander("View Raw Data (Last 50 Rows)"):
        st.dataframe(df.head(50), width='stretch')