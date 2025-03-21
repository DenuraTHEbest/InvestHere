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

# Debug: Display the cleaned data
print(stock_df[['Date', 'Change %']].head())

# Ensure both datasets have 'Date' in datetime format
sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date'])
stock_df['Date'] = pd.to_datetime(stock_df['Date'])

# Filter ASPI data to match sentiment data date range
min_date = sentiment_df['Date'].min()
max_date = sentiment_df['Date'].max()
filtered_stock_df = stock_df[(stock_df['Date'] >= min_date) & (stock_df['Date'] <= max_date)]

# Merge sentiment data with stock price changes
merged_df = pd.merge(sentiment_df, filtered_stock_df, on='Date', how='inner')

# Check merged data
print("Merged Data Preview:")
print(merged_df.head())

# Define a function to compute daily weighted sentiment scores
def compute_daily_scores(df, weights):
    # Map weights to sentiment labels
    weight_map = {'positive': weights[0], 'neutral': weights[1], 'negative': weights[2]}
    df['Weighted_Sentiment'] = df['simplified_label'].map(weight_map)
    # Calculate daily mean sentiment scores
    return df.groupby('Date')['Weighted_Sentiment'].mean()

# Define a loss function (e.g., negative correlation or MSE)
def loss_function(weights, df, target):
    daily_scores = compute_daily_scores(df, weights)
    # Align the scores and target
    aligned_scores = daily_scores.reindex(target.index, fill_value=0)
    correlation = np.corrcoef(aligned_scores, target)[0, 1]  # Pearson correlation
    return -correlation  # Minimize negative correlation

# Prepare the target variable (daily stock price changes)
target = merged_df.set_index('Date')['Change %']  # Replace 'Stock Price Change' with the actual column name

# Initial weights for optimization
initial_weights = [1, 0, -1]

# Optimize weights
result = minimize(
    loss_function,
    initial_weights,
    args=(merged_df, target),
    bounds=[(-2, 2), (-1, 1), (-2, 0)]  # Bounds for each sentiment weight
)

# Retrieve optimal weights
optimal_weights = result.x
print("Optimal Weights:", optimal_weights)

# Apply optimal weights to compute final daily sentiment scores
final_daily_scores = compute_daily_scores(merged_df, optimal_weights)

# Save the final daily scores to a CSV file (optional)
output_file = 'daily_weighted_scores.csv'
final_daily_scores.to_csv(output_file, header=True)
print(f"Final daily scores saved to {output_file}.")
