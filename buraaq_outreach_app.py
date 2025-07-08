import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets setup
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA/edit#gid=0"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
client = gspread.authorize(credentials)
sheet = client.open_by_url(GSHEET_URL).sheet1

st.set_page_config(page_title="Buraaq Outreach App", layout="centered")

# Sidebar name input saved in session_state
st.sidebar.title("Your Identity")
if "your_name" not in st.session_state:
    st.session_state["your_name"] = ""
your_name = st.sidebar.text_input("Enter Your Name", st.session_state["your_name"])
st.session_state["your_name"] = your_name

st.title("📩 Buraaq Outreach Entry Form")
st.markdown("Fill in the outreach details below:")

with st.form("outreach_form"):
    email = st.text_input("Client Email").strip()
    reference = st.text_input("Reference (Instagram / YouTube / etc)").strip()
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not your_name or not email or not reference:
            st.warning("Please fill in all fields.")
        else:
            all_emails = sheet.col_values(3)  # Column C
            if email in all_emails:
                st.error("⚠️ This email already exists in the sheet.")
            else:
                next_row = len(all_emails) + 1
                sheet.update(f"B{next_row}", your_name)
                sheet.update(f"C{next_row}", email)
                sheet.update(f"F{next_row}", reference)
                st.success("✅ Submitted successfully!")

                st.experimental_rerun()
