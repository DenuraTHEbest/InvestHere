from flask import Flask, request, jsonify
import datetime
from db_connection import get_database
from pipeline import process_news

app = Flask(__name__)
db = get_database()
raw_collection = db["raw_news"]
business_collection = db["business_sentiment"]

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
def process_news_api():
    process_news()
    return jsonify({"message": "News processing completed"})

@app.route("/get_recent_business_news", methods=["GET"])
def get_recent_business_news():
    two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
    news_list = list(business_collection.find({"timestamp": {"$gte": two_days_ago}}, {"_id": 0}))
    return jsonify({"business_news": news_list})

if __name__ == "__main__":
    app.run(debug=True)
