from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# Connect to MongoDB Atlas
uri = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["news_database"]
raw_collection = db["raw_news"]
business_collection = db["business_sentiment"]

# Load category model and tokenizer
#tokenizer_category = AutoTokenizer.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")
#model_category = AutoModelForSequenceClassification.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")
#category_labels = {0: "business news", 1: "international news", 2: "local news", 3: "sports news"}

# Load sentiment model and tokenizer
#tokenizer_sentiment = AutoTokenizer.from_pretrained("sinhala-nlp/Sentiment-sinbert-large")
#model_sentiment = AutoModelForSequenceClassification.from_pretrained("sinhala-nlp/Sentiment-sinbert-large")
#sentiment_labels = {0: "negative", 1: "neutral", 2: "positive"}
@app.route("/add_news", methods=["POST"])
def add_news():
    data = request.get_json()
    news_list = data.get("news", [])
    
    if not news_list:
        return jsonify({"error": "No news data provided"}), 400
    
    for news in news_list:
        news_item = {
            "title": news.get("title", ""),
            "date": news.get("date", datetime.datetime.utcnow().strftime('%Y-%m-%d')),
            "timestamp": datetime.datetime.utcnow()
        }
        raw_collection.insert_one(news_item)
    
    return jsonify({"message": "News added successfully"})

@app.route("/process_news", methods=["POST"])
def process_news():
    two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
    news_list = list(raw_collection.find({"timestamp": {"$gte": two_days_ago}}))
    
    if not news_list:
        return jsonify({"message": "No recent news to process"})
    
    for news in news_list:
        title = news["title"]
        inputs = tokenizer_category([title], return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model_category(**inputs)
        category = category_labels.get(torch.argmax(outputs.logits, dim=1).item(), "unknown")
        
        if category == "business news":
            inputs = tokenizer_sentiment([title], return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = model_sentiment(**inputs)
            sentiment = sentiment_labels.get(torch.argmax(outputs.logits, dim=1).item(), "neutral")
            
            business_item = {
                "title": title,
                "category": category,
                "sentiment": sentiment,
                "date": news["date"],
                "timestamp": news["timestamp"]
            }
            business_collection.insert_one(business_item)
    
    return jsonify({"message": "News processing completed"})

@app.route("/get_recent_business_news", methods=["GET"])
def get_recent_business_news():
    two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
    news_list = list(business_collection.find({"timestamp": {"$gte": two_days_ago}}, {"_id": 0}))
    return jsonify({"business_news": news_list})

if __name__ == "__main__":
    app.run(debug=True)
