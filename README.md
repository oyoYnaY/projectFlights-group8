# projectFlights-group8-
## Flights Analysis Dashboard✈️
This project is belong to the **XB_0112 Data Engineering** group assignment. It provides an interactive dashboard to visualize airport and flight data using Python and Plotly. The dashboard includes functionalities such as global airport distribution, flight route visualization, and distance calculations.

### Features
- **Global US airport distribution** – Visualize all airports on a US map.
- **Flight route visualization** – Display routes between New York and other airports.
- **Distance calculations** – Compute Euclidean and geodesic distances.
- ...

### Installation & Setup
#### Clone the repository
```bash
git clone https://github.com/oyoYnaY/projectFlights-group8.git
cd flights-analysis
```

#### [optional] Create a virtual environment and activate it
Since macOS restricts global pip installation, the best solution is to create a virtual environment:
```bash
python3 -m venv myenv
source myenv/bin/activate  # macOS/Linux
myenv\Scripts\activate     # Windows
```

#### Download libary
```bash
pip install --upgrade pip    
pip install plotly
pip install geopy
```
#### Run
```bash
python3 flights.py
```

### Git workflow
| Step | Command |
|------|---------|
| **Clone the repository** | `git clone https://github.com/oyoYnaY/projectFlights-group8.git` |
| **Create a new branch** | `git checkout -b feature-branch-name` |
| **Commit changes** | `git add . && git commit -m "Your commit message"` |
| **Push to remote repository** | `git push origin feature-branch-name` |
| **Create a Pull Request** | Navigate to GitHub → Click on "New Pull Request" |
| **Code review** | The team members review the code |
| **Merge PR** | `git merge feature-branch-name && git push origin main` |
| **Delete merged branch** | `git branch -d feature-branch-name && git push origin --delete feature-branch-name` |
| **Deploy the code** | Manually run `git pull` on the server |

Following this workflow ensures an organized and efficient development process.


