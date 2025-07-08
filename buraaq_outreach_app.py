import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# -------------------- CONFIG --------------------
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA/edit#gid=0"
SHEET_NAME = "Outreach"
SETTINGS_SHEET_NAME = "Settings"

# -------------------- AUTHENTICATION --------------------
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = gspread.authorize(credentials)

# -------------------- HELPER FUNCTIONS --------------------
def load_your_name():
    try:
        sheet = client.open_by_url(GSHEET_URL).worksheet(SETTINGS_SHEET_NAME)
        name_cell = sheet.acell("A1").value
        return name_cell if name_cell else ""
    except:
        return ""

def save_your_name(name):
    sheet = client.open_by_url(GSHEET_URL).worksheet(SETTINGS_SHEET_NAME)
    sheet.update_acell("A1", name)

def email_exists(email):
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)
    existing_emails = sheet.col_values(3)  # Column C
    return email.strip().lower() in [e.strip().lower() for e in existing_emails]

def get_first_empty_row(sheet):
    col_b = sheet.col_values(2)
    for idx, val in enumerate(col_b, start=1):
        if not val.strip():
            return idx
    return len(col_b) + 1

def save_outreach_entry(entry):
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)
    idx = get_first_empty_row(sheet)
    sheet.update(f"B{idx}", entry["Your Name"])         # Column B
    sheet.update(f"C{idx}", entry["Client Email"])      # Column C
    sheet.update(f"F{idx}", entry["Client Reference"])  # Column F

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Buraaq Outreach App", layout="centered")

st.title("📤 Buraaq Outreach Entry")

if "your_name" not in st.session_state:
    st.session_state.your_name = load_your_name()

with st.form("outreach_form"):
    your_name = st.text_input("Your Name", value=st.session_state.your_name)
    client_email = st.text_input("Client Email")
    client_reference = st.text_area("Client Reference (Instagram, YouTube, etc.)")

    submitted = st.form_submit_button("Submit")

    if submitted:
        if not your_name or not client_email or not client_reference:
            st.warning("Please fill in all fields.")
        elif email_exists(client_email):
            st.error("❌ Email already exists in the sheet.")
        else:
            st.session_state.your_name = your_name
            save_your_name(your_name)
            save_outreach_entry({
                "Your Name": your_name,
                "Client Email": client_email,
                "Client Reference": client_reference
            })
            st.success("✅ Submitted successfully!")
            st.experimental_rerun()
