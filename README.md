
## Flights Analysis Dashboard✈️
This project is belong to the **XB_0112 Data Engineering** group assignment. It provides an interactive dashboard to visualize airport and flight data using Python and Plotly. The dashboard includes functionalities such as ...
### Project Report && Project Inrtoduction
[Project Report](project%20report.md) && [flights_part12.pdf](project_introduction/flights_part12.pdf) 

## Dataset Overview
**airports.csv** contains **information on all destination airports** for flights departing from **New York City in 2023**. Each row represents a **destination airport** where a flight from NYC landed. The dataset includes key details such as the airport's **FAA code, name, latitude, longitude, altitude, time zone, and daylight saving time information**.

**worldcities.csv** contains over 4 million unique cities and towns from every country in the world. [Source](https://simplemaps.com/data/world-cities)


## Project Features
* **Multi-Language Support**
  * The interface supports English, Chinese, Croatian, and Dutch. Users can switch languages in real time, with all interface text dynamically updated through a translation table.
* **Multi-Page Switching**
  * Two main pages are provided:
    * **Dashboard:** Displays airport data, map visualizations, flight path and flight time estimations, and various data statistics.
    * **New Data Entry:** Allows users to input new airport data, which is updated and displayed in real time during the current session.
* **Map Visualization and Flight Path Simulation**
  * Utilizes Plotly's Scatter Mapbox to render a map showing airport locations.
  * Based on the user's input for departure and arrival cities, the system automatically calculates the nearest airports, the flight path distance, and the estimated flight time, then displays the flight progress on the map in real time (to speed up execution, world city coordinates have been added from **worldcities.csv**. [Data Source](https://simplemaps.com/data/world-cities)).
* **Data Statistics and Dynamic Visualizations**
  * Provides multiple statistical charts:
    * Altitude distribution histogram
    * Time zone distribution histogram
    * Scatter plot of altitude vs. distance
  * These visualizations help users intuitively understand the distribution and characteristics of the airport data.
* **Data Entry**
  * New data is entered via a form.
  * The new data is stored in `session_state` and merged with the original data for display on the Dashboard.
* **Data Query**
  * Users can input an FAA code or airport name to retrieve the full row of information. Fuzzy search allows users to query without needing an exact match.
* **Interactive Sidebar Control**
  * The sidebar includes built-in controls for airport queries, map mode switching (US/World), time zone filtering, and more, allowing users to easily adjust and query the displayed map content.


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
pip install pandas plotly geopy matplotlib timezonefinder seaborn numpy scikit-learn networkx dash math streamlit base64
```
If you use Jupyter Notebook or Google Colab
```bash
!pip install pandas plotly geopy matplotlib timezonefinder seaborn numpy scikit-learn networkx dash math streamlit base64
```
### Run
```bash
python3 flights.py
```
**Run the dashboard on your own machine**
```bash
streamlit run dashboard.py
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
│-- project_introduction/  # Project Task Documents Folder
│-- project report.md     # Detailed project report
│-- README.md             # Project documentation
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



