import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from timezonefinder import TimezoneFinder
import streamlit as st
import geopy.distance
import base64
import datetime

# --------------------- Data Loading and Preprocessing ---------------------
# Read the airports data from the database
db_path = "../flights_database.db"
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM airports", conn)
conn.close()

# CSV_FILE_PATH is kept for backup purposes
CSV_FILE_PATH = "../data/airports.csv"

# Perform missing value inference on the airports data
tf = TimezoneFinder()
df["tzone"] = df.apply(lambda row: tf.timezone_at(lng=row["lon"], lat=row["lat"]) if pd.isnull(row["tzone"]) else row["tzone"], axis=1)
tz_mapping_dynamic = dict(df[["tzone", "tz"]].dropna().drop_duplicates().values)
df["tz"] = df.apply(lambda row: tz_mapping_dynamic.get(row["tzone"], row["tz"]) if pd.isnull(row["tz"]) else row["tz"], axis=1)
def infer_dst_from_tzone(tzone):
    if pd.isnull(tzone):
        return 'U'
    if "America/" in tzone:
        return 'A'
    elif "Europe/" in tzone:
        return 'E'
    else:
        return 'N'
df["dst"] = df.apply(lambda row: row["dst"] if pd.notnull(row["dst"]) else infer_dst_from_tzone(row["tzone"]), axis=1)
df.loc[df["tzone"] == "America/Boise", "tz"] = -7
df.loc[df["tz"] == 8, "tz"] = -8
df["tz"] = df["tz"].astype("Int64")

# --------------------- Streamlit Page Configuration ---------------------
st.set_page_config(layout="wide")
# Translation dictionary with an expanded language list including Romania
translations = {
    "language_options": ["English", "中文", "Hrvatski", "Nederlands", "Romania"],
    "project_flight_title": {
        "English": "Project Flight",
        "中文": "项目飞行",
        "Hrvatski": "Projekt Let",
        "Nederlands": "Project Vlucht",
        "Romania": "Proiect Zbor"
    },
    "select_page": {
        "English": "Select Page",
        "中文": "选择页面",
        "Hrvatski": "Odaberite stranicu",
        "Nederlands": "Selecteer pagina",
        "Romania": "Selectați pagina"
    },
    "select_language": {
        "English": "Select Language",
        "中文": "选择语言",
        "Hrvatski": "Odaberite jezik",
        "Nederlands": "Selecteer taal",
        "Romania": "Selectați limba"
    },
    "enter_departure_city": {
        "English": "Enter departure city name:",
        "中文": "输入出发城市名称:",
        "Hrvatski": "Unesite grad polaska:",
        "Nederlands": "Voer de naam van de vertrekstad in:",
        "Romania": "Introduceți numele orașului de plecare:"
    },
    "enter_arrival_city": {
        "English": "Enter arrival city name:",
        "中文": "输入到达城市名称:",
        "Hrvatski": "Unesite grad dolaska:",
        "Nederlands": "Voer de naam van de aankomststad in:",
        "Romania": "Introduceți numele orașului de sosire:"
    },
    "select_default_map_type": {
        "English": "Select Default Map Type:",
        "中文": "选择默认地图类型:",
        "Hrvatski": "Odaberite zadani tip karte:",
        "Nederlands": "Selecteer standaard kaarttype:",
        "Romania": "Selectați tipul implicit al hărții:"
    },
    "select_time_zone": {
        "English": "Select a Time Zone:",
        "中文": "选择时区:",
        "Hrvatski": "Odaberite vremensku zonu:",
        "Nederlands": "Selecteer een tijdzone:",
        "Romania": "Selectați o zonă de timp:"
    },
    "nearest_airport_1": {
        "English": "Nearest Airport 1:",
        "中文": "最近机场 1:",
        "Hrvatski": "Najbliža zračna luka 1:",
        "Nederlands": "Dichtstbijzijnde luchthaven 1:",
        "Romania": "Cel mai apropiat aeroport 1:"
    },
    "nearest_airport_2": {
        "English": "Nearest Airport 2:",
        "中文": "最近机场 2:",
        "Hrvatski": "Najbliža zračna luka 2:",
        "Nederlands": "Dichtstbijzijnde luchthaven 2:",
        "Romania": "Cel mai apropiat aeroport 2:"
    },
    "distance": {
        "English": "Distance:",
        "中文": "距离:",
        "Hrvatski": "Udaljenost:",
        "Nederlands": "Afstand:",
        "Romania": "Distanță:"
    },
    "estimated_flight_time": {
        "English": "Estimated Flight Time:",
        "中文": "预计飞行时间:",
        "Hrvatski": "Procijenjeno vrijeme leta:",
        "Nederlands": "Geschatte vliegtijd:",
        "Romania": "Timp estimat de zbor:"
    },
    "select_map_mode": {
        "English": "Select Map Mode:",
        "中文": "选择地图模式:",
        "Hrvatski": "Odaberite način prikaza karte:",
        "Nederlands": "Selecteer kaartmodus:",
        "Romania": "Selectați modul de afișare a hărții:"
    },
    "flight_path": {
        "English": "Flight Path",
        "中文": "航线",
        "Hrvatski": "Putanja leta",
        "Nederlands": "Vluchtpad",
        "Romania": "Traiectoria zborului"
    },
    "flight_progress": {
        "English": "Flight Progress",
        "中文": "飞行进度",
        "Hrvatski": "Napredak leta",
        "Nederlands": "Vluchtvoortgang",
        "Romania": "Progresul zborului"
    },
    "airport_data_analysis": {
        "English": "Airport Data Analysis",
        "中文": "机场数据分析",
        "Hrvatski": "Analiza podataka o zračnim lukama",
        "Nederlands": "Analyse van luchthavengegevens",
        "Romania": "Analiza datelor aeroportuare"
    },
    "altitude_distribution": {
        "English": "Altitude Distribution",
        "中文": "海拔分布",
        "Hrvatski": "Distribucija nadmorske visine",
        "Nederlands": "Hoogteverdeling",
        "Romania": "Distribuția altitudinii"
    },
    "time_zone_distribution": {
        "English": "Time Zone Distribution",
        "中文": "时区分布",
        "Hrvatski": "Distribucija vremenske zone",
        "Nederlands": "Tijdzoneverdeling",
        "Romania": "Distribuția zonelor de timp"
    },
    "altitude_vs_distance_scatter_plot": {
        "English": "Altitude vs Distance Scatter Plot",
        "中文": "海拔与距离散点图",
        "Hrvatski": "Raspršeni grafikon visine u odnosu na udaljenost",
        "Nederlands": "Hoogte versus afstand spreidingsdiagram",
        "Romania": "Diagramă de dispersie altitudine vs distanță"
    },
    "altitude_vs_distance": {
        "English": "Altitude vs Distance",
        "中文": "海拔与距离",
        "Hrvatski": "Nadmorska visina u odnosu na udaljenost",
        "Nederlands": "Hoogte versus afstand",
        "Romania": "Altitudine vs Distanță"
    },
    "add_new_airport": {
        "English": "Add a New Airport",
        "中文": "添加新机场",
        "Hrvatski": "Dodaj novu zračnu luku",
        "Nederlands": "Voeg een nieuwe luchthaven toe",
        "Romania": "Adaugă un aeroport nou"
    },
    "no_new_airports": {
        "English": "No new airports have been added yet.",
        "中文": "当前没有新增机场。",
        "Hrvatski": "Nije dodana nijedna nova zračna luka.",
        "Nederlands": "Er zijn nog geen nieuwe luchthavens toegevoegd.",
        "Romania": "Nu au fost adăugate aeroporturi noi încă."
    },
    "no_new_flights": {
        "English": "No new flights have been added yet.",
        "中文": "当前没有新增航班。",
        "Hrvatski": "Nije dodan nijedan novi let.",
        "Nederlands": "Er zijn nog geen nieuwe vluchten toegevoegd.",
        "Romania": "Nu au fost adăugate încă zboruri noi."
    },
    "no_new_airlines": {
        "English": "No new airlines have been added yet.",
        "中文": "当前没有新增航空公司。",
        "Hrvatski": "Nije dodana nijedna nova aviokompanija.",
        "Nederlands": "Er zijn nog geen nieuwe luchtvaartmaatschappijen toegevoegd.",
        "Romania": "Nu au fost adăugate încă companii aeriene noi."
    },
    "no_new_planes": {
        "English": "No new planes have been added yet.",
        "中文": "当前没有新增飞机。",
        "Hrvatski": "Nije dodan nijedan novi avion.",
        "Nederlands": "Er zijn nog geen nieuwe vliegtuigen toegevoegd.",
        "Romania": "Nu au fost adăugate încă avioane noi."
    },
    "no_new_weather": {
        "English": "No new weather data has been added yet.",
        "中文": "当前没有新增天气数据。",
        "Hrvatski": "Nisu dodani novi vremenski podaci.",
        "Nederlands": "Er zijn nog geen nieuwe weersgegevens toegevoegd.",
        "Romania": "Nu au fost adăugate încă date meteo noi."
    },
    "note_session": {
        "English": "Note: New data is only stored in this session and will disappear if refreshed or restarted.",
        "中文": "注意：新增数据仅在当前会话中保存，刷新后将消失。",
        "Hrvatski": "Opomena: Novi podaci se spremaju samo tijekom sesije i nestat će nakon osvježenja.",
        "Nederlands": "Opmerking: Nieuwe gegevens worden alleen in deze sessie opgeslagen en verdwijnen bij verversen.",
        "Romania": "Notă: Datele noi sunt stocate doar în această sesiune și vor dispărea dacă pagina este reîncărcată sau repornită."
    },
    "dashboard": {
        "English": "Dashboard",
        "中文": "仪表盘",
        "Hrvatski": "Kontrolna ploča",
        "Nederlands": "Dashboard",
        "Romania": "Panou de control"
    },
    "new_data_entry": {
        "English": "New Data Entry",
        "中文": "数据录入",
        "Hrvatski": "Unos podataka",
        "Nederlands": "Nieuwe gegevensinvoer",
        "Romania": "Introducere date noi"
    },
    "new_data_submitted": {
        "English": "New Data Submitted (Session State)",
        "中文": "新数据已提交（会话状态）",
        "Hrvatski": "Novi podaci poslani (stanje sesije)",
        "Nederlands": "Nieuwe gegevens ingediend (sessiestatus)",
        "Romania": "Datele noi trimise (stare sesiune)"
    },
    "query_flights_date_range": {
        "English": "Query Flights by Date Range (2023)",
        "中文": "查询2023年航班日期范围",
        "Hrvatski": "Pretraži letove po datumu (2023)",
        "Nederlands": "Zoek vluchten op datum (2023)",
        "Romania": "Interogare zboruri după interval de date (2023)"
    },
    "total_flights": {
        "English": "Total flights on {start_date} to {end_date}: {total_flights}",
        "中文": "{start_date} 到 {end_date} 的总航班数：{total_flights}",
        "Hrvatski": "Ukupno letova od {start_date} do {end_date}: {total_flights}",
        "Nederlands": "Totaal aantal vluchten van {start_date} tot {end_date}: {total_flights}",
        "Romania": "Total zboruri de la {start_date} la {end_date}: {total_flights}"
    },
    "airlines_avg_delay": {
        "English": "Airlines and Average Departure Delay (min)",
        "中文": "航空公司及平均出发延误（分钟）",
        "Hrvatski": "Aviokompanije i prosječno kašnjenje pri polasku (min)",
        "Nederlands": "Luchtvaartmaatschappijen en gemiddelde vertrekvertraging (min)",
        "Romania": "Companii aeriene și întârziere medie la plecare (min)"
    },
    "aircraft_manufacturers": {
        "English": "Aircraft Manufacturers",
        "中文": "飞机制造商",
        "Hrvatski": "Proizvođači aviona",
        "Nederlands": "Vliegtuigfabrikanten",
        "Romania": "Producători de avioane"
    },
    "unique_destinations": {
        "English": "Unique Destinations: {unique_destinations}",
        "中文": "独特目的地：{unique_destinations}",
        "Hrvatski": "Jedinstvene destinacije: {unique_destinations}",
        "Nederlands": "Unieke bestemmingen: {unique_destinations}",
        "Romania": "Destinații unice: {unique_destinations}"
    },
    "most_visited": {
        "English": "Most visited destination: {most_visited} with {most_visited_count} flights",
        "中文": "最常访问的目的地：{most_visited}，航班数量：{most_visited_count}",
        "Hrvatski": "Najposjećenija destinacija: {most_visited} s {most_visited_count} letova",
        "Nederlands": "Meest bezochte bestemming: {most_visited} met {most_visited_count} vluchten",
        "Romania": "Destinația cea mai vizitată: {most_visited} cu {most_visited_count} zboruri"
    },
    "aircraft_types_counts": {
        "English": "Aircraft Types and Counts:",
        "中文": "飞机类型及数量：",
        "Hrvatski": "Vrste aviona i broj:",
        "Nederlands": "Vliegtuigtypes en aantallen:",
        "Romania": "Tipuri de avioane și număr:"
    },
    "flight_details": {
        "English": "Flight Details:",
        "中文": "航班详情：",
        "Hrvatski": "Detalji leta:",
        "Nederlands": "Vluchtdetails:",
        "Romania": "Detalii zbor:"
    }
}

def t(key, lang):
    return translations[key].get(lang, key)

# --------------------- Page Selection ---------------------
# Pages: Dashboard, New Data Entry, Developer Tool
col_lang, col_page = st.columns(2)
with col_lang:
    selected_language = st.selectbox(label=t("select_language", "English"), options=translations["language_options"])
with col_page:
    selected_page = st.selectbox(label=t("select_page", selected_language),
                                 options=[t("dashboard", selected_language),
                                          t("new_data_entry", selected_language),
                                          "Developer Tool"])

# --------------------- Other Data Loading ---------------------
def load_city_data():
    city_file_path = "../data/worldcities.csv"  
    city_df = pd.read_csv(city_file_path)
    return city_df

city_df = load_city_data()

def haversine_distance(coord1, coord2):
    return geopy.distance.geodesic(coord1, coord2).km

ny_coords = (40.7128, -74.0060)
df["distance"] = df.apply(lambda row: haversine_distance(ny_coords, (row["lat"], row["lon"])), axis=1)

def get_city_coordinates(city_name):
    city_name = city_name.lower()
    matches = city_df[city_df["city_ascii"].str.lower().str.contains(city_name, na=False)]
    if not matches.empty:
        best_match = matches.iloc[0]
        return best_match["lat"], best_match["lng"]
    return None

def find_nearest_airport(city_name, df):
    city_coords = get_city_coordinates(city_name)
    if city_coords is None:
        return None
    df["distance_to_city"] = df.apply(lambda row: haversine_distance(city_coords, (row["lat"], row["lon"])), axis=1)
    return df.loc[df["distance_to_city"].idxmin()]

df = df.copy()  # Avoid modifying the original DataFrame

# --------------------- New Data Entry Page ---------------------
if selected_page == t("new_data_entry", selected_language):
    st.subheader(t("new_data_entry", selected_language))
    # Choose Table to Enter New Data
    table_choice = st.selectbox("Choose Table to Enter New Data", ["Airports", "Flights", "Airlines", "Planes", "Weather"], key="table_choice")
    
    if table_choice == "Airports":
        with st.form("airport_form"):
            faa_val = st.text_input("FAA Code (3 letters)", "")
            name_val = st.text_input("Airport Name", "")
            lat_val = st.number_input("Latitude", value=0.0, format="%.6f")
            lon_val = st.number_input("Longitude", value=0.0, format="%.6f")
            alt_val = st.number_input("Altitude (feet)", value=0, step=1)
            tz_val = st.number_input("Time Zone Offset", value=0, step=1)
            dst_val = st.text_input("DST Usage (e.g. A, N, E...)", "")
            tzone_val = st.text_input("Timezone (Olson)", "")
            submitted = st.form_submit_button("Submit Airport")
            if submitted:
                new_airport = {
                    "faa": faa_val.strip(),
                    "name": name_val.strip(),
                    "lat": lat_val,
                    "lon": lon_val,
                    "alt": alt_val,
                    "tz": tz_val,
                    "dst": dst_val.strip(),
                    "tzone": tzone_val.strip()
                }
                if "new_airports" not in st.session_state:
                    st.session_state["new_airports"] = []
                st.session_state["new_airports"].append(new_airport)
                st.success("New Airport Data Added!")
    
    elif table_choice == "Flights":
        with st.form("flights_form"):
            st.write("Enter new flight data (2023):")
            year_val = st.number_input("Year", value=2023, step=1)
            month_val = st.number_input("Month", value=1, min_value=1, max_value=12, step=1)
            day_val = st.number_input("Day", value=1, min_value=1, max_value=31, step=1)
            dep_time = st.number_input("Departure Time (HHMM)", value=0, step=1)
            sched_dep_time = st.number_input("Scheduled Departure Time (HHMM)", value=0, step=1)
            dep_delay = st.number_input("Departure Delay (min)", value=0.0, step=0.1)
            arr_time = st.number_input("Arrival Time (HHMM)", value=0, step=1)
            sched_arr_time = st.number_input("Scheduled Arrival Time (HHMM)", value=0, step=1)
            arr_delay = st.number_input("Arrival Delay (min)", value=0.0, step=0.1)
            carrier = st.text_input("Carrier", "")
            flight_num = st.number_input("Flight Number", value=0, step=1)
            tailnum = st.text_input("Tail Number", "")
            origin = st.text_input("Origin", "")
            dest = st.text_input("Destination", "")
            air_time = st.number_input("Air Time (min)", value=0.0, step=0.1)
            distance = st.number_input("Distance (miles)", value=0.0, step=0.1)
            hour_val = st.number_input("Scheduled Departure Hour", value=0.0, step=0.1)
            minute_val = st.number_input("Scheduled Departure Minute", value=0.0, step=0.1)
            time_hour = st.text_input("Time Hour (timestamp)", "")
            submitted = st.form_submit_button("Submit Flight")
            if submitted:
                new_flight = {
                    "year": year_val,
                    "month": month_val,
                    "day": day_val,
                    "dep_time": dep_time,
                    "sched_dep_time": sched_dep_time,
                    "dep_delay": dep_delay,
                    "arr_time": arr_time,
                    "sched_arr_time": sched_arr_time,
                    "arr_delay": arr_delay,
                    "carrier": carrier,
                    "flight": flight_num,
                    "tailnum": tailnum,
                    "origin": origin,
                    "dest": dest,
                    "air_time": air_time,
                    "distance": distance,
                    "hour": hour_val,
                    "minute": minute_val,
                    "time_hour": time_hour
                }
                if "new_flights" not in st.session_state:
                    st.session_state["new_flights"] = []
                st.session_state["new_flights"].append(new_flight)
                st.success("New Flight Data Added!")
    
    elif table_choice == "Airlines":
        with st.form("airlines_form"):
            st.write("Enter new airline data:")
            carrier = st.text_input("Carrier", "")
            name = st.text_input("Airline Name", "")
            submitted = st.form_submit_button("Submit Airline")
            if submitted:
                new_airline = {"carrier": carrier, "name": name}
                if "new_airlines" not in st.session_state:
                    st.session_state["new_airlines"] = []
                st.session_state["new_airlines"].append(new_airline)
                st.success("New Airline Data Added!")
    
    elif table_choice == "Planes":
        with st.form("planes_form"):
            st.write("Enter new plane data:")
            tailnum = st.text_input("Tail Number", "")
            year_val = st.number_input("Year of Manufacture", value=2000, step=1)
            type_val = st.text_input("Aircraft Type", "")
            manufacturer = st.text_input("Manufacturer", "")
            model = st.text_input("Model", "")
            engines = st.number_input("Number of Engines", value=1, step=1)
            seats = st.number_input("Seating Capacity", value=100, step=1)
            speed = st.number_input("Speed", value=0, step=1)
            engine = st.text_input("Engine Type", "")
            submitted = st.form_submit_button("Submit Plane")
            if submitted:
                new_plane = {
                    "tailnum": tailnum,
                    "year": year_val,
                    "type": type_val,
                    "manufacturer": manufacturer,
                    "model": model,
                    "engines": engines,
                    "seats": seats,
                    "speed": speed,
                    "engine": engine
                }
                if "new_planes" not in st.session_state:
                    st.session_state["new_planes"] = []
                st.session_state["new_planes"].append(new_plane)
                st.success("New Plane Data Added!")
    
    elif table_choice == "Weather":
        with st.form("weather_form"):
            st.write("Enter new weather data:")
            origin = st.text_input("Origin", "")
            year_val = st.number_input("Year", value=2023, step=1)
            month_val = st.number_input("Month", value=1, min_value=1, max_value=12, step=1)
            day_val = st.number_input("Day", value=1, min_value=1, max_value=31, step=1)
            hour_val = st.number_input("Hour", value=0, min_value=0, max_value=23, step=1)
            temp = st.number_input("Temperature (°F)", value=0.0, step=0.1)
            dewp = st.number_input("Dew Point (°F)", value=0.0, step=0.1)
            humid = st.number_input("Humidity (%)", value=0.0, step=0.1)
            wind_dir = st.number_input("Wind Direction (degrees)", value=0.0, step=0.1)
            wind_speed = st.number_input("Wind Speed (mph)", value=0.0, step=0.1)
            wind_gust = st.number_input("Wind Gust (mph)", value=0.0, step=0.1)
            precip = st.number_input("Precipitation (inches)", value=0.0, step=0.1)
            pressure = st.number_input("Air Pressure (inHg)", value=0.0, step=0.1)
            visib = st.number_input("Visibility (miles)", value=0.0, step=0.1)
            time_hour = st.text_input("Time Hour (timestamp)", "")
            submitted = st.form_submit_button("Submit Weather")
            if submitted:
                new_weather = {
                    "origin": origin,
                    "year": year_val,
                    "month": month_val,
                    "day": day_val,
                    "hour": hour_val,
                    "temp": temp,
                    "dewp": dewp,
                    "humid": humid,
                    "wind_dir": wind_dir,
                    "wind_speed": wind_speed,
                    "wind_gust": wind_gust,
                    "precip": precip,
                    "pressure": pressure,
                    "visib": visib,
                    "time_hour": time_hour
                }
                if "new_weather" not in st.session_state:
                    st.session_state["new_weather"] = []
                st.session_state["new_weather"].append(new_weather)
                st.success("New Weather Data Added!")
    
    # Display new data submitted (if none, show info message)
    st.subheader(t("new_data_submitted", selected_language))
    if "new_airports" in st.session_state and st.session_state["new_airports"]:
        st.write("Airports:")
        st.dataframe(pd.DataFrame(st.session_state["new_airports"]))
    else:
        st.info(t("no_new_airports", selected_language))
        
    if "new_flights" in st.session_state and st.session_state["new_flights"]:
        st.write("Flights:")
        st.dataframe(pd.DataFrame(st.session_state["new_flights"]))
    else:
        st.info(t("no_new_flights", selected_language))
        
    if "new_airlines" in st.session_state and st.session_state["new_airlines"]:
        st.write("Airlines:")
        st.dataframe(pd.DataFrame(st.session_state["new_airlines"]))
    else:
        st.info(t("no_new_airlines", selected_language))
        
    if "new_planes" in st.session_state and st.session_state["new_planes"]:
        st.write("Planes:")
        st.dataframe(pd.DataFrame(st.session_state["new_planes"]))
    else:
        st.info(t("no_new_planes", selected_language))
        
    if "new_weather" in st.session_state and st.session_state["new_weather"]:
        st.write("Weather:")
        st.dataframe(pd.DataFrame(st.session_state["new_weather"]))
    else:
        st.info(t("no_new_weather", selected_language))
        
    st.info(t("note_session", selected_language))

# --------------------- Developer Tool Page ---------------------
elif selected_page == "Developer Tool":
    st.subheader("Developer Tool")
    st.write("Enter SQL query to run on the 2023 database (supports SELECT, INSERT, UPDATE, DELETE, etc.):")
    sql_query = st.text_area("SQL Query", height=150)
    if st.button("Run Query"):
        try:
            conn = sqlite3.connect(db_path)
            # If the query starts with 'select', return the result as a DataFrame
            if sql_query.strip().lower().startswith("select"):
                result_df = pd.read_sql_query(sql_query, conn)
                st.write("Query Result:")
                st.dataframe(result_df)
            else:
                cur = conn.cursor()
                cur.execute(sql_query)
                conn.commit()
                st.success("Query executed successfully!")
            conn.close()
        except Exception as e:
            st.error(f"Error executing query: {e}")

# --------------------- Dashboard Page ---------------------
else:
    # If new airports data exists in session_state, append it to the main dataframe
    if "new_airports" in st.session_state and st.session_state["new_airports"]:
        new_df = pd.DataFrame(st.session_state["new_airports"])
        df = pd.concat([df, new_df], ignore_index=True)
        
    st.sidebar.title(t("project_flight_title", selected_language))
    with open("../figures/airplane.png", "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode()
        airplane_img = "data:image/png;base64," + encoded_image
    st.sidebar.markdown(
    f"""
    <style>
    .cat-container {{
        text-align: left;
        padding: 10px;
    }}
    .airplane-img {{
        width: 50px;
        animation: bounceAndScale 2s infinite;
    }}
    @keyframes bounceAndScale {{
        0%, 100% {{
            transform: translateY(0.5px) scale(1);
        }}
        20% {{
            transform: translateY(1.5px) scale(1.01);
        }}
        40% {{
            transform: translateY(0.5px) scale(1);
        }}
        60% {{
            transform: translateY(1.5px) scale(1.01);
        }}
        80% {{
            transform: translateY(0.5px) scale(1);
        }}
    }}
    </style>
    <div class="cat-container">
        <img class="airplane-img" src="{airplane_img}" alt="Airplane">
    </div>
    """,
    unsafe_allow_html=True
    )
    
    # Query flights by date range (default End Date is 2023-01-02)
    st.sidebar.markdown(t("query_flights_date_range", selected_language))
    start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1),
                                       min_value=datetime.date(2023, 1, 1), max_value=datetime.date(2023, 12, 31),
                                       key="start_date")
    end_date = st.sidebar.date_input("End Date", value=datetime.date(2023, 1, 2),
                                     min_value=datetime.date(2023, 1, 1), max_value=datetime.date(2023, 12, 31),
                                     key="end_date")
    
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM flights WHERE year = 2023"
    flights_df = pd.read_sql_query(query, conn)
    conn.close()
    flights_df['flight_date'] = pd.to_datetime(flights_df[['year','month','day']])
    mask = (flights_df['flight_date'] >= pd.to_datetime(start_date)) & (flights_df['flight_date'] <= pd.to_datetime(end_date))
    flights_df = flights_df[mask]
        
    if not flights_df.empty:
        conn = sqlite3.connect(db_path)
        airlines_df = pd.read_sql_query("SELECT * FROM airlines", conn)
        planes_df = pd.read_sql_query("SELECT * FROM planes", conn)
        airports_df = pd.read_sql_query("SELECT * FROM airports", conn)
        weather_df = pd.read_sql_query("SELECT * FROM weather", conn)
        conn.close()
        
        flights_df = flights_df.merge(airlines_df, on='carrier', how='left', suffixes=('', '_airline'))
        flights_df = flights_df.rename(columns={"name": "name_airline"})
        flights_df = flights_df.merge(planes_df, on='tailnum', how='left', suffixes=('', '_plane'))
        flights_df = flights_df.merge(airports_df[['faa','name','lat','lon']], left_on='origin', right_on='faa', how='left', suffixes=('', '_origin'))
        flights_df = flights_df.rename(columns={'name': 'origin_name', 'lat': 'origin_lat', 'lon': 'origin_lon'})
        flights_df = flights_df.merge(airports_df[['faa','name','lat','lon']], left_on='dest', right_on='faa', how='left', suffixes=('', '_dest'))
        flights_df = flights_df.rename(columns={'name': 'dest_name', 'lat': 'dest_lat', 'lon': 'dest_lon'})
        flights_df = flights_df.merge(weather_df[['origin','year','month','day','hour','wind_dir','wind_speed']],
                                      on=['origin','year','month','day','hour'], how='left')
        
        route_stats = flights_df.groupby(['origin','dest']).agg(
            avg_dep_delay=('dep_delay', 'mean'),
            avg_distance=('distance', 'mean')
        ).reset_index()
        flights_df = flights_df.merge(route_stats, on=['origin','dest'], how='left')
        flights_df['distance_km'] = flights_df['distance'] * 1.60934
        # Calculate speed (km/h) = (distance_km * 60) / air_time (in minutes)
        flights_df['speed'] = flights_df.apply(lambda row: (row['distance_km'] * 60 / row['air_time']) if row['air_time'] and row['air_time'] > 0 else None, axis=1)
        
        total_flights = len(flights_df)
        st.write(t("total_flights", selected_language).format(start_date=start_date, end_date=end_date, total_flights=total_flights))
        
        avg_delay_by_airline = flights_df.groupby('name_airline')['dep_delay'].mean().reset_index()
        fig_avg_delay = px.bar(avg_delay_by_airline, x='name_airline', y='dep_delay',
                               labels={'name_airline': 'Airline', 'dep_delay': 'Avg Departure Delay (min)'},
                               title=t("airlines_avg_delay", selected_language))
        st.plotly_chart(fig_avg_delay, use_container_width=True, key="fig_avg_delay")
        
        manufacturer_counts = flights_df['manufacturer'].value_counts().reset_index()
        manufacturer_counts.columns = ['manufacturer', 'count']
        fig_manufacturers = px.pie(manufacturer_counts, names='manufacturer', values='count',
                                   title=t("aircraft_manufacturers", selected_language))
        st.plotly_chart(fig_manufacturers, use_container_width=True, key="fig_manufacturers")
        
        unique_destinations = flights_df['dest'].nunique()
        dest_counts = flights_df['dest'].value_counts()
        most_visited = dest_counts.idxmax()
        most_visited_count = dest_counts.max()
        st.write(t("unique_destinations", selected_language).format(unique_destinations=unique_destinations))
        st.write(t("most_visited", selected_language).format(most_visited=most_visited, most_visited_count=most_visited_count))
        
        type_counts = flights_df['type'].value_counts().reset_index()
        type_counts.columns = ['Aircraft Type', 'Count']
        st.write(t("aircraft_types_counts", selected_language))
        st.dataframe(type_counts)
        
        # In Flight Details, replace avg_distance with computed speed
        display_columns = [
            'origin_name',
            'origin',
            'dest_name',
            'dest',
            'tailnum',
            'year_plane',
            'type',
            'manufacturer',
            'avg_dep_delay',
            'distance_km',
            'speed',            # computed speed in km/h
            'dest_lat',
            'dest_lon',
            'wind_dir',
            'wind_speed'
        ]
        flights_display = flights_df[display_columns]
        with st.sidebar.expander(t("flight_details", selected_language)):
            st.dataframe(flights_display)
    else:
        st.sidebar.warning("No flights found for the given date range")
    
    destination_1 = st.sidebar.text_input(t("enter_departure_city", selected_language), key="destination_1")
    destination_2 = st.sidebar.text_input(t("enter_arrival_city", selected_language), key="destination_2")
    map_type = st.sidebar.radio(t("select_default_map_type", selected_language), ["US", "World"])
    tz_options = ['All'] + sorted(df['tz'].unique())
    selected_tz = st.sidebar.selectbox(t("select_time_zone", selected_language), options=tz_options, index=0)
    filtered_df = df if selected_tz == 'All' else df[df['tz'] == selected_tz]
    if destination_1 and destination_2:
        airport_1 = find_nearest_airport(destination_1, df)
        airport_2 = find_nearest_airport(destination_2, df)
        if airport_1 is not None and airport_2 is not None:
            distance_km = haversine_distance((airport_1['lat'], airport_1['lon']), (airport_2['lat'], airport_2['lon']))
            flight_time_hr = distance_km / 600.0
            st.sidebar.markdown(f"{t('nearest_airport_1', selected_language)} {airport_1['name']} ({airport_1['faa']})")
            st.sidebar.markdown(f"{t('nearest_airport_2', selected_language)} {airport_2['name']} ({airport_2['faa']})")
            st.sidebar.markdown(f"{t('distance', selected_language)} {distance_km:.2f} km")
            st.sidebar.markdown(f"{t('estimated_flight_time', selected_language)} {flight_time_hr:.2f} hours")
            center_coords = {"lat": 37.0902, "lon": -95.7129} if map_type == "US" else {"lat": 20, "lon": 0}
            zoom_level = 2.7 if map_type == "US" else 1
            flight_progress = st.sidebar.slider(t("flight_progress", selected_language), 0.0, flight_time_hr, 0.0, step=0.1)
            progress_ratio = flight_progress / flight_time_hr if flight_time_hr > 0 else 0
            current_lat = airport_1['lat'] + progress_ratio * (airport_2['lat'] - airport_1['lat'])
            current_lon = airport_1['lon'] + progress_ratio * (airport_2['lon'] - airport_1['lon'])
            center_coords = {"lat": 37.0902, "lon": -95.7129} if map_type == "US" else {"lat": 50, "lon": -90}
            zoom_level = 2.5 if map_type == "US" else 1.2
            fig = px.scatter_mapbox(
                filtered_df,
                lat="lat", lon="lon",
                color="alt", color_continuous_scale="viridis",
                size_max=10, zoom=zoom_level, center=center_coords,
                mapbox_style="open-street-map", opacity=0.7
            )
            fig.add_trace(go.Scattermapbox(
                mode="lines",
                lon=[airport_1['lon'], airport_2['lon']],
                lat=[airport_1['lat'], airport_2['lat']],
                line={'width': 2, 'color': 'blue'},
                name=t("flight_path", selected_language)
            ))
            with open("../figures/airplane.png", "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode()
            airplane_img = "data:image/png;base64," + encoded_image
            delta = 3
            if airport_2['lon'] >= airport_1['lon']:
                coordinates = [
                    [current_lon - delta, current_lat + delta],
                    [current_lon + delta, current_lat + delta],
                    [current_lon + delta, current_lat - delta],
                    [current_lon - delta, current_lat - delta]
                ]
            else:
                coordinates = [
                    [current_lon + delta, current_lat + delta],
                    [current_lon - delta, current_lat + delta],
                    [current_lon - delta, current_lat - delta],
                    [current_lon + delta, current_lat - delta]
                ]
            fig.update_layout(
                mapbox=dict(
                    layers=[
                        {
                            "source": airplane_img,
                            "sourcetype": "image",
                            "coordinates": coordinates,
                        }
                    ]
                )
            )
        st.plotly_chart(fig, use_container_width=True, key=f"map-{destination_1}-{destination_2}")
    else:
        center_coords = {"lat": 37.0902, "lon": -95.7129} if map_type == "US" else {"lat": 50, "lon": -90}
        zoom_level = 2.5 if map_type == "US" else 1
        fig_default = px.scatter_mapbox(
            filtered_df, lat="lat", lon="lon",
            color="alt", color_continuous_scale="viridis",
            size_max=10, zoom=zoom_level, center=center_coords,
            mapbox_style="open-street-map", opacity=0.7
        )
        fig_default.update_layout(coloraxis_colorbar=dict(title="Altitude"))
        st.plotly_chart(fig_default, use_container_width=True, key="default-map")
    
    def display_visualizations(data):
        col1, col2 = st.columns(2)
        with col1:
            fig_alt = px.histogram(
                data, x="alt", nbins=50,
                title=t("altitude_distribution", selected_language),
                color_discrete_sequence=["blue"]
            )
            st.plotly_chart(fig_alt, use_container_width=True, key="fig_alt")
        with col2:
            fig_tz = px.histogram(
                data, x="tz", nbins=20,
                title=t("time_zone_distribution", selected_language),
                color_discrete_sequence=["orange"]
            )
            st.plotly_chart(fig_tz, use_container_width=True, key="fig_tz")
        fig_scatter = px.scatter(
            data, x="alt", y="distance",
            title=t("altitude_vs_distance", selected_language),
            color_discrete_sequence=["green"], opacity=0.7
        )
        st.plotly_chart(fig_scatter, use_container_width=True, key="fig_scatter")
        
    display_visualizations(filtered_df)


