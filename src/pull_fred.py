import os
import pandas as pd
from pathlib import Path
from fredapi import Fred
from dotenv import load_dotenv

def get_data():
    # 1. Setup paths and Load Environment Variables
    # Find the root directory (one level up from /src)
    script_path = Path(__file__).resolve()
    root_dir = script_path.parents[1]
    
    # Load .env from the root directory
    load_dotenv(root_dir / ".env")
    
    # Access the API key
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("Error: FRED_API_KEY not found. Check your .env file in the root folder.")
        return

    # Define the output directory
    output_dir = root_dir / "data" / "controls"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Initialize FRED
    fred = Fred(api_key=api_key)
    
    # Series to pull: {Ticker: Friendly Name}
    series_map = {
        'CPIAUCSL': 'US_CPI',
        'UNRATE': 'US_Unemployment',
        'CP0000EZ19M086NEST': 'EZ_HICP',
        'LRHUTTTTEZM156S': 'EZ_Unemployment',
        'GBRCPIALLMINMEI': 'UK_CPI',
        'LRHUTTTTGBM156S': 'UK_Unemployment'
    }

    print(f"Starting data pull for {len(series_map)} series...")

    # 3. Processing Loop
    for ticker, name in series_map.items():
        try:
            print(f"Fetching vintage history for {name} ({ticker})...")
            
            # Pull all release versions
            df_all = fred.get_series_all_releases(ticker)
            
            # Clean dates
            df_all['date'] = pd.to_datetime(df_all['date'])
            df_all['realtime_start'] = pd.to_datetime(df_all['realtime_start'])
            
            # Filter for 2015 onwards
            df_all = df_all[df_all['date'] >= '2015-01-01']

            # Identify Initial vs. Current releases
            # groupby('date').first() captures the very first time a month's data was seen
            # groupby('date').last() captures the most recent revision
            initial = df_all.groupby('date').first().reset_index()
            revised = df_all.groupby('date').last().reset_index()

            # Merge into a clean summary
            summary = pd.DataFrame({
                'Observation_Month': initial['date'],
                'Initial_Value': initial['value'],
                'Initial_Release_Date': initial['realtime_start'],
                'Current_Value': revised['value'],
                'Latest_Revision_Date': revised['realtime_start']
            })

            # 4. Save to CSV
            file_name = f"{name.lower()}_vintages.csv"
            summary.to_csv(output_dir / file_name, index=False)
            print(f" Successfully saved: {file_name}")

        except Exception as e:
            print(f" Warning: Could not process {name}. Detailed error: {e}")

if __name__ == "__main__":
    get_data()