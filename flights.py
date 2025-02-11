import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic

# read airports.csv
df = pd.read_csv("airports.csv") 

# descriptive statistics and data preprocessing
print("first 5 rows of the dataset:\n", df.head())  # display first few rows
print("dataset information:")
df.info()  # display dataset information

print("descriptive statistics:\n", df.describe())  # display descriptive statistics
print("missing values in each column:\n", df.isnull().sum())  # check for missing values

# drop rows with missing values in 'tz', 'dst', and 'tzone' columns
df.dropna(subset=["tz", "dst", "tzone"], inplace=True)
print("missing values in each column after removal:\n", df.isnull().sum())  # verify missing values

# remove duplicate rows
df.drop_duplicates(inplace=True)

# plot global airport distribution, with color coded by 'alt' (altitude)
fig_global = px.scatter_geo(df, 
                            lat="lat", lon="lon", 
                            hover_name="name",
                            color="alt",  # color by altitude
                            title="global airport distribution (colored by altitude)",
                            projection="natural earth",
                            color_continuous_scale="plasma")  # choose color scale
fig_global.show()

# filter only us airports
df_us = df[df["tzone"].str.startswith("America")] 

# plot us airport distribution, with color coded by 'alt' (altitude)
fig_us = px.scatter_geo(df_us, 
                        lat="lat", lon="lon", 
                        hover_name="name",
                        color="alt",  # color by altitude
                        title="us airport distribution (colored by altitude)",
                        scope="usa",
                        color_continuous_scale="plasma")
fig_us.show()
