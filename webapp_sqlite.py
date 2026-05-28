import streamlit as st
import pandas as pd

# Setup web page layout
st.set_page_config(page_title="pollometeret", page_icon="🌱", layout="wide")
st.title("🌱 Pollometeret - Overblik over de Københavnske pollendata")

# Connection to SQLite db
conn = st.connection("sqlite", type="sql", url="sqlite:///pollen_data.db")

# ocation sidebar
st.sidebar.header("Filtrer pollendata")

# Fetch locations to build dropdown menu
try:
    location_query = conn.query('SELECT DISTINCT "location" FROM pollen;')
    location_list = location_query["location"].dropna().tolist()
except Exception:
    # Fallback in case DB has different name
    st.error("Could not find table named 'pollen' in database.")
    st.stop()

selected_location = st.sidebar.selectbox("Vælg lokation:", ["Alle lokationer"] + location_list)

# SQL query based on selected location
if selected_location == "Alle lokationer":
    sql_query = 'SELECT * FROM pollen;'
else:
    sql_query = f'SELECT * FROM pollen WHERE "location" = \'{selected_location}\';'

# Fetch table from SQLite, cache turned off
df = conn.query(sql_query, ttl="0")

# Display metric boxes at top of page
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Antal målinger for valgte lokation:", value=len(df))
with col2:
    # Clean up Concentration to numeric just in case there are text strings left
    numeric_concentration = pd.to_numeric(df["concentration"].astype(str).str.extract(r'(\d+)', expand=False), errors='coerce')
    st.metric(label="Højest målte koncentration:", value=int(numeric_concentration.max()) if not numeric_concentration.isna().all() else 0)

# Print interactive data table onto the webpage
st.subheader(f"Viser resultater for {selected_location}")
st.dataframe(df, use_container_width=True)