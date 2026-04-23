import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Attendance System", layout="wide")

# ---------- CENTER TITLE ----------
st.markdown(
    """
    <h1 style='text-align: center;'>
    🎓 AI Smart Attendance System
    </h1>
    """,
    unsafe_allow_html=True
)

# ---------- IMPORT PAGES ----------
import realtime
import dashboard
import student
import admin

# ---------- SIDEBAR ----------
page = st.sidebar.selectbox(
    "Select Page",
    ["Realtime Attendance", "Teacher Dashboard", "Student Portal", "Admin Dashboard"]
)

# ---------- ROUTING ----------
if page == "Realtime Attendance":
    realtime.run()

elif page == "Teacher Dashboard":
    dashboard.run()

elif page == "Student Portal":
    student.run()

elif page == "Admin Dashboard":
    admin.run()