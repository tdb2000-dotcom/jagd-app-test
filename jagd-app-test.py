import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import json  # Ganz wichtig für diesen Weg!

# --- KONFIGURATION ---
SHEET_NAME = "jagd-app-test"

# --- VERBINDUNG ---
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Wir laden den "rohen" Text aus der Variable gcp_service_account
        info_json = json.loads(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info_json, scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")
        return None

# --- RESTLICHER CODE (Formular & Anzeige) ---
st.set_page_config(page_title="Jagd-Protokoll", page_icon="🦌")
st.title("🦌 Digitales Jagdbuch")

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

if submit:
    sheet = connect_to_sheet()
    if sheet:
        try:
            with st.spinner('Speichere...'):
                sheet.append_row([str(datum), str(uhrzeit), wildart, str(kilogramm), notizen])
                st.success("✅ Waidmannsheil!")
                st.balloons()
        except Exception as e:
            st.error(f"Speicherfehler: {e}")

st.divider()
st.subheader("Letzte Erlegungen")
try:
    sheet = connect_to_sheet()
    if sheet:
        data = sheet.get_all_records()
        if data:
            st.table(pd.DataFrame(data).tail(5))
except:
    st.write("Warte auf Daten...")