import pandas as pd

#Code on removing time from date column and adding simplified label column as 2-positive, 1-neutral, 0-negative
# Load your dataset
file_path = "/Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/LabellingData/data/predictions.csv"
df = pd.read_csv(file_path)
print(df)

# Remove the time from the 'Date' column
df['Date'] = pd.to_datetime(df['Date']).dt.date

# Map the 'predicted_label' to 'simplified_label'
label_mapping = {2: 'positive', 1: 'neutral', 0: 'negative'}
df['simplified_label'] = df['predicted_label'].map(label_mapping)

# Save the updated dataframe to a new CSV
output_path = "/Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/LabellingData/data/time_dropped_simplifiedlabel_added.csv"
df.to_csv(output_path, index=False)

print("Dataset processed and saved to:", output_path)
print(df)
