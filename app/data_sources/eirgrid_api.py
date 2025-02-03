import os
import requests
import pandas as pd
from datetime import datetime

RAW_PATH = os.path.join("app", "ml_models", "data", "raw")

if not os.path.exists(RAW_PATH):
    print(f"Warning: {RAW_PATH} does not exist. Please create it manually.")
else:
    print(f"Using existing directory: {RAW_PATH}")

EIRGRID_API_URL = "https://www.eirgrid.ie/api/graph-data"

DATA_TYPES = ["demandactual", "demandforecast", "fuelmix", "windactual", "windforecast", "co2emission", "co2intensity", "interconnection"]

TODAY = datetime.today().strftime("%d %b %Y")
CSV_DATE = datetime.today().strftime("%Y%m%d")

def fetch_eirgrid_data(data_type):
    """Fetches data from EirGrid API and saves as CSV."""
    params = {"area": data_type, "region": "ALL", "date": TODAY}
    
    response = requests.get(EIRGRID_API_URL, params=params)
    
    if response.status_code == 200:
        try:
            data = response.json()
            df = pd.DataFrame(data)

            csv_filename = f"{RAW_PATH}{data_type}_{CSV_DATE}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"{data_type} data saved to {csv_filename}")

            return df
        
        except Exception as e:
            print(f"Error processing {data_type}: {e}")
            return None
    else:
        print(f"Failed to fetch {data_type} data: {response.status_code}")
        return None

if __name__ == "__main__":
    for data_type in DATA_TYPES:
        fetch_eirgrid_data(data_type)

