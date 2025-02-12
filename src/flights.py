import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from timezonefinder import TimezoneFinder

# read airports.csv
df = pd.read_csv("../data/airports.csv") 

# descriptive statistics and data preprocessing
print("first 5 rows of the dataset:\n", df.head())  # display first few rows
print("dataset information:")
df.info()  # display dataset information

print("descriptive statistics:\n", df.describe())  # display descriptive statistics
print("missing values in each column:\n", df.isnull().sum())  # check for missing values

# display unique time zones and their corresponding tz values
unique_tz_mapping = df[["tzone", "tz"]].dropna().drop_duplicates()
print(unique_tz_mapping)

# inferring missing values instead of deleting them
tf = TimezoneFinder()
df["tzone"] = df.apply(lambda row: tf.timezone_at(lng=row["lon"], lat=row["lat"]) if pd.isnull(row["tzone"]) else row["tzone"], axis=1)
# update tz values based on the inferred tzone
tz_mapping_dynamic = dict(df[["tzone", "tz"]].dropna().drop_duplicates().values)
df["tz"] = df.apply(lambda row: tz_mapping_dynamic.get(row["tzone"], row["tz"]) if pd.isnull(row["tz"]) else row["tz"], axis=1)
# infer dst based on the most common dst setting per tzone
dst_mapping = df.groupby("tzone")["dst"].apply(lambda x: x.mode().iloc[0] if not x.isna().all() else "N").to_dict()

# fill missing dst values
df["dst"] = df.apply(lambda row: dst_mapping.get(row["tzone"], row["dst"]) if pd.isnull(row["dst"]) else row["dst"], axis=1)

# check for missing values after inference
print("missing values after inference:\n", df.isnull().sum())
print(df[df["tz"].isnull()])
print(df[df["tzone"] == "America/Boise"][["tzone", "tz"]].dropna().drop_duplicates())
df.loc[df["tzone"] == "America/Boise", "tz"] = -7
print("missing values after final fix:\n", df.isnull().sum())

# explore relationships within the dataset
# scatter plot: altitude vs latitude
plt.figure(figsize=(10, 6))
plt.scatter(df["lat"], df["alt"], alpha=0.5, color="blue")

plt.xlabel("Latitude")
plt.ylabel("Altitude (feet)")
plt.title("Scatter Plot: Airport Altitude vs Latitude")
plt.grid(True)

plt.show()


# # plot global airport distribution, with color coded by 'alt' (altitude)
# fig_global = px.scatter_geo(df, 
#                             lat="lat", lon="lon", 
#                             hover_name="name",
#                             color="alt",  # color by altitude
#                             title="global airport distribution (colored by altitude)",
#                             projection="natural earth",
#                             color_continuous_scale="plasma")  # choose color scale
# fig_global.show()

# # filter only us airports
# df_us = df[df["tzone"].str.startswith("America")] 

# # plot us airport distribution, with color coded by 'alt' (altitude)
# fig_us = px.scatter_geo(df_us, 
#                         lat="lat", lon="lon", 
#                         hover_name="name",
#                         color="alt",  # color by altitude
#                         title="us airport distribution (colored by altitude)",
#                         scope="usa",
#                         color_continuous_scale="plasma")
# fig_us.show()
