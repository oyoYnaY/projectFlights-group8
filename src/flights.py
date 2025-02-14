import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from timezonefinder import TimezoneFinder
import seaborn as sns
import math

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
df["tzone"] = df.apply(lambda row: tf.timezone_at(lng=row["lon"], lat=row["lat"]) if pd.isnull(row["tzone"]) else row["tzone"], axis=1)
# update tz values based on the inferred tzone
tz_mapping_dynamic = dict(df[["tzone", "tz"]].dropna().drop_duplicates().values)
df["tz"] = df.apply(lambda row: tz_mapping_dynamic.get(row["tzone"], row["tz"]) if pd.isnull(row["tz"]) else row["tz"], axis=1)

# Need Fix:
# infer dst based on the most common dst setting per tzone
dst_mapping = df.groupby("tzone")["dst"].apply(lambda x: x.mode().iloc[0] if not x.isna().all() else "N").to_dict()
# fill missing dst values
df["dst"] = df.apply(lambda row: dst_mapping.get(row["tzone"], row["dst"]) if pd.isnull(row["dst"]) else row["dst"], axis=1)

# # check for missing values after inference
# print("missing values after inference:\n", df.isnull().sum())
# print(df[df["tz"].isnull()])
# print(df[df["tzone"] == "America/Boise"][["tzone", "tz"]].dropna().drop_duplicates()) # check for missing values in America/Boise
# df.loc[df["tzone"] == "America/Boise", "tz"] = -7 # fix missing values in America/Boise
# print("missing values after final fix:\n", df.isnull().sum()) 

# convert altitude to meters
df["alt_meters"] = df["alt"] * 0.3048
df["tz"] = df["tz"].astype("Int64") # convert tz to integer
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
sns.countplot(x=df["tz"], hue=df["tz"], palette="coolwarm", legend=False) 

plt.xlabel("Time Zone (UTC)")
plt.ylabel("Number of Airports")
plt.title("Number of Airports in Each Time Zone")
plt.grid(True)

plt.show()

# find airports that do not observe daylight saving time, later visualizing these airports on a map
df_no_dst = df[df["dst"] == "N"]

plt.figure(figsize=(10, 6))
sns.scatterplot(x=df_no_dst["lon"], y=df_no_dst["lat"], color="red")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Airports That Do NOT Observe DST")

# plt.show()


############################################################################################################################################################################
# Part 1
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
R = 6378.1370 # in kilometeres
jfk_data = df[df['faa'] == 'JFK']
jfk_loc = [jfk_data['lat'].iloc[0], jfk_data['lon'].iloc[0]]
df['geo_dist'] = None
df['euc_dist'] = None
for index, airport in df.iterrows():
    lat_scale = 111.32  # 1 degree of latitude ≈ 111.32 km
    lon_scale = 111.32 * math.cos(math.radians((airport['lat'] + jfk_loc[0]) / 2))  # Adjust for longitude
    lat_diff_km = abs(airport['lat'] - jfk_loc[0]) * lat_scale
    lon_diff_km = abs(airport['lon'] - jfk_loc[1]) * lon_scale
    euc_distance = math.sqrt(lat_diff_km**2 + lon_diff_km**2)
    lat1 = math.radians(jfk_loc[0])
    lon1 = math.radians(jfk_loc[1])
    lat2 = math.radians(airport['lat'])
    lon2 = math.radians(airport['lon'])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    exp_one = (2*math.sin(dlat/2)*math.cos(dlon/2))**2
    exp_two = (2*math.cos((lat1+lat2)/2)*math.sin(dlon/2))**2
    geo_distance = R * math.sqrt(exp_one+exp_two)
    # Store distances
    df.at[index, 'euc_dist'] = euc_distance
    df.at[index, 'geo_dist'] = geo_distance

print(df.loc[df["euc_dist"].idxmax()])

plt.figure(figsize=(10, 6))
plt.hist(df['euc_dist'], bins = 30, alpha=0.5, color="blue")

plt.xlabel("Euclidean distance")
plt.ylabel("Count")
plt.title("Distribution of the euclidean distances between the eirports and JFK")
plt.grid(True)

plt.show()

plt.figure(figsize=(10, 6))
plt.hist(df['geo_dist'], bins = 30, alpha=0.5, color="blue")

plt.xlabel("Geodesic distance")
plt.ylabel("Count")
plt.title("Distribution of the geodesic distances between the eirports and JFK")
plt.grid(True)

plt.show()
