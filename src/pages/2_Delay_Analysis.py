import streamlit as st
import sqlite3
import pandas as pd
import altair as alt


def load_data(query):
    with sqlite3.connect("flights_database.db") as conn:
        df = pd.read_sql_query(query, conn)
    return df


st.title("Delay Analysis \U0001F551")

st.markdown("""
In this section, we'll explore potential causes or patterns behind flight delays, 
such as **time of day** and **weather** factors.
""")

# --- 1) Delays by Hour of Day ---
st.subheader("Delays by Hour of Day")

query_delays_by_hour = """
SELECT dep_time_hour AS hour,
       AVG(dep_delay) AS avg_dep_delay,
       AVG(arr_delay) AS avg_arr_delay
FROM (
    SELECT strftime('%H', printf('%04d', dep_time)) AS dep_time_hour,
           dep_delay,
           arr_delay
    FROM flights
    WHERE dep_time IS NOT NULL
      AND dep_delay IS NOT NULL
      AND arr_delay IS NOT NULL
      AND origin IN ('JFK','LGA','EWR')
)
GROUP BY dep_time_hour
ORDER BY dep_time_hour;
"""
df_delays_by_hour = load_data(query_delays_by_hour)

if not df_delays_by_hour.empty:
    chart_hour = (
        alt.Chart(df_delays_by_hour)
        .transform_fold(
            ["avg_dep_delay", "avg_arr_delay"],
            as_=["DelayType", "DelayValue"]
        )
        .mark_line(point=True)
        .encode(
            x=alt.X("hour:N", title="Departure Hour (Local)"),
            y=alt.Y("DelayValue:Q", title="Average Delay (min)"),
            color="DelayType:N",
            tooltip=["hour:N", "DelayType:N", "DelayValue:Q"]
        )
        .properties(
            width=700,
            height=400,
            title="Average Departure and Arrival Delays by Hour of Day"
        )
    )
    st.altair_chart(chart_hour, use_container_width=True)
else:
    st.warning("No delay data available by hour.")

# --- 2) Weather Influence (optional example) ---
st.subheader("Weather Influence on Delays")

st.markdown("""
*Below is a simplified example showing how you might start examining weather variables, 
such as wind speed or precipitation, versus average delays. You can expand upon this 
with more robust correlation or regression analyses.*
""")

# Example: average departure delay by wind speed (this is just illustrative)
query_weather_delay = """
SELECT w.wind_speed, AVG(f.dep_delay) AS avg_dep_delay
FROM flights f
JOIN weather w ON f.origin = w.origin
   AND f.year = w.year
   AND f.month = w.month
   AND f.day = w.day
   AND f.hour = w.hour
WHERE f.dep_delay IS NOT NULL
  AND w.wind_speed IS NOT NULL
GROUP BY w.wind_speed
ORDER BY w.wind_speed;
"""
df_weather_delay = load_data(query_weather_delay)

if not df_weather_delay.empty:
    scatter_chart = (
        alt.Chart(df_weather_delay)
        .mark_circle(size=60, color="#8c564b")
        .encode(
            x=alt.X("wind_speed:Q", title="Wind Speed (m/s or knots)"),
            y=alt.Y("avg_dep_delay:Q", title="Average Departure Delay (min)"),
            tooltip=["wind_speed", "avg_dep_delay"]
        )
        .properties(
            width=700,
            height=400,
            title="Average Departure Delay vs. Wind Speed"
        )
        .interactive()
    )
    st.altair_chart(scatter_chart, use_container_width=True)
else:
    st.info("No matching weather data found for delay analysis.")
