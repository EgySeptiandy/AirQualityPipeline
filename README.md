# Automated Air Quality Index (AQI) Data Pipeline & Live Dashboard

Proyek Data Engineering *end-to-end* yang mengekstrak data time-series kualitas udara secara otomatis, melakukan pembersihan data (*data cleansing*), dan mengunggahnya ke PostgreSQL Data Warehouse dengan logika **Upsert** yang *idempotent*. 

Pipeline ini berjalan secara kontinyu menggunakan **GitHub Actions (Cron Job)** dan divisualisasikan melalui **Streamlit Live Dashboard**.

---

## Arsitektur Sistem

'''text
[ Open-Meteo API (FlatBuffers Binary) ]
                  │
                  ▼
      [ Python ETL Pipeline ]  <─── [ GitHub Actions Cron Job (Setiap 6 Jam) ]
                  │
                  ▼
       [ Supabase PostgreSQL ] (Schema: `air_quality`, Upsert Strategy)
                  │
                  ▼
     [ Streamlit Live Dashboard ]
