import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# -------- Google Sheets Setup --------
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA"
DATA_SHEET_NAME = "Outreach Data"
SETTINGS_SHEET_NAME = "Settings"

@st.cache_resource(ttl=3600)
def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    return client

def email_exists(email):
    client = get_gsheet_client()
    sheet = client.open_by_url(GSHEET_URL).worksheet(DATA_SHEET_NAME)
    records = sheet.get_all_values()
    emails = [row[2].strip().lower() for row in records[1:] if len(row) > 2 and row[2].strip()]
    return email.lower() in emails

def save_outreach_entry(entry):
    client = get_gsheet_client()
    sheet = client.open_by_url(GSHEET_URL).worksheet(DATA_SHEET_NAME)
    records = sheet.get_all_values()

    for idx, row in enumerate(records[1:], start=2):  # Skip header
        name_cell = row[1] if len(row) > 1 else ""
        email_cell = row[2] if len(row) > 2 else ""
        reference_cell = row[5] if len(row) > 5 else ""

        if name_cell == "" and email_cell == "" and reference_cell == "":
            sheet.update(f"B{idx}", [[entry["Your Name"]]])
            sheet.update(f"C{idx}", [[entry["Email"]]])
            sheet.update(f"F{idx}", [[entry["Reference"]]])
            return

    # Add to next available row if no empty one found
    next_row = len(records) + 1
    sheet.update(f"B{next_row}", [[entry["Your Name"]]])
    sheet.update(f"C{next_row}", [[entry["Email"]]])
    sheet.update(f"F{next_row}", [[entry["Reference"]]])

def load_your_name():
    client = get_gsheet_client()
    try:
        sheet = client.open_by_url(GSHEET_URL).worksheet(SETTINGS_SHEET_NAME)
        records = sheet.get_all_records()
        if records and "Your Name" in records[0]:
            return records[0]["Your Name"]
        else:
            return ""
    except gspread.WorksheetNotFound:
        sheet = client.open_by_url(GSHEET_URL).add_worksheet(title=SETTINGS_SHEET_NAME, rows=5, cols=2)
        sheet.append_row(["Your Name"])
        return ""

def save_your_name(name):
    client = get_gsheet_client()
    try:
        sheet = client.open_by_url(GSHEET_URL).worksheet(SETTINGS_SHEET_NAME)
        sheet.clear()
        sheet.append_row(["Your Name"])
        sheet.append_row([name])
    except gspread.WorksheetNotFound:
        sheet = client.open_by_url(GSHEET_URL).add_worksheet(title=SETTINGS_SHEET_NAME, rows=5, cols=2)
        sheet.append_row(["Your Name"])
        sheet.append_row([name])

# -------- Streamlit App --------
def main():
    st.set_page_config(page_title="Buraaq Studios Outreach", page_icon="🎥")
    st.title("🎯 Buraaq Studios Outreach Site")

    your_name = load_your_name()

    # Sidebar: Name settings
    st.sidebar.header("🔒 Your Name Settings")
    name_input_sidebar = st.sidebar.text_input("Enter your name", value=your_name)
    if st.sidebar.button("💾 Save Your Name"):
        save_your_name(name_input_sidebar.strip())
        st.success("✅ Your name has been saved.")
        st.rerun()

    # Session state to reset fields
    if "email_input" not in st.session_state:
        st.session_state.email_input = ""
    if "reference_input" not in st.session_state:
        st.session_state.reference_input = ""
    if "name_input" not in st.session_state:
        st.session_state.name_input = ""

    # Main form
    with st.form("Add New Outreach Entry"):
        email = st.text_input("Email / Any Contact Info", value=st.session_state.email_input, key="email_input_key")
        reference = st.text_input("Reference", value=st.session_state.reference_input, key="reference_input_key")
        name = st.text_input("Your Name (leave blank to use saved name)", value=st.session_state.name_input, key="name_input_key")
        submitted = st.form_submit_button("📩 Add Entry")

        if submitted:
            entry_name = name.strip() if name.strip() else your_name
            if not entry_name:
                st.error("⚠️ Please provide your name or save it in the sidebar.")
            elif not email.strip():
                st.error("⚠️ Email is required.")
            elif email_exists(email.strip()):
                st.error("❌ This email already exists in the sheet.")
            else:
                entry = {
                    "Date": datetime.date.today().strftime("%Y-%m-%d"),
                    "Email": email.strip(),
                    "Reference": reference.strip(),
                    "Your Name": entry_name
                }
                save_outreach_entry(entry)
                st.success("✅ Entry added successfully!")

                # Reset form fields
                st.session_state.email_input = ""
                st.session_state.reference_input = ""
                st.session_state.name_input = ""
                st.rerun()

if __name__ == "__main__":
    main()
