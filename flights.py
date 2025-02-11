import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic


# read airports.csv
df = pd.read_csv("airports.csv")

