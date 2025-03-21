import pandas as pd

# Load your dataset

file_path = 'news_data_with_simplified_label.csv'  # Replace with the path to your dataset
df = pd.read_csv(file_path)

# Ensure the 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Group by 'Date' and calculate daily sentiment score
daily_sentiment_score = df.groupby(df['Date'].dt.date)['predicted_label'].mean().reset_index()

# Rename columns for clarity
daily_sentiment_score.columns = ['Date', 'Daily_Sentiment_Score']

# Define a function to classify the sentiment score
def classify_sentiment(score):
    if score < 1:
        return 'Negative'
    elif 1 <= score < 1.5:
        return 'Neutral'
    else:
        return 'Positive'

# Apply classification
daily_sentiment_score['Sentiment_Classification'] = daily_sentiment_score['Daily_Sentiment_Score'].apply(classify_sentiment)

# Save to a new CSV file (optional)
output_file = 'daily_sentiment_scores_with_classification.csv'
daily_sentiment_score.to_csv(output_file, index=False)

# Display the result
print(daily_sentiment_score)
