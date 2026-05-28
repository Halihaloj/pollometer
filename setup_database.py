import csv
import re
import sqlite3

# 1. Forbind til databasen og slå Foreign Keys til
conn = sqlite3.connect("pollen_data.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# 2. Opret info-tabellen først
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS pollen_info (
    pollen_type TEXT PRIMARY KEY,
    saeson_top TEXT,
    symptomer TEXT,
    gode_raad TEXT
)
"""
)

info_data = [
    (
        "Grass",
        "Juni - Juli",
        "Kløende øjne, nysen, løbende næse, astma",
        "Slå ikke græs selv, skyl håret inden sengetid",
    ),
    (
        "Birch",
        "April - Maj",
        "Kraftig nysen, kløe i øjnene, krydsallergi (f.eks. nødder/æbler)",
        "Hold vinduer lukkede i dagtimerne, brug solbriller udendørs",
    ),
    (
        "Oak",
        "Maj",
        "Milde til moderate høfebersymptomer, øjenirritation",
        "Luft ud tidligt om morgenen eller sent om aftenen",
    ),
    (
        "Pine",
        "Maj - Juni",
        "Sjældent allergi (større partikler), men kan irritere øjne mekanisk",
        "Tør ikke tøj udendørs, da det gule fyrrestøv lægger sig på alt",
    ),
]
cursor.executemany(
    "INSERT OR REPLACE INTO pollen_info VALUES (?, ?, ?, ?)", info_data
)


# 3. Opret målingstabellen (Vi dropper den gamle for at bygge den rigtigt op)
cursor.execute("DROP TABLE IF EXISTS pollen")
cursor.execute(
    """
CREATE TABLE pollen_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    time TEXT,
    location TEXT,
    pollen_type TEXT,
    concentration INTEGER,
    FOREIGN KEY (pollen_type) REFERENCES pollen_info(pollen_type)
)
"""
)


# 4. En funktion i Python der renser rækkerne med REGEX inden de ryger i SQL
def clean_row(row):
    raw_date, raw_time, raw_loc, raw_type, raw_conc = row

    # Ensret dato til DD-MM-YYYY
    date_str = raw_date.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        parts = date_str.split("-")
        date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
    elif re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        date_str = date_str.replace("/", "-")
    elif "May" in date_str:
        day = re.search(r"May\s*(\d{2})", date_str).group(1)
        year = re.search(r"(\d{4})", date_str).group(1)
        date_str = f"{day}-05-{year}"
    elif "Jun" in date_str:
        day = re.search(r"Jun[e]?\s*(\d{2})", date_str).group(1)
        year = re.search(r"(\d{4})", date_str).group(1)
        date_str = f"{day}-06-{year}"

    # Rens lokationer
    loc = raw_loc.strip()
    if re.search(r"island[s]?\s?brygge", loc, re.IGNORECASE):
        loc = "Islands brygge"
    elif re.search(r"univ\.?\s*park", loc, re.IGNORECASE):
        loc = "University Park"
    elif re.search(r"nordhavn", loc, re.IGNORECASE):
        loc = "Nordhavn"
    elif re.search(r"sydhavn", loc, re.IGNORECASE):
        loc = "Sydhavn"
    elif re.search(r"ryparken", loc, re.IGNORECASE):
        loc = "Ryparken"

    # Rens pollentyper (VIGTIGT for Foreign Key!)
    p_type = raw_type.strip()
    if re.search(r"gr[a|s]ss?", p_type, re.IGNORECASE):
        p_type = "Grass"
    elif re.search(r"b[i|u]rch", p_type, re.IGNORECASE):
        p_type = "Birch"
    elif re.search(r"oak", p_type, re.IGNORECASE):
        p_type = "Oak"
    elif re.search(r"pine", p_type, re.IGNORECASE):
        p_type = "Pine"

    # Rens koncentration til et rent heltal
    conc_digits = re.sub(r"\D", "", raw_conc)
    try:
        conc = int(conc_digits)
    except ValueError:
        conc = 0

    return (date_str, raw_time.strip(), loc, p_type, conc)


# 5. Kør CSV igennem rensningen og indsæt i SQL
cleaned_rows = []
with open("copenhagen_pollen_data_regex_v2.csv", mode="r", encoding="utf-8") as fil:
    csv_læser = csv.reader(fil)
    next(csv_læser)  # Skip overskrifter

    for row in csv_læser:
        if not row or not any(row):
            continue
        cleaned_rows.append(clean_row(row))

cursor.executemany(
    "INSERT INTO pollen_measurements (date, time, location, pollen_type, concentration) VALUES (?, ?, ?, ?, ?)",
    cleaned_rows,
)

conn.commit()
conn.close()
print(
    "Succes! Al data er renset i Python og lagt fejlfrit i databasen med Foreign Key-relationer."
)