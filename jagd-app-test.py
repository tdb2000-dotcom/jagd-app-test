import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- KONFIGURATION ---
JSON_FILE = "jagd-app-test-86ac50eaf539.json"
SHEET_NAME = "jagd-app-test"


# --- VERBINDUNG ZU GOOGLE SHEETS ---
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


# --- APP INTERFACE ---
st.set_page_config(page_title="Jagd-Protokoll", page_icon="🦌")
st.title("🦌 Digitales Jagdbuch")


# Funktion zum Zurücksetzen des Formulars
def reset_form():
    st.session_state["datum"] = datetime.now()
    st.session_state["uhrzeit"] = datetime.now().time()
    st.session_state["wildart"] = "Reh"
    st.session_state["kg"] = 0.0
    st.session_state["notizen"] = ""


# Formular-Start
with st.form("jagd_form", clear_on_submit=True):
    st.subheader("Neuer Eintrag")

    col1, col2 = st.columns(2)
    datum = col1.date_input("Datum", datetime.now(), key="f_datum")
    uhrzeit = col2.time_input("Uhrzeit", datetime.now(), key="f_uhrzeit")

    col3, col4 = st.columns(2)
    wildart = col3.selectbox("Wildart", ["Reh", "Hirsch", "Wildschwein", "Fuchs", "Dachs", "Sonstiges"], key="f_wild")
    kilogramm = col4.number_input("Kilogramm", min_value=0.0, step=0.1, key="f_kg")

    notizen = st.text_area("Notizen", key="f_notiz")

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

            # Neue Erfolgsmeldung
            st.success("✅ Gratuliere zu deiner Jagd!")
            st.balloons()

            # Da 'clear_on_submit=True' oben im Formular steht,
            # werden die Felder beim nächsten Laden automatisch leer sein.

    except Exception as e:
        st.error(f"Fehler: Bitte prüfe die Google Sheet Freigabe. Details: {e}")