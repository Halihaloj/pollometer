import streamlit as st
import pandas as pd

# Setup web page layout
st.set_page_config(page_title="pollometeret", page_icon="🌱", layout="wide")
st.title("🌱 Pollometeret - Københavns samlede pollendata")

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
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Observationer", value=len(filtered_df))
with col2:
    if not filtered_df.empty and "concentration" in filtered_df.columns:
        # We prepare the numeric concentration here so we can reuse it for metrics and graphs
        filtered_df["numeric_concentration"] = pd.to_numeric(
            filtered_df["concentration"].astype(str).str.extract(r'(\d+)', expand=False), 
            errors='coerce'
        )
        max_val = filtered_df["numeric_concentration"].max()
        st.metric(label="Højest målte koncentration", value=int(max_val) if pd.notna(max_val) else 0)
    else:
        st.metric(label="Højest målte koncentration", value=0)

st.write("---")
st.subheader("📊 Visualisering af pollenniveauer")

if filtered_df.empty:
    st.info("Ingen data tilgængelig til at tegne en graf.")
else:
    # Look for a date/time column automatically (handles common variations like 'date', 'dato', 'timestamp')
    date_col = next((col for col in filtered_df.columns if col.lower() in ['date', 'dato', 'timestamp', 'tid']), None)

    if date_col:
        # OPTION A: Timeline Line Chart (If date column exists)
        # Ensure dates are parsed correctly and sorted chronologically
        graph_df = filtered_df.dropna(subset=[date_col, "numeric_concentration"]).copy()
        graph_df[date_col] = pd.to_datetime(graph_df[date_col])
        graph_df = graph_df.sort_values(by=date_col)

        # If they are looking at all pollen types, split lines by pollen type. Otherwise split by location.
        color_by = "pollen_type" if selected_pollen == "Alle pollentyper" else "location"

        st.line_chart(
            data=graph_df,
            x=date_col,
            y="numeric_concentration",
            color=color_by,
            use_container_width=True
        )
    else:
        # OPTION B: Overview Bar Chart (Fallback if there is no date column)
        # Group by pollen type or location to show average levels
        group_by = "pollen_type" if selected_pollen == "Alle pollentyper" else "location"
        
        summary_df = (
            filtered_df.groupby(group_by)["numeric_concentration"]
            .mean()
            .reset_index()
            .sort_values(by="numeric_concentration", ascending=False)
        )
        
        st.bar_chart(
            data=summary_df,
            x=group_by,
            y="numeric_concentration",
            use_container_width=True
        )

st.write("---")
st.subheader(f"📋 Viser resultater for: {selected_location} — {selected_pollen}")

if filtered_df.empty:
    st.warning("Ingen data fundet for denne kombination.")
else:
    # Drop our temporary numeric column before displaying the raw data table to the user
    display_df = filtered_df.drop(columns=["numeric_concentration"], errors="ignore")
    st.dataframe(display_df, use_container_width=True)