import pandas as pd
import os

# Specify the directory containing the .xlsx files
input_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\preprocessed4\big_one.csv"
output_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\preprocessed4\big_one.csv"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Loop through all .xlsx files in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.xlsx'):  # Process only Excel files
        file_path = os.path.join(input_directory, filename)

        try:
            # Load the Excel file
            df = pd.read_excel(file_path)

            # Define the output CSV file path
            output_file_path = os.path.join(output_directory, f'{os.path.splitext(filename)[0]}.csv')

            # Save the dataframe as a CSV file
            df.to_csv(output_file_path, index=False)

            print(f"Converted {filename} to CSV and saved to {output_file_path}")

        except Exception as e:
            print(f"Failed to convert {filename}: {e}")
