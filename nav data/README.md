# Mutual Fund NAV Analysis

Console-based solution for the NAV data analysis assessment.  
The application ingests seven years of mutual fund NAV history for five funds,  
computes CAGR rankings, flags ±5 % NAV swings, and reports top/worst performers.

## Dataset

- Folder: `data/`
- Format: CSVs (`Fund Name, Date, NAV`)
- Coverage: 2018‑01‑01 to 2025‑12‑01 (fund dependent)
- Funds: Aditya Birla, Axis, Bandhan, Groww, Tata

## Requirements

- Python 3.10+
- Git
- pip
- Dependencies listed in `requirements.txt`:
  - `pandas`
  - `openpyxl`

## Setup

```powershell
python -m venv venv

3. Activate the environment
- Windows (PowerShell):
venv\Scripts\activate
- 
4. Install all dependencies
pip install -r requirements.txt


5. Run the analysis script
 & "C:/Users/RAJ RANA/AppData/Local/Programs/Python/Python313/python.exe" "d:/nav data/src/main.py" --data-dir "d:/nav data/data"


6. Review the generated outputs
- Console output:
     - Top 2 funds by CAGR
     - Worst 2 funds by CAGR
     - NAV swings greater than +5% (fund name, date, NAV change)
- Reports/graphs can be extended to output/ if required.
- The script normalizes headers automatically and overwrites results on each run,
so you always see the latest analysis.


-Project structure

├─ data/                    # Input CSVs
├─ output/                  # (optional) Generated reports/graphs
├─ src/
│  └─ main.py               # Entry point
├─ requirements.txt
└─ README.md

7. NOTES

- To add more funds, drop additional CSV/Excel files into data/; the script auto-discovers any .csv file in that folder.
