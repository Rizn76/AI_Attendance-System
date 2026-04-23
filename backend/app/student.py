def run():
    import streamlit as st
    import sqlite3
    import pandas as pd

    st.title("🎓 AI Smart Attendance System")
    st.subheader("🎓 Student Portal")

    name = st.text_input("Enter Your Name")

    if name:
        conn = sqlite3.connect("attendance.db")

        # Load data
        df = pd.read_sql_query(
            "SELECT * FROM attendance WHERE name=?",
            conn,
            params=(name,)
        )

        if df.empty:
            st.warning("No records found")
            return

        # Convert date column properly
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # 🔥 REMOVE DUPLICATES (same day multiple entries)
        df_unique = df.drop_duplicates(subset=["date"])

        # Show cleaned attendance table
        st.dataframe(df_unique)

        # ✅ CORRECT ATTENDANCE %
        total_days = df["date"].nunique()       # total working days (based on DB)
        present_days = df_unique["date"].nunique()

        attendance_percent = (present_days / total_days) * 100 if total_days > 0 else 0

        st.subheader("Attendance %")
        st.success(f"{attendance_percent:.2f}%")

        conn.close()