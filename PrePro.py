import pandas as pd
import os
from glob import glob

# Define input and output directories
input_directory = r'C:\Users\nimsi\OneDrive\Desktop\Stock data'
output_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\preprocessed4"

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Dictionary to store all processed data for each company
company_data = {}

# Fetch both .xls and .xlsx files
file_paths = glob(os.path.join(input_directory, '*.xls')) + glob(os.path.join(input_directory, '*.xlsx'))

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

                # Lagged close prices (1 to 10 days) using the 'CLOSE PRICE (Rs.)'
                for lag in range(1, 11):  # Create lagged features for the first 10 days
                    company_df[f'CLOSE PRICE (Lag {lag})'] = company_df['CLOSE PRICE (Rs.)'].shift(lag)

                # Moving Averages (7-day, 14-day, 30-day)
                company_df['MA_7'] = company_df['CLOSE PRICE (Rs.)'].rolling(window=7, min_periods=1).mean()
                company_df['MA_14'] = company_df['CLOSE PRICE (Rs.)'].rolling(window=14, min_periods=1).mean()
                company_df['MA_30'] = company_df['CLOSE PRICE (Rs.)'].rolling(window=30, min_periods=1).mean()

                # Drop rows with NaN values caused by shifting or moving averages
                company_df = company_df.dropna(
                    subset=[f'CLOSE PRICE (Lag {lag})' for lag in range(1, 11)] + ['MA_7', 'MA_14', 'MA_30']
                )

                # Remove unwanted columns
                columns_to_remove = ['PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', 'CLOSE PRICE (Rs.)',
                                     'TRADE VOLUME (No.)', 'SHARE VOLUME (No.)', 'TURNOVER (Rs.)']
                company_df.drop(columns=[col for col in columns_to_remove if col in company_df.columns], inplace=True)

                # Store data for each company, appending to existing data if necessary
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
