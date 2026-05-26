import os
import webbrowser
import requests

# 1. INDSÆT DINE API-OPLYSNINGER HER:
API_KEY = "DIN_API_NØGLE_HER"
# Indsæt den præcise API-URL du har fået oplyst (f.eks. 'https://api.astma-allergi.dk/v1/pollen')
API_URL = "HTTPS://URL_TIL_DERES_API_HER" 

def hent_pollen_fra_api():
    print("Henter live-data via Astma-Allergi API...")
    
    # Send din API-key med i anmodningen (typisk i "headers" eller som "params")
    headers = {
        "Authorization": f"Bearer {API_KEY}", # Eller "X-API-Key": API_KEY alt efter deres krav
        "Accept": "application/json"
    }
    
    try:
        respons = requests.get(API_URL, headers=headers, timeout=10)
        
        if respons.status_code == 200:
            json_data = respons.json() # Python omdanner automatisk JSON til en dictionary
            
            # -----------------------------------------------------------------
            # OBS: Du skal måske rette linjerne herunder, så de passer til 
            # præcis de navne (keys), der ligger i dit JSON-svar.
            # -----------------------------------------------------------------
            # Eksempel: Hvis JSON ser sådan ud: {"graes": 42}
            pollen_tal = json_data.get("graes", 0) 
            
            return "Græspollen", pollen_tal
            
        else:
            print(f"Fejl fra API (Statuskode: {respons.status_code}). Bruger test-data.")
    except Exception as e:
        print(f"Kunne ikke forbinde til API: {e}. Bruger test-data.")
        
    return "Græspollen (Test-data)", 15


# --- HOVEDPROGRAMMET (Samme princip som før) ---

# 1. Hent tallet via JSON API
DAGENS_POLLEN_TYPE, POLLEN_VALUE = hent_pollen_fra_api()
DAGENS_POLLEN_TAL = str(POLLEN_VALUE)

# 2. Find stier
skabelon_sti = os.path.abspath("templates/index.html")
output_sti = os.path.abspath("templates/live_pollometer.html")

# 3. Læs HTML
with open(skabelon_sti, "r", encoding="utf-8") as fil:
    html_indhold = fil.read()

# 4. Erstat pladsholdere
html_indhold = html_indhold.replace("{{ POLLEN_TYPE }}", DAGENS_POLLEN_TYPE)
html_indhold = html_indhold.replace("{{ POLLEN_TAL }}", DAGENS_POLLEN_TAL)

# 5. Gem ny HTML
with open(output_sti, "w", encoding="utf-8") as fil:
    fil.write(html_indhold)

# 6. Åbn i browser
url = f"file://{output_sti}"
print(f"Åbner pollometer med data: {DAGENS_POLLEN_TYPE} = {DAGENS_POLLEN_TAL}")
webbrowser.open(url)