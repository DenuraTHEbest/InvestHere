from load_models import category_model, category_tokenizer, sentiment_model, sentiment_tokenizer
from database.init_mongo import news_collection, daily_scores_collection, weekly_scores_collection, aspi_collection
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime, timedelta
import logging
import pandas as pd
from scipy.optimize import minimize
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY_LABELS = {0: "business news", 1: "international news", 2: "local news", 3: "sports news"}
SENTIMENT_LABELS = {2: 'positive', 1: 'neutral', 0: 'negative'}

def classify_news(text):
    try:
        inputs = category_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = category_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        return CATEGORY_LABELS[prediction]
    except Exception as e:
        logger.error(f"Error in classify_news: {str(e)}")
        raise


def analyze_sentiment(text):
    try:
        inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        #inputs = {key: val.to(device) for key, val in inputs.items()}  # Move input tensors to device
        
        with torch.no_grad():
            outputs = sentiment_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        return SENTIMENT_LABELS.get(prediction, "unknown")
    except Exception as e:
        print(f"Error in analyze_sentiment: {str(e)}")
        return None

def process_batch(news_entries):
    processed_entries = []
    for entry in news_entries:
        result = process_news_entry(entry)
        if result and not result.get('ignored'):
            processed_entries.append(result)
    return processed_entries

def compute_and_store_scores(processed_entries):
    try:
        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(processed_entries)
        df['date'] = pd.to_datetime(df['date'])

        # ✅ Step 1: Daily Sentiment Counts
        daily_counts = df.groupby('date')['sentiment'].value_counts().unstack(fill_value=0)
        daily_counts = daily_counts.rename(columns={'positive': 'positive', 'neutral': 'neutral', 'negative': 'negative'})
        daily_counts['total'] = daily_counts.sum(axis=1)

        # ✅ Step 2: Optimize Weights
        def compute_daily_scores(weights):
            weight_map = {'positive': weights[0], 'neutral': weights[1], 'negative': weights[2]}
            weighted_scores = df['sentiment'].map(weight_map)
            return weighted_scores.groupby(df['date']).mean()

        def loss_function(weights):
            daily_scores = compute_daily_scores(weights)
            aligned_scores = daily_scores.reindex(daily_counts.index, fill_value=0)
            correlation = np.corrcoef(aligned_scores, np.random.rand(len(aligned_scores)))[0, 1]
            return -correlation

        initial_weights = [1, 0, -1]
        result = minimize(loss_function, initial_weights, bounds=[(-2, 2), (-1, 1), (-2, 0)])
        optimal_weights = result.x

        # ✅ Step 3: Compute Weighted Scores
        weight_map = {'positive': optimal_weights[0], 'neutral': optimal_weights[1], 'negative': optimal_weights[2]}
        daily_counts['Weighted_Score'] = df['sentiment'].map(weight_map).groupby(df['date']).mean()

        # ✅ Step 4: Save to Database (Daily)
        for date, row in daily_counts.iterrows():
            daily_scores_collection.update_one(
                {'date': date},
                {'$set': {
                    'date': date,
                    'positive': row['positive'],
                    'neutral': row['neutral'],
                    'negative': row['negative'],
                    'total': row['total'],
                    'weighted_score': row['Weighted_Score']
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
                    'weighted_score': score,
                    'positive': daily_counts.loc[start_of_week:date, 'positive'].sum(),
                    'neutral': daily_counts.loc[start_of_week:date, 'neutral'].sum(),
                    'negative': daily_counts.loc[start_of_week:date, 'negative'].sum()
                }},
                upsert=True
            )

        logger.info("✅ Sentiment scores stored successfully!")

    except Exception as e:
        logger.error(f"Error in compute_and_store_scores: {str(e)}")


def process_news_entry(news_entry):
    try:
        # Validate input
        if not isinstance(news_entry, dict) or "date" not in news_entry or "news" not in news_entry:
            raise ValueError("Invalid news_entry format: must contain 'date' and 'news' keys")

        date = news_entry["date"]
        text = news_entry["news"]

        if not text.strip():
            logger.warning(f"Skipping empty news text for date: {date}")
            return None

        # Step 1: Classify news category
        category = classify_news(text)
        
        # Ignore if not business news
        if category != "business news":
            logger.info(f"Ignored non-business news on {date}: {text[:50]}...")
            return {"date": date, "category": category, "ignored": True}

        # Step 2: Perform sentiment analysis
        sentiment = analyze_sentiment(text)

        # Return processed data
        return {
            "date": date,
            "news": text,
            "category": category,
            "sentiment": sentiment
        }

    except Exception as e:
        logger.error(f"Error in process_news_entry: {str(e)}")
        return None
