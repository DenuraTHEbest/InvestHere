import os
import pandas as pd
from glob import glob

# Paths
input_directory = r"PreProcessed"
output_directory = r"BigPreprocess"
os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

# Pattern to match all CSV files in the input directory
file_paths = glob(os.path.join(input_directory, '*.csv'))

# List to collect DataFrames from each file
dataframes = []

for file_path in file_paths:
    try:
        df = pd.read_csv(file_path)
        dataframes.append(df)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        continue

# Concatenate all DataFrames into one
big_df = pd.concat(dataframes, ignore_index=True)

# Save the concatenated DataFrame to a single CSV file
big_file_path = os.path.join(output_directory, "big_one.csv")
big_df.to_csv(big_file_path, index=False)

print(f"✅ Successfully combined {len(dataframes)} files into '{big_file_path}'.")
