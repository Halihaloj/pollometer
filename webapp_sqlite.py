import streamlit as st
import pandas as pd

# Setup web page layout
st.set_page_config(page_title="pollometeret", page_icon="🌱", layout="wide")
st.title("🌱 Pollometeret - Københavns Pollendata")

# Connection to SQLite db
conn = st.connection("sqlite", type="sql", url="sqlite:///pollen_data.db")

# ocation sidebar
st.sidebar.header("Filtrer pollendata")

location_list = []

# Fetch locations to build dropdown menu
try:
    location_query = conn.query('SELECT DISTINCT "location" FROM pollen_measurements;')
    location_list = location_query["location"].dropna().tolist()

    pollen_query = conn.query('SELECT DISTINCT "pollen_type" FROM pollen_measurements; ')
    pollen_list = pollen_query["pollen_type"].dropna().tolist()
except Exception:
    # Fallback in case DB has different name
    st.error("Could not find table named 'pollen_measurements' in database.")
    st.stop()

selected_location = st.sidebar.selectbox("Vælg lokation:", ["Alle lokationer"] + location_list)
selected_pollen = st.sidebar.selectbox("Vælg pollen type", ["Alle pollentyper"]+pollen_list)

# SQL query based on selected location
base_query = 'SELECT * FROM pollen_measurements WHERE 1=1'
query_params = {}

# If a specific location is selected, add it to the SQL query
if selected_location != "Alle lokationer":
    base_query += ' AND "location" = :location'
    query_params["location"] = selected_location

# If a specific pollen type is selected, add it to the SQL query
if selected_pollen != "Alle pollentyper":
    base_query += ' AND "pollen_type" = :pollen_type'
    query_params["pollen_type"] = selected_pollen

    
# Fetch table from SQLite, cache turned off
filtered_df = conn.query(base_query, params=query_params, ttl="0")

# Display metric boxes at top of page
loc_col1, loc_col2 = st.columns(2)
with loc_col1:
    st.metric(label="Observationer", value=len(filtered_df))
with loc_col2:
    # Clean up Concentration to numeric just in case there are text strings left
    numeric_concentration = pd.to_numeric(filtered_df["concentration"].astype(str).str.extract(r'(\d+)', expand=False), errors='coerce')
    st.metric(label="Højest målte koncentration", value=int(numeric_concentration.max()) if not numeric_concentration.isna().all() else 0)

# Print interactive data table onto the webpage
st.subheader(f"Viser resultater for lokation: {selected_location}")
st.dataframe(filtered_df, use_container_width=True)
