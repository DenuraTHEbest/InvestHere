import pandas as pd

# Load your dataset
file_path = 'news_data_with_simplified_label.csv'
df = pd.read_csv(file_path)

# Ensure the 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Group by date and count occurrences of each label
daily_counts = df.groupby(['Date', 'predicted_label']).size().unstack(fill_value=0)

# Ensure all columns (0, 1, 2) exist, even if missing in the data
for col in [0, 1, 2]:
    if col not in daily_counts:
        daily_counts[col] = 0  # Add missing column with default 0

# Calculate total counts per day
daily_counts['Total'] = daily_counts.sum(axis=1)

# Handle cases where Total is 0 (avoid division by zero)
weights = {0: -1, 1: 0, 2: 1}
daily_counts['Weighted_Score'] = daily_counts.apply(
    lambda row: (row[0] * weights[0] + row[1] * weights[1] + row[2] * weights[2]) / row['Total']
    if row['Total'] > 0 else 0, axis=1
)

# Reset the index to move the Date from the index to a column
daily_counts.reset_index(inplace=True)
daily_counts.rename(columns={'index': 'Date'}, inplace=True)  # Rename the new 'index' column to 'Date'

# Save to a new CSV file
output_file = 'daily_weighted_score.csv'
daily_counts.to_csv(output_file, index=False)

# Display the result
print(daily_counts)
