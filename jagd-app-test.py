import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# --- KONFIGURATION ---
# Wir brauchen JSON_FILE nicht mehr, da wir st.secrets nutzen!
SHEET_NAME = "jagd-app-test"


# --- VERBINDUNG ZU GOOGLE SHEETS ---
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Nutzt die Daten aus dem Streamlit-Tresor (Secrets)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets, scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


# --- APP INTERFACE ---
st.set_page_config(page_title="Jagd-Protokoll", page_icon="🦌")
st.title("🦌 Digitales Jagdbuch")

# Formular-Bereich
with st.form("jagd_form", clear_on_submit=True):
    st.subheader("Neuer Eintrag")

    col1, col2 = st.columns(2)
    datum = col1.date_input("Datum", datetime.now())
    uhrzeit = col2.time_input("Uhrzeit", datetime.now())

    col3, col4 = st.columns(2)
    wildart = col3.selectbox("Wildart", ["Reh", "Hirsch", "Wildschwein", "Fuchs", "Dachs", "Sonstiges"])
    kilogramm = col4.number_input("Kilogramm", min_value=0.0, step=0.1)

    notizen = st.text_area("Notizen")

    submit = st.form_submit_button("Eintrag speichern")

# --- SPEICHER-LOGIK ---
if submit:
    try:
        with st.spinner('Speichere Daten...'):
            sheet = connect_to_sheet()
            neue_zeile = [
                str(datum),
                str(uhrzeit),
                wildart,
                kilogramm,
                notizen
            ]
            sheet.append_row(neue_zeile)
            st.success("✅ Gratuliere zu deiner Jagd!")
            st.balloons()
    except Exception as e:
        st.error(f"Fehler: {e}")

# --- ANZEIGE DER LETZTEN EINTRÄGE ---
st.divider()
st.subheader("Letzte Erlegungen")

try:
    sheet = connect_to_sheet()
    # Holt alle Daten aus dem Sheet
    data = sheet.get_all_records()
    if data:
        # Erstellt eine Tabelle (DataFrame) und zeigt die letzten 5 Zeilen
        df = pd.DataFrame(data)
        st.table(df.tail(5))
    else:
        st.info("Noch keine Einträge im Sheet gefunden.")
except:
    st.write("Lade Daten...")