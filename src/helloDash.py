import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from timezonefinder import TimezoneFinder
import seaborn as sns
import numpy as np 
import math 
from sklearn.cluster import DBSCAN 
from geopy.distance import great_circle
from sklearn.neighbors import NearestNeighbors
import networkx as nx 
from geopy.geocoders import Nominatim 
import dash
from dash import dcc, html
import streamlit as st
import geopy.distance  # for calculating geodesic distance
import base64 # for using png image as ui


# read airports.csv
df = pd.read_csv("../data/airports.csv")
CSV_FILE_PATH = "../data/airports.csv"  # path to rewrite the CSV file

# inferring missing values instead of deleting them
tf = TimezoneFinder()
df["tzone"] = df.apply(
    lambda row: (
        tf.timezone_at(lng=row["lon"], lat=row["lat"])
        if pd.isnull(row["tzone"])
        else row["tzone"]
    ),
    axis=1,
)
# update tz values based on the inferred tzone
tz_mapping_dynamic = dict(df[["tzone", "tz"]].dropna().drop_duplicates().values)
df["tz"] = df.apply(
    lambda row: (
        tz_mapping_dynamic.get(row["tzone"], row["tz"])
        if pd.isnull(row["tz"])
        else row["tz"]
    ),
    axis=1,
)

# infer dst based on the most common dst setting per tzone
def infer_dst_from_tzone(tzone):
    if pd.isnull(tzone):
        return 'N'
    if "America/" in tzone:
        return 'A'
    elif "Europe/" in tzone:
        return 'E'
    else:
        return 'N'

df["dst"] = df.apply(
    lambda row: row["dst"] if pd.notnull(row["dst"]) else infer_dst_from_tzone(row["tzone"]),
    axis=1
)

df.loc[df["tzone"] == "America/Boise", "tz"] = -7 # fix missing values in America/Boise
df.loc[df['tz'] == 8, 'tz'] = -8 # fix incorrect tz value

# convert altitude to meters
df["alt_meters"] = df["alt"] * 0.3048
df["tz"] = df["tz"].astype("Int64")  # convert tz to integer

#dashboard
# page layout
st.set_page_config(layout="wide")

# language translations
translations = {
    "language_options": ["English", "中文", "Hrvatski", "Nederlands"],
    "project_flight_title": {
        "English": "Project Flight✈️",
        "中文": "项目飞行✈️",
        "Hrvatski": "Projekt Let✈️",
        "Nederlands": "Project Vlucht✈️"
    },
    "select_page": {
        "English": "Select Page",
        "中文": "选择页面",
        "Hrvatski": "Odaberite stranicu",
        "Nederlands": "Selecteer pagina"
    },
    "select_language": {
        "English": "Select Language",
        "中文": "选择语言",
        "Hrvatski": "Odaberite jezik",
        "Nederlands": "Selecteer taal"
    },
    "enter_departure_city": {
        "English": "Enter departure city name:",
        "中文": "输入出发城市名称:",
        "Hrvatski": "Unesite grad polaska:",
        "Nederlands": "Voer de naam van de vertrekstad in:"
    },
    "enter_arrival_city": {
        "English": "Enter arrival city name:",
        "中文": "输入到达城市名称:",
        "Hrvatski": "Unesite grad dolaska:",
        "Nederlands": "Voer de naam van de aankomststad in:"
    },
    "select_default_map_type": {
        "English": "Select Default Map Type:",
        "中文": "选择默认地图类型:",
        "Hrvatski": "Odaberite zadani tip karte:",
        "Nederlands": "Selecteer standaard kaarttype:"
    },
    "select_time_zone": {
        "English": "Select a Time Zone:",
        "中文": "选择时区:",
        "Hrvatski": "Odaberite vremensku zonu:",
        "Nederlands": "Selecteer een tijdzone:"
    },
    "nearest_airport_1": {
        "English": "Nearest Airport 1:",
        "中文": "最近机场 1:",
        "Hrvatski": "Najbliža zračna luka 1:",
        "Nederlands": "Dichtstbijzijnde luchthaven 1:"
    },
    "nearest_airport_2": {
        "English": "Nearest Airport 2:",
        "中文": "最近机场 2:",
        "Hrvatski": "Najbliža zračna luka 2:",
        "Nederlands": "Dichtstbijzijnde luchthaven 2:"
    },
    "distance": {
        "English": "Distance:",
        "中文": "距离:",
        "Hrvatski": "Udaljenost:",
        "Nederlands": "Afstand:"
    },
    "estimated_flight_time": {
        "English": "Estimated Flight Time:",
        "中文": "预计飞行时间:",
        "Hrvatski": "Procijenjeno vrijeme leta:",
        "Nederlands": "Geschatte vliegtijd:"
    },
    "select_map_mode": {
        "English": "Select Map Mode:",
        "中文": "选择地图模式:",
        "Hrvatski": "Odaberite način prikaza karte:",
        "Nederlands": "Selecteer kaartmodus:"
    },
    "flight_path": {
        "English": "Flight Path",
        "中文": "航线",
        "Hrvatski": "Putanja leta",
        "Nederlands": "Vluchtpad"
    },
    "flight_progress": {
        "English": "Flight Progress",
        "中文": "飞行进度",
        "Hrvatski": "Napredak leta",
        "Nederlands": "Vluchtvoortgang"
    },
    "airport_data_analysis": {
        "English": "Airport Data Analysis",
        "中文": "机场数据分析",
        "Hrvatski": "Analiza podataka o zračnim lukama",
        "Nederlands": "Analyse van luchthavengegevens"
    },
    "altitude_distribution": {
        "English": "Altitude Distribution",
        "中文": "海拔分布",
        "Hrvatski": "Distribucija nadmorske visine",
        "Nederlands": "Hoogteverdeling"
    },
    "time_zone_distribution": {
        "English": "Time Zone Distribution",
        "中文": "时区分布",
        "Hrvatski": "Distribucija vremenske zone",
        "Nederlands": "Tijdzoneverdeling"
    },
    "altitude_vs_distance_scatter_plot": {
        "English": "Altitude vs Distance Scatter Plot",
        "中文": "海拔与距离散点图",
        "Hrvatski": "Raspršeni grafikon visine u odnosu na udaljenost",
        "Nederlands": "Hoogte versus afstand spreidingsdiagram"
    },
    "altitude_vs_distance": {
        "English": "Altitude vs Distance",
        "中文": "海拔与距离",
        "Hrvatski": "Nadmorska visina u odnosu na udaljenost",
        "Nederlands": "Hoogte versus afstand"
    },
    "add_new_airport": {
        "English": "Add a New Airport",
        "中文": "添加新机场",
        "Hrvatski": "Dodaj novu zračnu luku",
        "Nederlands": "Voeg een nieuwe luchthaven toe"
    },
    "no_new_airports": {
        "English": "No new airports have been added yet.",
        "中文": "当前没有新增机场。",
        "Hrvatski": "Još nije dodana nijedna nova zračna luka.",
        "Nederlands": "Er zijn nog geen nieuwe luchthavens toegevoegd."
    },
    "note_session": {
        "English": "Note: New data is only stored in this session and will disappear if refreshed or restarted.",
        "中文": "注意：新增数据仅在当前会话中保存，刷新后将消失。",
        "Hrvatski": "Opomena: Novi podaci se spremaju samo tijekom sesije i nestat će nakon osvježenja.",
        "Nederlands": "Opmerking: Nieuwe gegevens worden alleen in deze sessie opgeslagen en verdwijnen bij verversen."
    },
    "dashboard": {
        "English": "Dashboard",
        "中文": "仪表盘",
        "Hrvatski": "Kontrolna ploča",
        "Nederlands": "Dashboard"
    },
    "new_data_entry": {
        "English": "New Data Entry",
        "中文": "数据录入",
        "Hrvatski": "Unos podataka",
        "Nederlands": "Nieuwe gegevensinvoer"
    },
    "fill_all_fields": {
        "English": "Please fill in all required fields.",
        "中文": "请填写所有必填项。",
        "Hrvatski": "Molimo, popunite sva obavezna polja.",
        "Nederlands": "Vul alle verplichte velden in."
    },
    "submit_airport": {
        "English": "Submit Airport",
        "中文": "提交机场",
        "Hrvatski": "Pošalji zračnu luku",
        "Nederlands": "Verzend luchthaven"
    },
    "new_airport_added": {
        "English": "New Airport Added!",
        "中文": "新增机场成功！",
        "Hrvatski": "Nova zračna luka je dodana!",
        "Nederlands": "Nieuwe luchthaven toegevoegd!"
    },
    "query_airport": {
        "English": "Query Airport",
        "中文": "查询机场",
        "Hrvatski": "Pretraži zračnu luku",
        "Nederlands": "Zoek luchthaven"
    },
    "query_placeholder": {
        "English": "Enter FAA code or Airport Name",
        "中文": "输入FAA代码或机场名称",
        "Hrvatski": "Unesite FAA kod ili ime zračne luke",
        "Nederlands": "Voer FAA-code of luchthavennaam in"
    },
    "query_invalid": {
        "English": "Query invalid: No matching airport found.",
        "中文": "查询无效：未找到匹配的机场。",
        "Hrvatski": "Upit nije važeći: Nijedna odgovarajuća zračna luka nije pronađena.",
        "Nederlands": "Ongeldige query: Geen overeenkomende luchthaven gevonden."
    }
}

def t(key, lang):
    # return the translation if available, otherwise return the key
    return translations[key].get(lang, key)

# main page layout
col_lang, col_page = st.columns(2)
with col_lang:
    selected_language = st.selectbox(
        label=t("select_language", "English"),
        options=translations["language_options"]
    )
with col_page:
    selected_page = st.selectbox(
        label=t("select_page", selected_language),
        options=[t("dashboard", selected_language), t("new_data_entry", selected_language)]
    )

# load city data
def load_city_data():
    city_file_path = "../data/worldcities.csv"  
    city_df = pd.read_csv(city_file_path)
    return city_df

city_df = load_city_data()

# calculate 2 cites distance
def haversine_distance(coord1, coord2):
    return geopy.distance.geodesic(coord1, coord2).km

# calculus distance to New York
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

df = df.copy()

# page switch
if selected_page == t("new_data_entry", selected_language):
    st.subheader(t("add_new_airport", selected_language))

    # storing new airports in session state
    if "new_airports" not in st.session_state:
        st.session_state["new_airports"] = []

    with st.form("airport_form"):
        faa_val = st.text_input("FAA Code (3 letters)", "")
        name_val = st.text_input("Airport Name", "")
        lat_val = st.number_input("Latitude", value=0.0, format="%.6f")
        lon_val = st.number_input("Longitude", value=0.0, format="%.6f")
        alt_val = st.number_input("Altitude (meter)", value=0, step=1)
        tz_val = st.number_input("Time Zone Offset", value=0, step=1)
        dst_val = st.text_input("DST Usage (e.g. A, N, E...)", "")
        tzone_val = st.text_input("Timezone (Olson)", "")

        submitted = st.form_submit_button(t("submit_airport", selected_language))
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
            st.session_state["new_airports"].append(new_airport)
            st.success(t("new_airport_added", selected_language))

    if st.session_state["new_airports"]:
        st.subheader(t("new_data_entry", selected_language))
        new_df = pd.DataFrame(st.session_state["new_airports"])
        st.dataframe(new_df)
    else:
        st.info(t("no_new_airports", selected_language))
        
    st.info(t("note_session", selected_language))

else:
    # first check if there are new airports to add
    if "new_airports" in st.session_state and st.session_state["new_airports"]:
        new_df = pd.DataFrame(st.session_state["new_airports"])
        df = pd.concat([df, new_df], ignore_index=True)
        
    st.sidebar.title(t("project_flight_title", selected_language))
    destination_1 = st.sidebar.text_input(t("enter_departure_city", selected_language), key="destination_1")
    destination_2 = st.sidebar.text_input(t("enter_arrival_city", selected_language), key="destination_2")
    
    # add a query section to search for airports
    st.sidebar.markdown("### " + t("query_airport", selected_language))
    query_input = st.sidebar.text_input(t("query_placeholder", selected_language), key="query_airport_input")
    if query_input:
        query_lower = query_input.strip().lower()
        # search for the query in the faa and name columns, case-insensitive
        query_result = df[(df['faa'].str.lower() == query_lower) | (df['name'].str.lower().str.contains(query_lower))]
        if not query_result.empty:
            st.sidebar.write(query_result)
        else:
            st.sidebar.warning(t("query_invalid", selected_language))
    
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

            map_mode = st.sidebar.radio(t("select_map_mode", selected_language), ["US", "World"], index=0)
            center_coords = {"lat": 37.0902, "lon": -95.7129} if map_mode == "US" else {"lat": 20, "lon": 0}
            zoom_level = 2.7 if map_mode == "US" else 1

            flight_progress = st.sidebar.slider(t("flight_progress", selected_language), 0.0, flight_time_hr, 0.0, step=0.1)
            progress_ratio = flight_progress / flight_time_hr if flight_time_hr > 0 else 0
            current_lat = airport_1['lat'] + progress_ratio * (airport_2['lat'] - airport_1['lat'])
            current_lon = airport_1['lon'] + progress_ratio * (airport_2['lon'] - airport_1['lon'])

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
            # set the coordinates for the airplane image
            delta = 3  # ui size
            coordinates = [
                [current_lon - delta, current_lat + delta],  # left top
                [current_lon + delta, current_lat + delta],  # right top
                [current_lon + delta, current_lat - delta],  # right bottom
                [current_lon - delta, current_lat - delta]   # left bottom
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
        zoom_level = 2.5 if map_type == "US" else 1.2
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
            st.subheader(t("altitude_distribution", selected_language))
            fig_alt = px.histogram(
                data, x="alt", nbins=50,
                title=t("altitude_distribution", selected_language),
                color_discrete_sequence=["blue"]
            )
            st.plotly_chart(fig_alt, use_container_width=True)
        with col2:
            st.subheader(t("time_zone_distribution", selected_language))
            fig_tz = px.histogram(
                data, x="tz", nbins=20,
                title=t("time_zone_distribution", selected_language),
                color_discrete_sequence=["orange"]
            )
            st.plotly_chart(fig_tz, use_container_width=True)
        fig_scatter = px.scatter(
            data, x="alt", y="distance",
            title=t("altitude_vs_distance", selected_language),
            color_discrete_sequence=["green"], opacity=0.7
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    display_visualizations(filtered_df)