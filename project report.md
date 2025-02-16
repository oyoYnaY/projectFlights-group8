# Data Engineering - Project Report

### Project Group Members

- **A. Lis (Adel), ali248**
- **M. Taciak (Monika), mta275**
- **N. Micek (Nikolina), nmk490**
- **Y. Yan (Yoyo), yyn480**

---

## Data Fields

| **Column** | **Description**                                                    | **Example Value**                       | **Data Type** |
| ---------- | ------------------------------------------------------------------ | --------------------------------------- | ------------- |
| `faa`      | **FAA Code** (Three-letter identifier for the destination airport) | `"AAF"` (Apalachicola Regional Airport) | `object`      |
| `name`     | **Destination Airport Name**                                       | `"Apalachicola Regional Airport"`       | `object`      |
| `lat`      | **Latitude** (Geographical coordinate of the airport)              | `29.72750092`                           | `float64`     |
| `lon`      | **Longitude** (Geographical coordinate of the airport)             | `-85.02749634`                          | `float64`     |
| `alt`      | **Altitude** (Elevation of the airport in feet)                    | `20`                                    | `int64 `      |
| `tz`       | **Time Zone Offset** (Relative to UTC)                             | `-5` (Apalachicola in UTC-5)            | `float64`     |
| `dst`      | **Daylight Saving Time (DST) Usage**                               | `"A"` (Active, follows DST)             | `object`      |
| `tzone`    | **[Timezone in "tz" (Olson) format](https://en.wikipedia.org/wiki/Tz_database)** | `"America/New_York"`      | `object`      |

---

## Libraries Used

The following Python libraries were used in this project for **data processing, visualization, and geospatial analysis**:

- `pandas` – For reading and processing the dataset.
- `plotly` – For interactive visualizations.
- `geopy` – For geographic distance calculations.
- `matplotlib` - For descriptive statistics
- `timezonefinder` - For inferring the missing value
- `seaborn` - Statistical data visualization
- `numpy` - For numerical operations
- `scikit-learn` - For cluster data
- `networkx` - For building the airport network
- `Nominatim` - For finding the nearest airport to a city
- `dash` - Used to initially build and test dashboard concepts and functionality in a demo environment.
- `math` - Calculate distance

### Data Cleaning

```python
print("missing values in each column:\n", df.isnull().sum())
```

missing values in each column:
faa 0
name 0
lat 0
lon 0
alt 0
tz 48
dst 48
tzone 119

No missing values in FAA codes, airport names, coordinates, and altitude.
Missing tz (time zone offset) and dst (daylight saving time info) in 48 rows.
tzone (time zone name) missing in 119 rows, which may impact time-based analysis.

Since tz (UTC offset), dst (Daylight Saving Time), and tzone (time zone name) are related, we can infer their missing values instead of dropping them. This will help retain more data and improve the accuracy of our analysis.

### Data Transformation

Since altitude (alt) is given in feet, we need to convert it to meters.

```python
df["alt_meters"] = df["alt"] * 0.3048 # use alt_meters to replace alt
```

Convert tz to Integer

```python
df["tz"] = df["tz"].astype("Int64")
```

|      | **Data Type** |
| ---- | ------------- |
| `tz` | Int64         |

### Descriptive Statistics

After inferring the missing values, we used various charts and graphs to analyze patterns and relationships between different attributes in the dataset.

```python
print("missing values in each column:\n", df.isnull().sum())
```

|                  | Latitude (`lat`) | Longitude (`lon`) | Altitude (`alt`) | Time Zone (`tz`) | alt_meters  |
| ---------------- | ---------------- | ----------------- | ---------------- | ---------------- | ----------- |
| **Count**        | 1251             | 1251              | 1251             | 1251             | 1251        |
| **Mean**         | 40.9333          | -103.4659         | 1121.9920        | -6.3333          | 341.983164  |
| **Std Dev**      | 10.1935          | 28.1121           | 1602.5218        | 2.0812           | 488.448652  |
| **Min**          | 19.7214          | -176.6460         | -115.0000        | -10.0000         | -35.052000  |
| **25%**          | 34.1035          | -117.8760         | 96.0000          | -8.0000          | 29.260800   |
| **50% (Median)** | 39.3451          | -95.9125          | 551.0000         | -6.0000          | 167.944800  |
| **75%**          | 44.3167          | -83.2863          | 1226.0000        | -5.0000          | 373.684800  |
| **Max**          | 71.29            | 174.11            | 9070.000000      | 8.00             | 2764.536000 |

This dataset contains **1251 records**, with each row representing a **landing airport**.  
Most destinations are primarily located in the **mid-latitude regions (30°N to 50°N)**, with some airports in **tropical and Arctic regions**.

The majority of airports are in **North America**, within the **UTC-10 to UTC-5 time zones**, but some flights reach **Asia and the Pacific**.  
Most airports are **near sea level**, though a few **high-altitude airports exist in mountainous regions**.

#### To better understand the relationships between different variables, we can create several visualizations.

<div align="center">
  <img src="figures/Figure_1.png" alt="Figure 1: Altitude vs Latitude" width="45%"/>
  <img src="figures/Figure_2.png" alt="Figure 2: tz" width="45%"/>
  <img src="figures/Figure_3.png" alt="Figure 3: dst" width="45%"/>
</div>

The following airports **do not observe DST** and are located in specific regions:  
**Airports around latitude ~20° and longitude ~-160°**, **Airports around latitude ~30-35° and longitude ~-110°**. Later can visualizing these airports on a map to see the locations.

### Visualization

#### World Map && US Map

<div align="center">
  <img src="figures/Figure_5.png" alt="Figure 5: World map" width="45%"/>
  <img src="figures/Figure_4.png" alt="Figure 4: US map" width="45%"/>
</div>

By cross-validating the world map and the U.S. map, we can identify that only two airports are located outside the United States:
Taszári Air Base (FAA: TZR) – located in Hungary.
Oryol Yuzhnyy Airport (FAA: OEL) – located in Oryol, Russia.

#### Plot Multiple Lines

We assume that all starting points are located at John F. Kennedy Airport in New York City to simplify the process of drawing flight paths.

#### Euclidean Distance && Geodesic Distance

Distances calculated manually with formulas. The output is given in kilometers.

<div align="center">
  <img src="figures/euc_dist_hist.png" alt="Histogram of the euclidean distances between airports in the list and JFK" width="45%"/>
  <img src="figures/geodesic_dist_hist.png" alt="Histogram of the geodesic distances between airports in the list and JFK" width="45%"/>
</div>

#### Time Zones

<div align="center">
  <img src="figures/Figure_2.png" alt="Figure 2: tz" width="45%"/>
  <img src="figures/Figure_11.png" alt="Figure 11: time zone" width="45%"/>
</div>

In the timezone data, most airports are located in the Eastern (America/New_York) and Central (America/Chicago) time zones, while a small number of airports are in Europe (Moscow/Budapest). The number of airports in the Western time zones (Pacific and Mountain) is relatively lower due to the vast and sparsely populated regions, which aligns with our previous map analysis.

Acoording to the figure, we found 3 time zones in Alaska. America/Adak, America/Nome, America/Anchorage.

Alaska (America/Anchorage) has significantly more airports than other regions, likely due to weak road infrastructure, making air travel essential for many remote areas. This has led to a high number of small regional airports and a well-developed feeder airline network.

The presence of airports in the America/Indiana/Indianapolis time zone suggests historical complexities in time regulation in that region. Parts of Indiana follow independent time zone rules within the Eastern Time Zone, and America/Indiana/Indianapolis has its own time zone designation, possibly due to historical reasons.

The first figure highlights airports in UTC 8. After extracting airports with tz=8, we found that all of them are in the America/Los_Angeles time zone. The correct tz value should be -8, indicating an error in the database entry.

#### More Visualizations

#### Cluster

Use DBSCAN. Set the range is 80km.

<div align="center">
  <img src="figures/Figure_6.png" alt="Cluster" width="100%"/>
</div>

#### Undirected Airport Graph

Choose 5 neighbors.

<div align="center">
  <img src="figures/Figure_7.png" alt="Graph" width="100%"/>
</div>

In the current DBSCAN results with an 80km radius:

Texas (Houston, Dallas) forms multiple clusters.
The East Coast has several dense clusters.
The West Coast (Los Angeles, San Francisco) does not form dense clusters.
This may be related to economic patterns and industry structure:

East Coast & Texas → High economic activity areas

New York (JFK, LGA, EWR) is one of the world's largest financial centers, with extremely high economic activity and a dense network of surrounding airports.
Texas (Dallas, Houston) is an energy hub with strong business connections, leading to a dense airport network.
Major East Coast cities (Boston, Philadelphia, Washington, etc.) have a high concentration of commercial flights, resulting in high airport density.
West Coast (California) → Fewer airports but stronger hubs

The number of airports is smaller, but they serve as major hubs.
Due to the greater distances between cities in California, airports are not as densely packed as in New York or Texas.
In DBSCAN clustering, they are more likely to be classified as outliers rather than clusters.
The results of the undirected airport network graph are similar to the DBSCAN clustering results.

## Dashboard Features Demo

This part for add any ideas and build the basic demo to test your idea.

### Idea1-input 2 cities name, find the nearest airport to 2 given city, then plot the flight path between them

```python
plot_flight_between_cities("New York", "London")
plot_flight_between_cities("San Francisco", "Tokyo")
```

<div align="center">
  <img src="figures/Figure_8.png" alt="New York->London" width="45%"/>
  <img src="figures/Figure_9.png" alt="San Francisco->Tokyo" width="45%"/>
</div>

### Idea2-simulate a flight from JFK to the nearest airport in each cluster

Select the nearest airports from the top ten clusters in the previous aggregation map, choosing the airport closest to the cluster center.

```python
if __name__ == "__main__":
    app.run_server(debug=True)
```

<div align="center">
  <img src="figures/Figure_10.png" alt="Simulate" width="100%"/>
</div>

### Idea3-for each flight, compute the the compass direction from NYC to the destination airport, and examine the directional distribution of the departing flights.

Compute the direction (in degrees °) of each route leaving from NYC and show the distribution over a polar histogram.
The study reveals the most taken directions from NYC, and, therefore prefered destinations.

```python
df_dest['bearing'] = df_dest.apply(lambda row: calculate_bearing(nyc_lat, nyc_lon, row['lat'], row['lon']), axis=1)
```

<div align="center">
  <img src="figures/Figure_12.png" alt="New York->London" width="85%"/>
  <img src="figures/Figure_13.png" alt="San Francisco->Tokyo" width="85%"/>
</div>
