import csv
import sqlite3

# 1. Forbind til databasen
conn = sqlite3.connect("pollen_data.db")
cursor = conn.cursor()

# 2. Opret tabellen med de rigtige kolonner (alle som TEXT i første omgang)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS pollen (
    date TEXT,
    time TEXT,
    location TEXT,
    pollen_type TEXT,
    concentration TEXT
)
"""
)

# 3. Åbn CSV-filen og læs rækkerne ind
with open("copenhagen_pollen_data_regex_v2.csv", mode="r", encoding="utf-8") as fil:
    csv_læser = csv.reader(fil)

    # Spring over overskrifterne (første række i CSV-filen)
    ved_overskrift = next(csv_læser)

    # Indsæt alle rækker i databasen
    cursor.executemany(
        "INSERT INTO pollen (date, time, location, pollen_type, concentration) VALUES (?, ?, ?, ?, ?)",
        csv_læser,
    )

# Gem ændringerne og luk
conn.commit()
print("Tabellen er oprettet og fyldt med data!")
conn.close()