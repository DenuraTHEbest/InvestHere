from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Load Model & Tokenizer
MODEL_PATH = "/sentiment/models/sentiment_model"  # Adjust if needed
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model.eval()  # Set to evaluation mode
l = AutoModelForSequenceClassification.from_pretrained("sinhala-nlp/Sentiment-sinbert-large")

sentiment_labels = {0: "negative", 1: "neutral", 2: "positive"}

def analyze_sentiment(title):
    inputs = tokenizer([title], return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    sentiment = sentiment_labels.get(torch.argmax(outputs.logits, dim=1).item(), "neutral")
    return sentiment
