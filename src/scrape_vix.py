import yfinance as yf
import pandas as pd
from pathlib import Path

def get_vix_data():
    # 1. Setup paths (Identical to previous script)
    current_dir = Path(__file__).resolve().parent
    output_dir = current_dir.parent / "data" / "controls"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "vix_daily.csv"

    # 2. Define the ticker for CBOE Volatility Index
    ticker = "^VIX"
    
    print(f"Fetching data for: {ticker}...")

    # 3. Download data
    df = yf.download(ticker, start="2015-01-01", interval="1d", auto_adjust=False)

    # 4. Robust Column Selection
    # VIX is an index, so 'Close' and 'Adj Close' are usually identical.
    if 'Adj Close' in df.columns:
        data = df[['Adj Close']]
    else:
        data = df[['Close']]

    # Forward-fill any missing holiday gaps
    data = data.ffill()

    # 5. Rename for clarity
    data.columns = ['VIX']

    # 6. Save to CSV
    data.to_csv(file_path)
    
    print(f"Download complete! VIX data saved to: {file_path}")
    return data

if __name__ == "__main__":
    try:
        get_vix_data()
    except Exception as e:
        print(f"An error occurred pulling VIX data: {e}")