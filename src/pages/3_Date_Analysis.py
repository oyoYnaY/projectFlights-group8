import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime


def load_data(query):
    with sqlite3.connect("flights_database.db") as conn:
        df = pd.read_sql_query(query, conn)
    return df


st.title("Date-based Analysis \U0001F4C5")

st.markdown("Pick a date to see relevant flight statistics from NYC airports.")

# A date input widget
selected_date = st.date_input("Select Date", value=datetime(2023, 1, 1),
                              min_value=datetime(2023, 1, 1),
                              max_value=datetime(2023, 12, 31))

if selected_date:
    year_ = selected_date.year
    month_ = selected_date.month
    day_ = selected_date.day

    st.write(f"**Selected date**: {selected_date.strftime('%Y-%m-%d')}")

    # Query flights for that specific date
    date_query = f"""
    SELECT 
        COUNT(*) as flight_count,
        AVG(dep_delay) as avg_dep_delay,
        AVG(arr_delay) as avg_arr_delay
    FROM flights
    WHERE year = {year_}
      AND month = {month_}
      AND day = {day_}
      AND origin IN ('JFK','LGA','EWR');
    """
    df_date_stats = load_data(date_query)

    flight_count = int(
        df_date_stats['flight_count'][0]) if not df_date_stats.empty else 0
    avg_dep_delay = round(
        df_date_stats['avg_dep_delay'][0], 2) if not df_date_stats.empty else None
    avg_arr_delay = round(
        df_date_stats['avg_arr_delay'][0], 2) if not df_date_stats.empty else None

    if flight_count > 0:
        col1, col2, col3 = st.columns(3)
        col1.metric("Number of Flights", flight_count)
        col2.metric("Avg. Departure Delay (min)", avg_dep_delay)
        col3.metric("Avg. Arrival Delay (min)", avg_arr_delay)

        # Example: breakdown by airline for that date
        airline_query = f"""
        SELECT f.carrier, a.name AS airline_name, COUNT(*) as flight_count
        FROM flights f
        JOIN airlines a ON f.carrier = a.carrier
        WHERE f.year = {year_}
          AND f.month = {month_}
          AND f.day = {day_}
          AND f.origin IN ('JFK','LGA','EWR')
        GROUP BY f.carrier
        ORDER BY flight_count DESC;
        """
        df_airline_date = load_data(airline_query)

        if not df_airline_date.empty:
            date_bar = (
                alt.Chart(df_airline_date)
                .mark_bar()
                .encode(
                    x=alt.X("flight_count:Q", title="Number of Flights"),
                    y=alt.Y("airline_name:N", sort="-x", title="Airline"),
                    tooltip=["airline_name", "flight_count"]
                )
                .properties(
                    width=700,
                    height=400,
                    title="Flights by Airline on Selected Date"
                )
            )
            st.altair_chart(date_bar, use_container_width=True)
        else:
            st.info("No flights found by airline for this date.")

    else:
        st.warning("No flights found on this date.")
