
## Flights Analysis Dashboard✈️
This project is belong to the **XB_0112 Data Engineering** group assignment. It provides an interactive dashboard to visualize airport and flight data using Python and Plotly. The dashboard includes functionalities such as global airport distribution, flight route visualization, and distance calculations.
### Project Report && Project Inrtoduction
[Project Report](project%20report.md) && [flights_part12.pdf](project_introduction/flights_part12.pdf) 

## Dataset Overview
This dataset contains **information on all destination airports** for flights departing from **New York City in 2023**. Each row represents a **destination airport** where a flight from NYC landed. The dataset includes key details such as the airport's **FAA code, name, latitude, longitude, altitude, time zone, and daylight saving time information**.

Since all flights originate from **New York City airports** (`EWR`- Newark Liberty International Airport), this dataset does **not** contain departure airport information—only details about where flights arrived.

---

### Dataset Fields
This dataset contains **information on all destination airports** for flights departing from **New York City in 2023**.  
Each row represents a **destination airport** where a flight from NYC landed. The dataset includes key details such as:
- **FAA code** (Three-letter airport code)
- **Airport name**
- **Latitude & Longitude** (Geographical coordinates)
- **Altitude** (Airport elevation in feet)
- **Time zone** (UTC offset)
- **Daylight saving time (DST) usage**

## Project Features
- **Global US airport distribution** – Visualize all airports on a US map.
- **Flight route visualization** – Display routes between New York and other airports.
- **Distance calculations** – Compute Euclidean and geodesic distances.
- ...(update later)

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
pip install --upgrade pip    
pip install plotly
pip install geopy
```
### Run
```bash
python3 flights.py
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

### Git Collaboration Guidelines
[CONTRIBUTING.md](CONTRIBUTING.md)



