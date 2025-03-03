import pandas as pd
from database.init_mongo import news_collection

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
