import requests
import pandas as pd

EIRGRID_DATA_URL = "https://www.eirgrid.ie/smartgrid/data_endpoint.json"

def fetch_eirgrid_data():
    """Fetches balancing market data from EirGrid's dashboard."""
    try:
        response = requests.get(EIRGRID_DATA_URL)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            print(f"Error fetching data: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    df = fetch_eirgrid_data()
    if df is not None:
        df.to_csv("ml_models/data/raw/eirgrid_data.csv", index=False)
        print("Data saved successfully!")
