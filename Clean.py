import os
import glob
import pandas as pd

def clean_files_and_save(input_folder, output_folder):
    # Columns you want to remove
    columns_to_remove = [
        "PRICE HIGH (Rs.)",
        "PRICE LOW (Rs.)",
        "CLOSE PRICE (Rs.)",
        "TRADE VOLUME (No.)",
        "SHARE VOLUME (No.)",
        "TURNOVER (Rs.)",
        "MAIN TYPE",
        "Unnamed: 12",
        "Unnamed: 13",
        "Unnamed: 14",
        "Unnamed: 15"
    ]

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get all .xlsx files in the input folder
    excel_files = glob.glob(os.path.join(input_folder, "*.xlsx"))

    for file_path in excel_files:
        # Read file into pandas DataFrame
        df = pd.read_excel(file_path)

        # Drop the columns you don't need (ignore errors if columns not present)
        df.drop(columns=columns_to_remove, axis=1, inplace=True, errors='ignore')

        # Prepare the output file name
        # Example: "ACL_data.xlsx" -> "ACL_data_Real.xlsx"
        base_name = os.path.basename(file_path)  # "ACL_data.xlsx"
        file_name_without_ext, _ = os.path.splitext(base_name)  # "ACL_data"
        new_file_name = f"{file_name_without_ext}_featured.xlsx"   # "ACL_data_Real.xlsx"
        output_path = os.path.join(output_folder, new_file_name)

        # Save to the output directory
        df.to_excel(output_path, index=False)
        print(f"Saved cleaned file to: {output_path}")


if __name__ == "__main__":
    # Set your actual input and output folders here
    input_folder = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\preprocessed2"
    output_folder = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\realPreprocess"

    clean_files_and_save(input_folder, output_folder)
