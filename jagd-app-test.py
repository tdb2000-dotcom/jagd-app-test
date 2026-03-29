import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# --- KONFIGURATION ---
SHEET_NAME = "jagd-app-test"

# --- VERBINDUNG ---
def connect_to_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # Secret als Dict laden und private_key \n fixen
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")
        return None

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Jagd-Protokoll", page_icon="🦌")
st.title("🦌 Digitales Jagdbuch")

st.divider()

# --- FORMULAR ---
with st.form("jagd_form", clear_on_submit=True):
    st.subheader("Neuer Eintrag")

    col1, col2 = st.columns(2)
    datum = col1.date_input("Datum", datetime.now())
    uhrzeit = col2.time_input("Uhrzeit", datetime.now())

    col3, col4 = st.columns(2)
    wildart = col3.selectbox("Wildart", [
        "Reh", "Hirsch", "Wildschwein", "Fuchs",
        "Dachs", "Hase", "Fasan", "Ente", "Sonstiges"
    ])
    kilogramm = col4.number_input("Kilogramm", min_value=0.0, step=0.1, format="%.1f")

    notizen = st.text_area("Notizen", placeholder="Besondere Vorkommnisse, Beobachtungen...")

    submit = st.form_submit_button("💾 Eintrag speichern", use_container_width=True)

# --- SPEICHERN ---
if submit:
    sheet = connect_to_sheet()
    if sheet:
        try:
            with st.spinner("Speichere Eintrag..."):
                sheet.append_row([
                    str(datum),
                    str(uhrzeit),
                    wildart,
                    str(kilogramm),
                    notizen
                ])
            st.success("✅ Waidmannsheil! Eintrag gespeichert.")
            st.balloons()
        except Exception as e:
            st.error(f"Speicherfehler: {e}")

st.divider()

# --- LETZTE EINTRÄGE ---
st.subheader("Letzte Erlegungen")

sheet = connect_to_sheet()
if sheet:
    try:
        with st.spinner("Lade Daten..."):
            data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.table(df.tail(5).iloc[::-1])
        else:
            st.info("Noch keine Einträge vorhanden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")