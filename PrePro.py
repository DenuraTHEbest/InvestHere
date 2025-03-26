import pandas as pd
import os
from glob import glob
import numpy as np

# Define input and output directories
input_directory = r'C:\Users\nimsi\OneDrive\Desktop\Stock data'
output_directory = r"PreProcessed"

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Dictionary to store all processed data for each company
company_data = {}

# Fetch both .xls and .xlsx files
file_paths = glob(os.path.join(input_directory, '*.xls')) + glob(os.path.join(input_directory, '*.xlsx'))

def compute_rsi(series, window=14):
    """
    Compute the RSI (Relative Strength Index) for a given price series.
    RSI = 100 - [100 / (1 + (avg_gain / avg_loss))]
    """
    delta = series.diff()
    # Separate positive and negative moves
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)

    # Calculate rolling means
    ma_up = up.rolling(window=window, min_periods=window).mean()
    ma_down = down.rolling(window=window, min_periods=window).mean()

    # Avoid division by zero
    rsi = 100 - 100 / (1 + (ma_up / ma_down))
    return rsi

def compute_macd(series, short_window=12, long_window=26, signal_window=9):
    """
    Compute MACD (Moving Average Convergence/Divergence).
    Returns MACD line, Signal line, and Histogram.
    """
    ema_short = series.ewm(span=short_window, adjust=False).mean()
    ema_long = series.ewm(span=long_window, adjust=False).mean()
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist

def compute_bollinger_bands(series, window=20, num_std=2):
    """
    Compute Bollinger Bands using a simple moving average.
    Returns the middle band (SMA), upper band, and lower band.
    """
    sma = series.rolling(window=window, min_periods=window).mean()
    r_std = series.rolling(window=window, min_periods=window).std()
    upper_band = sma + (r_std * num_std)
    lower_band = sma - (r_std * num_std)
    return sma, upper_band, lower_band

def compute_atr(df, window=14):
    """
    Compute the ATR (Average True Range) for the given DataFrame.
    Requires 'PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', and 'CLOSE PRICE (Rs.)'.
    ATR = rolling mean of TR, where
      TR = max( High-Low, abs(High-PrevClose), abs(Low-PrevClose) ).
    """
    # Make sure we have previous close
    df['PrevClose'] = df['CLOSE PRICE (Rs.)'].shift(1)

    # Calculate True Range
    df['TR'] = df[['PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', 'PrevClose']].apply(
        lambda row: max(
            row['PRICE HIGH (Rs.)'] - row['PRICE LOW (Rs.)'],
            abs(row['PRICE HIGH (Rs.)'] - row['PrevClose']),
            abs(row['PRICE LOW (Rs.)'] - row['PrevClose'])
        ), axis=1
    )

    # ATR is rolling mean of True Range
    df['ATR'] = df['TR'].rolling(window=window, min_periods=window).mean()
    return df['ATR']

for file_path in file_paths:
    print(f"📂 Processing file: {file_path}")

    try:
        # Choose correct engine based on file type
        engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'

        # Read all sheets with header starting at row 4 (0-indexed header=3)
        sheets = pd.read_excel(file_path, sheet_name=None, header=3, engine=engine)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        continue

    for sheet_name, df in sheets.items():
        print(f"📑 Processing sheet: {sheet_name}")

        if df.empty:
            print(f"⚠️ Sheet {sheet_name} is empty. Skipping...")
            continue

        # Convert 'TRADING DATE' to datetime format
        if 'TRADING DATE' in df.columns:
            df['TRADING DATE'] = pd.to_datetime(df['TRADING DATE'], format='%d-%b-%y', errors='coerce')

            # Break 'TRADING DATE' into Date, Month, and Year columns
            df['Date'] = df['TRADING DATE'].dt.day
            df['Month'] = df['TRADING DATE'].dt.month
            df['Year'] = df['TRADING DATE'].dt.year
        else:
            print(f"⚠️ 'TRADING DATE' column not found in {sheet_name}. Skipping...")
            continue

        # Filter data for years 2019-2024
        df = df[(df['Year'] >= 2019) & (df['Year'] <= 2024)]

        if df.empty:
            print(f"⚠️ No data from 2019-2024 in {sheet_name}. Skipping...")
            continue

        # Convert numeric columns to appropriate types before dropping unwanted columns
        numeric_cols = ['PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', 'CLOSE PRICE (Rs.)',
                        'OPEN PRICE (Rs.)', 'TRADE VOLUME (No.)', 'SHARE VOLUME (No.)',
                        'TURNOVER (Rs.)']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Fill missing values using forward fill
        df[numeric_cols] = df[numeric_cols].ffill()

        # Process data for each company
        if 'SHORT NAME' in df.columns:
            for company in df['SHORT NAME'].unique():
                company_df = df[df['SHORT NAME'] == company].copy()

                # Sort by 'TRADING DATE'
                company_df = company_df.sort_values(by='TRADING DATE')

                # 1) Compute additional indicators BEFORE dropping any columns
                # RSI (using 14-day window on the 'CLOSE PRICE (Rs.)')
                company_df['RSI_14'] = compute_rsi(company_df['CLOSE PRICE (Rs.)'], window=14)

                # MACD (12, 26, 9) - returns three columns: MACD_Line, MACD_Signal, MACD_Hist
                macd_line, macd_signal, macd_hist = compute_macd(company_df['CLOSE PRICE (Rs.)'])
                company_df['MACD_Line'] = macd_line
                company_df['MACD_Signal'] = macd_signal
                company_df['MACD_Hist'] = macd_hist

                # Bollinger Bands (20-day, 2 std)
                bb_mid, bb_upper, bb_lower = compute_bollinger_bands(company_df['CLOSE PRICE (Rs.)'], window=20, num_std=2)
                company_df['BB_Mid'] = bb_mid
                company_df['BB_Upper'] = bb_upper
                company_df['BB_Lower'] = bb_lower

                # Volume Change (difference in TRADE VOLUME (No.))
                if 'TRADE VOLUME (No.)' in company_df.columns:
                    company_df['Volume_Change'] = company_df['TRADE VOLUME (No.)'].diff()

                # ATR (14-day)
                if all(x in company_df.columns for x in ['PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', 'CLOSE PRICE (Rs.)']):
                    company_df['ATR_14'] = compute_atr(company_df, window=14)
                else:
                    company_df['ATR_14'] = np.nan

                # 2) Create lagged close prices for the first 30 days
                for lag in range(1, 31):
                    company_df[f'CLOSE PRICE (Lag {lag})'] = company_df['CLOSE PRICE (Rs.)'].shift(lag)

                # 3) Compute moving averages based on the lag features:
                # MA_7: Average of Lag 1 to Lag 7
                # MA_14: Average of Lag 1 to Lag 14
                # MA_30: Average of Lag 1 to Lag 30
                company_df['MA_7'] = company_df[[f'CLOSE PRICE (Lag {i})' for i in range(1, 8)]].mean(axis=1)
                company_df['MA_14'] = company_df[[f'CLOSE PRICE (Lag {i})' for i in range(1, 15)]].mean(axis=1)
                company_df['MA_30'] = company_df[[f'CLOSE PRICE (Lag {i})' for i in range(1, 31)]].mean(axis=1)

                # 4) Drop rows with NaN values caused by shifting or rolling computations
                required_cols = [f'CLOSE PRICE (Lag {lag})' for lag in range(1, 31)] + [
                    'MA_7', 'MA_14', 'MA_30',
                    'RSI_14', 'MACD_Line', 'MACD_Signal', 'MACD_Hist',
                    'BB_Mid', 'BB_Upper', 'BB_Lower',
                    'ATR_14'
                ]
                if 'Volume_Change' in company_df.columns:
                    required_cols.append('Volume_Change')

                company_df = company_df.dropna(subset=required_cols)

                # 5) Remove unwanted columns
                columns_to_remove = [
                    'PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', 'CLOSE PRICE (Rs.)',
                    'TRADE VOLUME (No.)', 'SHARE VOLUME (No.)', 'TURNOVER (Rs.)',
                    'PrevClose', 'TR'
                ]
                cols_to_drop = [c for c in columns_to_remove if c in company_df.columns]
                company_df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

                # 6) Store data for each company, appending to existing data if necessary
                if company in company_data:
                    company_data[company] = pd.concat([company_data[company], company_df], ignore_index=True)
                else:
                    company_data[company] = company_df

# Save the processed data for each company to CSV files
for company, data in company_data.items():
    output_file = os.path.join(output_directory, f"{company}_data.csv")
    data.to_csv(output_file, index=False)
    print(f"✅ Saved processed data for {company} to {output_file}")

print("🎯 Data preprocessing completed successfully!")
