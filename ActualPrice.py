import pandas as pd
import os

# Specify the directory containing the 300 files
input_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\stock_predictions6"
output_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\ActualPrices"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Loop through all Excel files in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.xlsx'):  # Make sure we are processing only Excel files
        file_path = os.path.join(input_directory, filename)

        # Load the Excel file
        try:
            df = pd.read_excel(file_path)

            # Extract the relevant columns (Year, Month, Day, Actual Day 1 to Actual Day 20)
            columns_to_extract = ['Year', 'Month', 'Day'] + [f'Actual Day {i}' for i in range(1, 21)]
            extracted_df = df[columns_to_extract]

            # If there is a company name in a column, you can add it like this (assuming it's in 'Company Name' column):
            # extracted_df['Company Name'] = df['Company Name']

            # Save the extracted data to a new file in the output directory
            output_file_path = os.path.join(output_directory, f'extracted_{filename}')
            extracted_df.to_excel(output_file_path, index=False)

            print(f"Extracted data from {filename} saved to {output_file_path}")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")


