import pandas as pd
from scipy.optimize import minimize
import numpy as np
from database.init_mongo import news_collection, aspi_collection, daily_scores_collection, weekly_scores_collection
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def aggregate_sentiment(period="daily"):
    news_data = list(news_collection.find({}, {"_id": 0, "date": 1, "sentiment": 1}))
    df = pd.DataFrame(news_data)
    df["date"] = pd.to_datetime(df["date"])

    sentiment_mapping = {"Negative": -1, "Neutral": 0, "Positive": 1}
    df["sentiment_score"] = df["sentiment"].map(sentiment_mapping)

    if period == "daily":
        grouped_df = df.groupby(df["date"].dt.date)["sentiment_score"].mean().reset_index()
    elif period == "weekly":
        grouped_df = df.groupby(df["date"].dt.to_period("W"))["sentiment_score"].mean().reset_index()
    
    return grouped_df

def compute_and_store_scores(processed_entries):
    try:
        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(processed_entries)
        
        # Validate DataFrame
        if 'date' not in df.columns or 'sentiment' not in df.columns:
            raise ValueError("Processed entries must contain 'date' and 'sentiment' fields")
        
        # Convert 'date' to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Ensure sentiment labels are valid
        valid_sentiments = {'positive', 'neutral', 'negative'}
        df = df[df['sentiment'].isin(valid_sentiments)]  # Filter out invalid sentiments

        if df.empty:
            logger.warning("No valid sentiment data to process")
            return

        # ✅ Step 1: Daily Sentiment Counts
        daily_counts = df.groupby('date')['sentiment'].value_counts().unstack(fill_value=0)
        
        # Ensure all sentiment columns exist
        for sentiment in valid_sentiments:
            if sentiment not in daily_counts.columns:
                daily_counts[sentiment] = 0  # Add missing column with default value 0

        daily_counts['total'] = daily_counts.sum(axis=1)

        # ✅ Step 2: Optimize Weights (only if there is sufficient data)
        if len(daily_counts) > 1:  # Ensure there are multiple days of data
            def compute_daily_scores(weights):
                weight_map = {'positive': weights[0], 'neutral': weights[1], 'negative': weights[2]}
                weighted_scores = df['sentiment'].map(weight_map)
                return weighted_scores.groupby(df['date']).sum()

            def loss_function(weights):
                daily_scores = compute_daily_scores(weights)
                return -daily_scores.mean()  # Minimize the negative of the mean score

            initial_weights = [1, 0, -1]  # Positive: 1, Neutral: 0, Negative: -1
            result = minimize(loss_function, initial_weights, bounds=[(0, 2), (-1, 1), (-2, 0)])
            optimal_weights = result.x
        else:
            logger.warning("Insufficient data for optimization. Using default weights.")
            optimal_weights = [1, 0, -1]  # Default weights

        # ✅ Step 3: Compute Weighted Scores
        weight_map = {'positive': optimal_weights[0], 'neutral': optimal_weights[1], 'negative': optimal_weights[2]}
        daily_counts['Weighted_Score'] = df['sentiment'].map(weight_map).groupby(df['date']).mean()

        # ✅ Step 4: Save to Database (Daily)
        for date, row in daily_counts.iterrows():
            daily_scores_collection.update_one(
                {'date': date},
                {'$set': {
                    'date': date,
                    'positive': int(row['positive']),
                    'neutral': int(row['neutral']),
                    'negative': int(row['negative']),
                    'total': int(row['total']),
                    'weighted_score': float(row['Weighted_Score'])
                }},
                upsert=True
            )

        # ✅ Step 5: Compute Weekly Scores
        weekly_scores = daily_counts['Weighted_Score'].resample('W-MON').mean()

        # ✅ Step 6: Save to Database (Weekly)
        for date, score in weekly_scores.items():
            start_of_week = date - timedelta(days=6)
            weekly_scores_collection.update_one(
                {'week': f"{start_of_week.date()}/{date.date()}"},
                {'$set': {
                    'week': f"{start_of_week.date()}/{date.date()}",
                    'weighted_score': float(score),
                    'positive': int(daily_counts.loc[start_of_week:date, 'positive'].sum()),
                    'neutral': int(daily_counts.loc[start_of_week:date, 'neutral'].sum()),
                    'negative': int(daily_counts.loc[start_of_week:date, 'negative'].sum())
                }},
                upsert=True
            )

        logger.info("✅ Sentiment scores stored successfully!")

    except Exception as e:
        logger.error(f"Error in compute_and_store_scores: {str(e)}")
        raise