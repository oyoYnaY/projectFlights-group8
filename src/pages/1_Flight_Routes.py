import streamlit as st
import sqlite3
import pandas as pd
import altair as alt


def load_data(query):
    with sqlite3.connect("flights_database.db") as conn:
        df = pd.read_sql_query(query, conn)
    return df


st.title("Flight Routes \U0001F6E9")

st.sidebar.header("Select Route")
# Query to get unique airport codes from the flights table
airport_query = """
SELECT DISTINCT faa 
FROM airports
ORDER BY faa
"""
df_airports = load_data(airport_query)
airport_list = df_airports['faa'].tolist()

origin = st.sidebar.selectbox(
    "Choose Departure Airport (origin)", options=airport_list, index=0)
dest = st.sidebar.selectbox(
    "Choose Arrival Airport (destination)", options=airport_list, index=1)

st.write(f"**Selected Route**: {origin} \u27A1 {dest}")

# Query flight statistics for this route
route_query = f"""
SELECT 
    COUNT(*) as flight_count,
    AVG(dep_delay) as avg_dep_delay,
    AVG(arr_delay) as avg_arr_delay,
    AVG(distance) as avg_distance
FROM flights
WHERE origin = '{origin}'
  AND dest = '{dest}';
"""
df_route_stats = load_data(route_query)

if df_route_stats['flight_count'][0] > 0:
    flight_count = int(df_route_stats['flight_count'][0])
    avg_dep_delay = round(df_route_stats['avg_dep_delay'][0], 2)
    avg_arr_delay = round(df_route_stats['avg_arr_delay'][0], 2)
    avg_distance = round(df_route_stats['avg_distance'][0], 2)

    st.subheader("Route Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Number of Flights", flight_count)
    col2.metric("Avg. Departure Delay (min)", avg_dep_delay)
    col3.metric("Avg. Arrival Delay (min)", avg_arr_delay)
    col4.metric("Avg. Distance (miles)", avg_distance)

    # Maybe show a histogram of departure delays for this route
    hist_query = f"""
    SELECT dep_delay
    FROM flights
    WHERE origin = '{origin}' AND dest = '{dest}'
      AND dep_delay IS NOT NULL
    """
    df_hist = load_data(hist_query)

    if not df_hist.empty:
        chart = (
            alt.Chart(df_hist)
            .mark_bar(color="#f28500")
            .encode(
                alt.X("dep_delay:Q", bin=alt.Bin(maxbins=30),
                      title="Departure Delay (min)"),
                y='count()'
            )
            .properties(
                width=600,
                height=400,
                title="Distribution of Departure Delays"
            )
        )
        st.altair_chart(chart, use_container_width=True)

else:
    st.warning("No flights found for the selected route.")
