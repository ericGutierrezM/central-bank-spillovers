import yfinance as yf
import pandas as pd
from pathlib import Path

def get_index_data():
    # 1. Setup paths
    current_dir = Path(__file__).resolve().parent
    output_dir = current_dir.parent / "data" / "controls"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "global_indices_daily.csv"

    # 2. Define the tickers
    # S&P 500, Euro Stoxx 50, FTSE 100
    tickers = ["^GSPC", "^STOXX50E", "^FTSE"]
    
    print(f"Fetching data for: {', '.join(tickers)}...")

    # 3. Download data 
    # We set auto_adjust=False to try and force 'Adj Close' to appear
    df = yf.download(tickers, start="2015-01-01", interval="1d", auto_adjust=False)

    # 4. Robust Column Selection
    # If 'Adj Close' is missing, we use 'Close'
    if 'Adj Close' in df.columns:
        data = df['Adj Close']
    else:
        print("Note: 'Adj Close' not found, using 'Close' prices instead.")
        data = df['Close']

    # Forward-fill missing values (for mismatched market holidays)
    data = data.ffill()

    # 5. Rename columns for clarity 
    # We use a dictionary map to ensure the right name goes to the right ticker
    name_map = {
        "^GSPC": "S&P 500",
        "^STOXX50E": "Euro Stoxx 50",
        "^FTSE": "FTSE 100"
    }
    data = data.rename(columns=name_map)

    # 6. Save to CSV
    data.to_csv(file_path)
    
    print(f"Download complete! File saved to: {file_path}")
    return data

if __name__ == "__main__":
    try:
        get_index_data()
    except Exception as e:
        print(f"An error occurred: {e}")