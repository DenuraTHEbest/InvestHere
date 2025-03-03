from load_models import category_model, category_tokenizer, sentiment_model, sentiment_tokenizer
from database.init_mongo import news_collection
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY_LABELS = {0: "business news", 1: "international news", 2: "local news", 3: "sports news"}
SENTIMENT_LABELS = {2: 'positive', 1: 'neutral', 0: 'negative'}

def classify_news(text):
    try:
        inputs = category_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = category_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        return CATEGORY_LABELS[prediction]
    except Exception as e:
        logger.error(f"Error in classify_news: {str(e)}")
        raise

'''def analyze_sentiment(text):
    try:
        inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = sentiment_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        return SENTIMENT_LABELS[prediction]
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {str(e)}")
        raise'''

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


def process_news_entry(news_entry):
    try:
        # Validate input
        if not isinstance(news_entry, dict) or "date" not in news_entry or "news" not in news_entry:
            raise ValueError("Invalid news_entry format: must contain 'date' and 'news' keys")

        date = news_entry["date"]
        text = news_entry["news"]

        # Step 1: Classify news category
        category = classify_news(text)
        
        # Ignore if not business news
        if category != "business news":
            logger.info(f"Ignored non-business news: {text}")
            return {"date": date, "category": category, "ignored": True}

        # Step 2: Perform sentiment analysis
        sentiment = analyze_sentiment(text)

        # Step 3: Store in MongoDB
        news_collection.insert_one({
            "date": date,
            "news": text,
            "category": category,
            "sentiment": sentiment
        })

        logger.info(f"Processed news entry: {text}")
        return {"date": date, "category": category, "sentiment": sentiment}
    except Exception as e:
        logger.error(f"Error in process_news_entry: {str(e)}")
        raise