from flask import Flask, request, jsonify, abort
from process_news import process_news_entry
from aggregate_sentiment import aggregate_sentiment
from database.init_mongo import predictions_collection, news_collection
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/process_news', methods=['POST'])
def process_news_endpoint():
    try:
        # Validate input
        if not request.json or "news" not in request.json:
            abort(400, description="Invalid input: 'news' field is required")

        news_list = request.json.get("news")
        if not isinstance(news_list, list):
            abort(400, description="Invalid input: 'news' must be a list")

        # Process each news entry
        results = [process_news_entry(news) for news in news_list]

        # Store results in MongoDB
        if results:
            news_collection.insert_many(results)

        return jsonify({"status": "success", "processed_entries": len(results)}), 200
    except Exception as e:
        logger.error(f"Error in /process_news: {str(e)}")
        abort(500, description="Internal server error")

@app.route('/get_predictions', methods=['GET'])
def get_predictions():
    try:
        # Aggregate sentiment scores
        sentiment_scores = aggregate_sentiment(period="daily").to_dict(orient="records")

        # Format predictions
        predictions = [
            {
                "date": entry["date"],
                "sentiment_score": entry["sentiment_score"],
                # "predicted_aspi_change": predict_aspi(entry["sentiment_score"], 0.1)  # Uncomment if needed
            }
            for entry in sentiment_scores
        ]

        # Store predictions in MongoDB
        if predictions:
            predictions_collection.insert_many(predictions)

        return jsonify({"status": "success", "predictions": predictions}), 200
    except Exception as e:
        logger.error(f"Error in /get_predictions: {str(e)}")
        abort(500, description="Internal server error")

if __name__ == '__main__':
    app.run(debug=True)