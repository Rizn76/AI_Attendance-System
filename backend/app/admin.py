def run():
    import streamlit as st
    import sqlite3
    import pandas as pd
    from datetime import datetime

    st.title("📊 Admin Dashboard")

    conn = sqlite3.connect("attendance.db", check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM attendance", conn)

    if df.empty:
        st.warning("No data available")
        return

    df["date"] = pd.to_datetime(df["date"])
    df["date_only"] = df["date"].dt.date

    # ---------- TOTAL STATS ----------
    st.subheader("📌 Overall Stats")

    col1, col2 = st.columns(2)
    col1.metric("Total Students", df["name"].nunique())
    col2.metric("Total Records", len(df))

    # ---------- DAILY TREND ----------
    st.subheader("📈 Attendance Trend")

    daily = df.groupby("date_only")["name"].nunique()
    st.line_chart(daily)

    # ---------- ATTENDANCE % ----------
    st.subheader("📊 Attendance %")

    total_days = df["date_only"].nunique()

    attendance = (
        df.groupby("name")["date_only"]
        .nunique()
        .reset_index(name="days_present")
    )

    attendance["attendance_%"] = (
        attendance["days_present"] / total_days * 100
    ).round(2)

    st.dataframe(attendance)

    # ---------- LOW ATTENDANCE ----------
    st.subheader("⚠️ Low Attendance (<75%)")

    low = attendance[attendance["attendance_%"] < 75]

    if low.empty:
        st.success("No defaulters 🎉")
    else:
        st.dataframe(low)

    # ---------- EXPORT ----------
    st.subheader("⬇️ Export Report")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        data=csv,
        file_name="attendance.csv",
        mime="text/csv"
    )