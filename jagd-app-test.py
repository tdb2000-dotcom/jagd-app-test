import streamlit as st
import gspread
from google.oauth2 import service_account
from datetime import datetime
import pandas as pd
import json

# --- KONFIGURATION ---
SHEET_NAME = "jagd-app-test"

# --- VERBINDUNG ---
def connect_to_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    try:
        # Methode: über google-auth statt oauth2client
        creds_dict = {
            "type": st.secrets["gcp_service_account"]["type"],
            "project_id": st.secrets["gcp_service_account"]["project_id"],
            "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
            "private_key": st.secrets["gcp_service_account"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["gcp_service_account"]["client_email"],
            "client_id": st.secrets["gcp_service_account"]["client_id"],
            "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
            "token_uri": st.secrets["gcp_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
        }

        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=scope
        )
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1

    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")

        # DEBUG: zeige was im private_key steckt
        try:
            key = st.secrets["gcp_service_account"]["private_key"]
            st.code(f"Key Länge: {len(key)}")
            st.code(f"Erste 60 Zeichen: {key[:60]}")
            st.code(f"Letzte 60 Zeichen: {key[-60:]}")
            st.code(f"Enthält \\\\n (escaped): {'\\\\n' in key}")
            st.code(f"Enthält echte Newlines: {chr(10) in key}")
        except Exception as e2:
            st.error(f"Debug Fehler: {e2}")

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

if submit:
    sheet = connect_to_sheet()
    if sheet:
        try:
            with st.spinner("Speichere Eintrag..."):
                sheet.append_row([str(datum), str(uhrzeit), wildart, str(kilogramm), notizen])
            st.success("✅ Waidmannsheil! Eintrag gespeichert.")
            st.balloons()
        except Exception as e:
            st.error(f"Speicherfehler: {e}")

st.divider()
st.subheader("Letzte Erlegungen")

sheet = connect_to_sheet()
if sheet:
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.table(df.tail(5).iloc[::-1])
        else:
            st.info("Noch keine Einträge vorhanden.")
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")