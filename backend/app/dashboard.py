import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect("attendance.db", check_same_thread=False)

# ✅ FIXED QUERY → ONLY 1 ENTRY PER STUDENT (EARLIEST TIME)
def get_today_attendance():
    query = """
        SELECT 
            name,
            date,
            MIN(time) as time
        FROM attendance
        WHERE date = DATE('now','localtime')
        GROUP BY name, date
        ORDER BY time ASC
    """
    return pd.read_sql_query(query, conn)


def get_all_students():
    query = "SELECT DISTINCT name FROM attendance"
    df = pd.read_sql_query(query, conn)
    return df["name"].tolist()


def run():
    st.title("👨‍🏫 Teacher Dashboard")

    # -----------------------
    st.subheader("📋 Today Attendance")

    df_today = get_today_attendance()

    if df_today.empty:
        st.warning("No attendance marked yet.")
        return

    st.dataframe(df_today, use_container_width=True)

    # -----------------------
    st.subheader("❌ Absent Students")

    all_students = set(get_all_students())
    present_students = set(df_today["name"].tolist())

    absent_students = list(all_students - present_students)

    if absent_students:
        st.error(", ".join(absent_students))
    else:
        st.success("No absentees 🎉")

    # -----------------------
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Students", len(all_students))

    with col2:
        st.metric("Present Today", len(present_students))

    # -----------------------
    st.subheader("📥 Export Today's Attendance")

    csv = df_today.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"attendance_{datetime.now().date()}.csv",
        mime="text/csv"
    )