import pandas as pd
import os
from glob import glob

input_directory = r'C:\Users\nimsi\OneDrive\Desktop\Stock data'  
output_directory = r'C:\Users\nimsi\OneDrive\Documents\DSGP_Datasets'  

company_data = {}

file_paths = glob(os.path.join(input_directory, '*.xls')) + glob(os.path.join(input_directory, '*.xlsx'))  

for file_path in file_paths:

    print(f"Processing file: {file_path}")

    sheets = pd.read_excel(file_path, sheet_name=None, header=3)

    for sheet_name, df in sheets.items():
        print(f"Processing sheet: {sheet_name}")
        
        if df.empty:
            continue  

        if 'TRADING DATE' in df.columns:
            df['TRADING DATE'] = pd.to_datetime(df['TRADING DATE'], format='%d-%b-%y', errors='coerce')

        
        numeric_cols = ['PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', 'CLOSE PRICE (Rs.)', 
                        'OPEN PRICE (Rs.)', 'TRADE VOLUME (No.)', 'SHARE VOLUME (No.)', 
                        'TURNOVER (Rs.)']  
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'SHORT NAME' in df.columns:
            for company in df['SHORT NAME'].unique():
                company_df = df[df['SHORT NAME'] == company]
                
                if company in company_data:
                    company_data[company] = pd.concat([company_data[company], company_df])
                else:
            
                    company_data[company] = company_df

for company, data in company_data.items():
    output_file = os.path.join(output_directory, f"{company}_data.xlsx")
    data.to_excel(output_file, index=False)

print("Data preprocessing, combining, and saving completed.")
