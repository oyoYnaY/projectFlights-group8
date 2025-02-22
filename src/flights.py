import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from timezonefinder import TimezoneFinder
import seaborn as sns
import math
import sqlite3


# =============== Data processing for airports.csv =============== 
# read airports.csv
df = pd.read_csv("../data/airports.csv")

# # descriptive statistics and data preprocessing
# print("first 5 rows of the dataset:\n", df.head())  # display first few rows
# print("dataset information:")
# df.info()  # display dataset information

# print("descriptive statistics:\n", df.describe())  # display descriptive statistics
# print("missing values in each column:\n", df.isnull().sum())  # check for missing values

# # display unique time zones and their corresponding tz values
# unique_tz_mapping = df[["tzone", "tz"]].dropna().drop_duplicates()
# print(unique_tz_mapping)

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
        return 'U'
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

# # check for missing values after inference
# print("missing values after inference:\n", df.isnull().sum())
# print(df[df["tz"].isnull()])
# print(df[df["tzone"] == "America/Boise"][["tzone", "tz"]].dropna().drop_duplicates()) # check for missing values in America/Boise
# df.loc[df["tzone"] == "America/Boise", "tz"] = -7 # fix missing values in America/Boise
# print("missing values after final fix:\n", df.isnull().sum())

df.loc[df['tz'] == 8, 'tz'] = -8 # fix incorrect tz value

# convert altitude to meters
df["alt_meters"] = df["alt"] * 0.3048
df["tz"] = df["tz"].astype("Int64")  # convert tz to integer
# df.info()

# explore relationships within the dataset
# print(df.describe()) # display descriptive statistics
# scatter plot: altitude vs latitude
plt.figure(figsize=(10, 6))
plt.scatter(df["lat"], df["alt_meters"], alpha=0.5, color="blue")

plt.xlabel("Latitude")
plt.ylabel("Altitude (meters)")
plt.title("Scatter Plot: Airport Altitude vs Latitude")
plt.grid(True)

# plt.show()

# print(df["dst"].unique()) # display unique values in 'dst' column
# print(df["tzone"].unique()) # display unique values in 'tzone' column
# print(df["tz"].unique()) # display unique values in 'tz' column

# countplot: number of airports in each time zone
plt.figure(figsize=(10, 6))
sns.countplot(x=df["tzone"], hue=df["tzone"], palette="coolwarm", legend=False)
# sns.countplot(x=df["tz"], hue=df["tz"], palette="coolwarm", legend=False)
plt.xlabel("Time Zone")
plt.xticks(rotation=25, ha='right', fontsize=6)
plt.ylabel("Number of Airports")
plt.title("Number of Airports in Each Time Zone")
plt.grid(True)
# plt.show()

# find airports that do not observe daylight saving time, later visualizing these airports on a map
df_no_dst = df[df["dst"] == "N"]

plt.figure(figsize=(10, 6))
sns.scatterplot(x=df_no_dst["lon"], y=df_no_dst["lat"], color="red")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Airports That Do NOT Observe DST")

# plt.show()


# =============== Part 1,2 =============== 
# visualizations
# plot global airport distribution, with color coded by 'alt' (altitude)
fig_global = px.scatter_geo(df, 
                            lat="lat", lon="lon", 
                            hover_name="name",
                            color="alt_meters",  # color by altitude
                            title="Global Airport Distribution (Colored by Altitude)",
                            projection="natural earth",
                            color_continuous_scale="Viridis",  # Choose color scale
                            labels={"alt_meters": "Altitude (m)"}  # Set color legend title
    )

# fig_global.show()


# plot US airport distribution, with color coded by 'alt' (altitude)
# use scatter_geo funcion, scope="usa"
fig_us= px.scatter_geo(df, 
                        lat="lat", lon="lon", 
                        hover_name="name",
                        color="alt_meters",  # color by altitude
                        title="us airport distribution (colored by altitude)",
                        scope="usa",
                        color_continuous_scale="Viridis",
                        labels={"alt_meters": "Altitude (m)"} 
                        )
# fig_us.show()

# analyze the distances between JFK and airports in the file
R = 6378.1370  # in kilometeres
jfk_data = df[df["faa"] == "JFK"]
jfk_loc = [jfk_data["lat"].iloc[0], jfk_data["lon"].iloc[0]]
df["geo_dist"] = None
df["euc_dist"] = None
for index, airport in df.iterrows():
    lat_scale = 111.32  # 1 degree of latitude ≈ 111.32 km
    lon_scale = 111.32 * math.cos(
        math.radians((airport["lat"] + jfk_loc[0]) / 2)
    )  # Adjust for longitude
    lat_diff_km = abs(airport["lat"] - jfk_loc[0]) * lat_scale
    lon_diff_km = abs(airport["lon"] - jfk_loc[1]) * lon_scale
    euc_distance = math.sqrt(lat_diff_km**2 + lon_diff_km**2)
    lat1 = math.radians(jfk_loc[0])
    lon1 = math.radians(jfk_loc[1])
    lat2 = math.radians(airport["lat"])
    lon2 = math.radians(airport["lon"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    exp_one = (2 * math.sin(dlat / 2) * math.cos(dlon / 2)) ** 2
    exp_two = (2 * math.cos((lat1 + lat2) / 2) * math.sin(dlon / 2)) ** 2
    geo_distance = R * math.sqrt(exp_one + exp_two)
    # Store distances
    df.at[index, "euc_dist"] = euc_distance
    df.at[index, "geo_dist"] = geo_distance

# print(df.loc[df["euc_dist"].idxmax()])

plt.figure(figsize=(10, 6))
plt.hist(df["euc_dist"], bins=30, alpha=0.5, color="blue")

plt.xlabel("Euclidean distance")
plt.ylabel("Count")
plt.title("Distribution of the euclidean distances between the eirports and JFK")
plt.grid(True)

# plt.show()

plt.figure(figsize=(10, 6))
plt.hist(df["geo_dist"], bins=30, alpha=0.5, color="blue")

plt.xlabel("Geodesic distance")
plt.ylabel("Count")
plt.title("Distribution of the geodesic distances between the eirports and JFK")
plt.grid(True)

# plt.show()

def plot_multiple_flight_routes(faa_codes):
    nyc_airport = df[df["faa"] == "EWR"]
    if nyc_airport.empty:
        print("Error: No airport found for EWR.")
        return

    nyc_lat = nyc_airport["lat"].values[0]
    nyc_lon = nyc_airport["lon"].values[0]

    fig = px.scatter_geo(
        lat=[],
        lon=[],
        title="Flight Routes from NYC (EWR)",
        projection="natural earth",
    )

    for faa_code in faa_codes:
        airport = df[df["faa"] == faa_code.upper()]

        if airport.empty:
            print(f"Warning: No airport found with FAA code '{faa_code}'.")
            continue

        airport_name = airport["name"].values[0]
        airport_lat = airport["lat"].values[0]
        airport_lon = airport["lon"].values[0]
        airport_tzone = airport["tzone"].values[0]

        is_us = str(airport_tzone).startswith(("America/", "Pacific/"))

        fig.add_trace(
            go.Scattergeo(
                lon=[nyc_lon, airport_lon],
                lat=[nyc_lat, airport_lat],
                mode="lines",
                line=dict(width=2, color="blue"),
                name=f"NYC → {airport_name}",
            )
        )

        fig.add_trace(
            go.Scattergeo(
                lon=[airport_lon],
                lat=[airport_lat],
                text=[airport_name],
                mode="markers",
                marker=dict(size=8, color="green"),
                name=f"{airport_name}",
            )
        )

    fig.show()

# Example usage
# plot_multiple_flight_routes(["LAX", "JFK", "SFO", "AAF", "AAP"])



# Example Usage:
# plot_flight_route("LAX")
# plot_flight_route("HNL")  # the flight route line is broken
# plot_flight_route("TZR")


# =============== Data processing for flights_database.db =============== 

# =============== Part 3 =============== 
# verify the distances 
# database_path 
db_path = "../flights_database.db"

# transform calculate_geo_distance function to a function that can be used in SQL queries
def compute_geo_distance(lat1, lon1, lat2, lon2):
    R = 6378.1370 
    # geo_distance
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    exp_one = (2 * math.sin(dlat / 2) * math.cos(dlon / 2)) ** 2
    exp_two = (2 * math.cos((lat1 + lat2) / 2) * math.sin(dlon / 2)) ** 2
    geo_distance = R * math.sqrt(exp_one + exp_two)
    return geo_distance

# connect to the database
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    
    # query the first 200 flights with origin and destination airport coordinates
    cursor.execute("""
        SELECT f.origin, f.dest, f.distance, a1.lat, a1.lon, a2.lat, a2.lon
        FROM flights AS f
        JOIN airports AS a1 ON f.origin = a1.faa
        JOIN airports AS a2 ON f.dest = a2.faa
        LIMIT 200;
    """)
    flights_data = cursor.fetchall()

# calculate the geo and database distances for each flight
geo_distances = []
db_distances = []
indices = []

for i, (origin, dest, db_distance, lat1, lon1, lat2, lon2) in enumerate(flights_data):
    geo_distance = compute_geo_distance(lat1, lon1, lat2, lon2)
    geo_distances.append(geo_distance)
    db_distances.append(db_distance * 1.60934)  # convert miles to kilometers
    indices.append(i)

# plot the computed and database distances for the first 200 flights
plt.figure(figsize=(12, 6))
plt.plot(indices, geo_distances, label="Calculated Distance (km)", linestyle="-")
plt.plot(indices, db_distances, label="Database Distance (km)", linestyle="--")
plt.xlabel("Flight Index")
plt.ylabel("Distance (km)")
plt.title("Comparison of Computed vs. Database Flight Distances (First 200 Flights)")
plt.legend()
# plt.show()



# extract NYC airports
cursor.execute("""
    SELECT DISTINCT origin FROM flights;
""")
unique_origins = [row[0] for row in cursor.fetchall()]

query = f"""
    SELECT * FROM airports
    WHERE faa IN ({', '.join(['?'] * len(unique_origins))});
    """
df_unique_origins = pd.read_sql_query(query, conn, params=unique_origins)

# print(df_unique_origins)
conn.close()

# analyse flights per day
# retrieve the number of flights per day for a specific NYC airport
def plot_flight_destinations(month, day, airport):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # query the number of flights to each destination from the specified airport
        cursor.execute("""
            SELECT dest, COUNT(*) AS flight_count
            FROM flights
            WHERE month = ? AND day = ? AND origin = ?
            GROUP BY dest
            ORDER BY flight_count DESC;
        """, (month, day, airport))
        
        results = cursor.fetchall()

    destinations = [row[0] for row in results]
    flight_counts = [row[1] for row in results]

    plt.figure(figsize=(12, 6))
    plt.bar(destinations, flight_counts, color="skyblue")
    plt.xlabel("Destination Airport")
    plt.ylabel("Number of Flights")
    plt.title(f"Flights from {airport} on {month}/{day}")
    plt.xticks(rotation=90)
    plt.show()

# plot_flight_destinations(1, 1, "JFK")  # plot the flight destinations for JFK on January 1st
conn.close()

# retrieve flight statistics
def get_flight_statistics(month, day, airport):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # statistics for total flights
        cursor.execute("""
            SELECT COUNT(*) FROM flights
            WHERE month = ? AND day = ? AND origin = ?;
        """, (month, day, airport))
        total_flights = cursor.fetchone()[0]

        # statistics for unique destinations
        cursor.execute("""
            SELECT COUNT(DISTINCT dest) FROM flights
            WHERE month = ? AND day = ? AND origin = ?;
        """, (month, day, airport))
        unique_destinations = cursor.fetchone()[0]

        # find the most visited destination
        cursor.execute("""
            SELECT dest, COUNT(*) AS flight_count
            FROM flights
            WHERE month = ? AND day = ? AND origin = ?
            GROUP BY dest
            ORDER BY flight_count DESC
            LIMIT 1;
        """, (month, day, airport))
        most_visited = cursor.fetchone()
        
        statistics = {
            "total_flights": total_flights,
            "unique_destinations": unique_destinations,
            "most_visited": most_visited[0] if most_visited else None,
            "most_visited_count": most_visited[1] if most_visited else 0
        }
    
    return statistics

stats = get_flight_statistics(1, 1, "JFK") # get flight statistics for JFK on January 1st
# print(stats)  
# conn.close()

def average_delay_per_carrier_plot():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # query the number of flights to each destination from the specified airport
        cursor.execute("""SELECT AVG(f.dep_delay), f.carrier, al.name 
            FROM flights f 
            JOIN airlines al ON f.carrier = al.carrier 
            GROUP BY f.carrier""")
        
        results = cursor.fetchall()
    
    plt.figure(figsize=(12, 6))
    plt.bar([x[2] for x in results], [x[0] for x in results], color="skyblue")
    plt.xlabel("Airlines")
    plt.ylabel("Average delay")
    plt.title("Average delay for each airline")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()
    conn.close()

# average_delay_per_carrier_plot()

def delays_month_destination(months, destination):
    with sqllite3.connect(db_path) as conn:
        cursor = conn.cursos()
        query = f"""
        SELECT COUNT(*)
        FROM flights
        WHERE dest = '{destination}' AND month IN {months} AND arr_delay > 0
        """
        results = conn.execute(query).fetchone()[0]
    conn.close()
    return results

# print(delays_month_destination((1,2,3), 'ORD'))

def bins_distance_delay():
    conn = sqllite3.connect(db_path)
    # Define the bins
    bins = range(0, 3001, 200)
    
    # Query the database
    query = """
    SELECT distance, arr_delay
    FROM flights
    """
    df = pd.read_sql_query(query, conn)
    
    # Bin the distances
    df['distance_bins'] = pd.cut(df['distance'], bins)
    
    # Group by the bins and calculate the mean arrival delay
    grouped = df.groupby('distance_bins')['arr_delay'].mean().reset_index()
    
    # Extract the midpoint of each bin for plotting
    grouped['bin_midpoint'] = grouped['distance_bins'].apply(lambda x: x.mid)
    
    # Plot the scatter plot
    plt.scatter(grouped['bin_midpoint'], grouped['arr_delay'])
    plt.xlabel('Distance Bin Midpoint')
    plt.ylabel('Average Arrival Delay')
    plt.title('Average Arrival Delay by Distance Bin')
    plt.grid(True)
    plt.show()
    conn.close()

# bins_distance_delay()

def bins_distance_delay_per_carrier():
    conn = sqllite3.connect(db_path)
    # Define the bins
    bins = range(0, 3001, 200)
    
    # Query the database
    query = """
    SELECT distance, arr_delay, carrier
    FROM flights
    """
    df = pd.read_sql_query(query, conn)
    
    # Bin the distances
    df['distance_bins'] = pd.cut(df['distance'], bins)
    
    # Group by both distance_bins and carrier, and calculate the mean arrival delay
    grouped = df.groupby(['distance_bins', 'carrier'])['arr_delay'].mean().reset_index()
    
    # Extract the midpoint of each bin for plotting
    grouped['bin_midpoint'] = grouped['distance_bins'].apply(lambda x: x.mid)

    # Filter carriers with at least 10 bins with data 
    filtered_carriers = non_missing_counts[non_missing_counts['n_non_missing'] >= 10]['carrier']

    # Filter the original DataFrame to include only the selected carriers
    grouped_filtered = grouped[grouped['carrier'].isin(filtered_carriers)]
    
    # Get the list of filtered carriers
    carriers = grouped_filtered['carrier'].unique()
    
    # Determine the grid size for subplots
    n_carriers = len(carriers)
    n_cols = 3  # Number of columns in the grid
    n_rows = (n_carriers // n_cols) + (1 if n_carriers % n_cols != 0 else 0)
    
    # Create a grid of subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 3))
    axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration
    
    # Plot a line plot for each filtered carrier in its own subplot
    for i, carrier in enumerate(carriers):
        ax = axes[i]
        carrier_data = grouped_filtered[grouped_filtered['carrier'] == carrier]
        ax.plot(carrier_data['bin_midpoint'], carrier_data['arr_delay'], marker='o', label=carrier)
        ax.set_title(f'Carrier: {carrier}')
        ax.set_xlabel('Distance Bin Midpoint')
        ax.set_ylabel('Average Arrival Delay')
        ax.grid(True)
        ax.legend()
    
    # Hide any unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')
    
    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()
    conn.close()

# bins_distance_delay_per_carrier()

