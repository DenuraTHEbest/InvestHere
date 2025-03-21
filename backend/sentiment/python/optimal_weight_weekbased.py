import pandas as pd
from scipy.optimize import minimize
import numpy as np

# Load Sentiment Dataset
sentiment_file_path = 'news_data_with_simplified_label.csv'  # Update with your file path
sentiment_df = pd.read_csv(sentiment_file_path)

# Load ASPI Dataset (or stock price changes dataset)
stock_file_path = 'CSE_All-Share_Historical_Data_(2).csv'  # Update with your file path
stock_df = pd.read_csv(stock_file_path)

# Remove the '%' sign and convert to numeric
stock_df['Change %'] = stock_df['Change %'].str.replace('%', '').astype(float)

# Convert 'Date' columns to datetime
sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date'])
stock_df['Date'] = pd.to_datetime(stock_df['Date'])

# Filter ASPI data to match sentiment data date range
min_date = sentiment_df['Date'].min()
max_date = sentiment_df['Date'].max()
filtered_stock_df = stock_df[(stock_df['Date'] >= min_date) & (stock_df['Date'] <= max_date)].copy()

# Add 'Week' column (Monday as the start of the week)
filtered_stock_df['Week'] = filtered_stock_df['Date'].dt.to_period('W-MON')
sentiment_df['Week'] = sentiment_df['Date'].dt.to_period('W-MON')

# Merge sentiment data with stock price changes
merged_df = pd.merge(sentiment_df, filtered_stock_df, on=['Date'], how='inner')

# Re-add 'Week' column to merged_df if missing
if 'Week' not in merged_df.columns:
    merged_df['Week'] = merged_df['Date'].dt.to_period('W-MON')

# Define a function to compute weekly weighted sentiment scores
def compute_weekly_scores(df, weights):
    # Map weights to sentiment labels
    weight_map = {'positive': weights[0], 'neutral': weights[1], 'negative': weights[2]}
    df['Weighted_Sentiment'] = df['simplified_label'].map(weight_map)
    # Calculate weekly mean sentiment scores
    return df.groupby('Week')['Weighted_Sentiment'].mean()

# Define the loss function (e.g., negative correlation or MSE)
def loss_function(weights, df, target):
    weekly_scores = compute_weekly_scores(df, weights)
    # Align weekly scores and target
    aligned_scores = weekly_scores.reindex(target.index, fill_value=0)
    correlation = np.corrcoef(aligned_scores, target)[0, 1]  # Pearson correlation
    return -correlation  # Minimize negative correlation

# Prepare the target variable (weekly stock price changes)
weekly_aspi_changes = filtered_stock_df.groupby('Week')['Change %'].mean()

# Initial weights for optimization
initial_weights = [1, 0, -1]

# Optimize weights
result = minimize(
    loss_function,
    initial_weights,
    args=(merged_df, weekly_aspi_changes),
    bounds=[(-2, 2), (-1, 1), (-2, 0)]  # Bounds for each sentiment weight
)

# Retrieve optimal weights
optimal_weights = result.x
print("Optimal Weights:", optimal_weights)

# Apply optimal weights to compute final weekly sentiment scores
final_weekly_scores = compute_weekly_scores(merged_df, optimal_weights)

# Save the final weekly scores to a CSV file (optional)
output_file = 'weekly_weighted_scores.csv'
final_weekly_scores.to_csv(output_file, header=True)
print(f"Final weekly scores saved to {output_file}.")
