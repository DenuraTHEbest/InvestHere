from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import joblib

# Load News Categorization Model
category_tokenizer = AutoTokenizer.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")
category_model = AutoModelForSequenceClassification.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")

# Load Sentiment Analysis Model
SENTIMENT_MODEL_PATH = "/Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/InvestHERE/Untitled/sentiment/models/sentiment_model"
sentiment_model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL_PATH)
sentiment_tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL_PATH)

print("✅ Models loaded successfully!")
