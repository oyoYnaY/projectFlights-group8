
## Flights Analysis Dashboard✈️
This project, developed by the **XB_0112 Data Engineering** group 8, provides an interactive dashboard built with Python and Streamlit to visualize airport and flight data—with features including multi-language support, multi-page switching, real-time map visualization and flight path simulation using world city coordinates from worldcities.csv, dynamic data statistics, real-time data entry and query capabilities, and interactive sidebar controls.
### Project Report && Project Inrtoduction
[Project Report](project%20report.md) && [flights_part1-4.pdf](flights_part1-4.pdf) 

## Dataset Overview
`flights_database.db` is an **SQLite database** containing all flights departing from **New York City (NYC)** in **2023**, along with relevant information. The database consists of the following **five tables**: 
* airlines : contains information of the airlines operating from NYC.
* airports
* flights : A very large table containing all (425,352) flights departing NYC in
2023 including flight information.
* planes : Information on the planes used.
* weather : hour-by-hour information on the weather in 2023.

`airports.csv` contains **information on all destination airports** for flights departing from **New York City in 2023**. Each row represents a **destination airport** where a flight from NYC landed. The dataset includes key details such as the airport's **FAA code, name, latitude, longitude, altitude, time zone, and daylight saving time information**.

`worldcities.csv` contains about 47 thousand unique cities and towns from every country in the world. [Source](https://simplemaps.com/data/world-cities)


## Project Features

- **Multi-Language Support**
  - The interface supports English, Chinese, Croatian, Dutch, and Romanian.
  - Users can switch languages in real time. All interface text is dynamically updated via a translation dictionary.

- **Multi-Page Navigation**
  - The application is divided into several main pages:
    - **Dashboard:**  
      - Displays dynamic visualizations and key statistics derived from flight data.
      - Features histograms for altitude and time zone distributions, and a scatter plot of altitude vs. distance.
      - Provides a collapsible "Flight Details" section showing computed flight speed (km/h), flight progress simulation, and additional flight information.
    - **New Data Entry:**  
      - Allows users to input new data for any of the five tables (Airports, Flights, Airlines, Planes, Weather) via dedicated forms.
      - New data is stored in the session state and merged with the existing data for real-time display (data resets if the session is refreshed or restarted).
    - **General Results:**  
      - Presents a comprehensive analysis of the 2023 flights data.
      - Includes various visualizations.
    - **Developer Tool:**  
      - Provides an interface for executing arbitrary SQL queries (SELECT, INSERT, UPDATE, DELETE, etc.) on the 2023 database.
      - Supports real-time database modifications and testing.

- **Map Visualization and Flight Path Simulation**
  - Utilizes Plotly's Scatter Mapbox to render interactive maps showing airport locations.
  - Based on user input (city, FAA code, or airport name), the system automatically identifies the nearest airports, calculates the flight path distance and estimated flight time, and simulates flight progress on the map in real time. (Due to performance limitations, We use worldcities.csv to read the coordinates directly from it. World city coordinates added from **worldcities.csv**. [Data Source]
    
  **Note:** Since `airports.csv` contains only 1251 airports, inputting arbitrary city names may sometimes yield the same nearest airport, potentially causing calculation errors.

- **Dynamic Data Statistics and Visualizations**
  - The Dashboard features multiple real-time statistical charts and metrics:
    - **Altitude Distribution Histogram:** Visualizes the distribution of airport altitudes.
    - **Time Zone Distribution Histogram:** Shows the frequency of different time zones among airports.
    - **Scatter Plot of Altitude vs. Distance:** Explores the relationship between airport altitude and distance from New York.
    - **Airlines and Average Departure Delay Bar Chart:** Highlights the average departure delays for each airline.
    - **Aircraft Manufacturers Pie Chart:** Illustrates the distribution of aircraft manufacturers.
    - **Real-Time Summary Statistics:**  
      - **Unique Destinations:** Total number of distinct destination airports.
      - **Most Visited Destination:** The destination with the highest number of flights.
      - **Aircraft Types and Counts:** A table listing different aircraft types and their counts.
  - All visualizations update dynamically based on the user-selected date range and other filters.

- **Interactive Sidebar Controls**
  - The sidebar includes controls for:
    - Querying flights by a specified date range.
    - Inputting departure and arrival information (city, FAA code, or airport name) to simulate flight paths.
    - Switching between map modes (US/World) and filtering data by time zone.
## Installation & Setup
### Clone the repository
```bash
git clone https://github.com/oyoYnaY/projectFlights-group8.git
```

### [optional] Create a virtual environment and activate it
Since macOS restricts global pip installation, the best solution is to create a virtual environment:
```bash
python3 -m venv myenv
source myenv/bin/activate  # open virtual environment on macOS/Linux
myenv\Scripts\activate     # virtual environment on Windows
^C #close the virtual environment
```

### Download libary
```bash
pip install pandas plotly geopy matplotlib timezonefinder seaborn numpy scikit-learn networkx dash math streamlit base64 datetime db-sqlite3
```
If you use Jupyter Notebook or Google Colab
```bash
!pip install pandas plotly geopy matplotlib timezonefinder seaborn numpy scikit-learn networkx dash math streamlit base64 datetime db-sqlite3
```
### Run
```bash
python3 flights.py
```
**Run the dashboard on your own machine**
```bash
streamlit run helloDash.py
```

### Project Structure
```
PROJECTFLIGHTS-GROUP8/
|-- /.github/workflows/   # Auto test
│-- data/                 # Contains dataset files (e.g., CSVs)
│-- figures/              # Stores generated visualizations (e.g., PNGs)
│-- src/                  # Source code directory 
│-- .gitignore            
│-- CONTRIBUTING.md       # Guidelines for contributors
│-- project_introduction/ # Project Task Documents Folder
│-- project report.md     # Detailed project report
│-- README.md             # Project documentation
│-- flights_database.db   # Database
│-- flights_part1-4.pdf   # Assignment introduction
```
### Git Collaboration Guidelines
[CONTRIBUTING.md](CONTRIBUTING.md)

### Git workflow
| Step | Command |
|------|---------|
| **Clone the repository** | `git clone https://github.com/oyoYnaY/projectFlights-group8.git` |
| **Fetch origin** | `git fetch origin` |
| **Create a new branch && Switch to the new branch** | `git checkout -b 6-add-linkes-to-readme` |
| **Switch to an existing branch** | `git checkout branch-name` |
| **Commit changes** | `git add . && git commit -m "Your commit message"` |
| **Push to remote repository** | `git push origin feature-branch-name` |
| **Create a Pull Request** | Navigate to GitHub → Click on "New Pull Request" |
| **Code review** | The team members review the code |
| **Merge PR** | `git merge feature-branch-name && git push origin main` |
| **Delete merged branch** | `git branch -d feature-branch-name && git push origin --delete feature-branch-name` |
| **Deploy the code** | Manually run `git pull` on the server |

Following this workflow ensures an organized and efficient development process. **Ensure You Always Fetch the Latest Code Before Making Changes.**

**If your local changes have not been committed, but you want to sync with the remote repository:**

Store your changes.
```bash
git stash
```
Sync with the remote repository.
```bash
git pull origin main
```
Get your changes.
```bash
git stash pop
```



