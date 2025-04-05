from flask import Flask, request, jsonify, abort
from process_news import process_news_entry  # Import the function to process individual entries
from aggregate_sentiment import compute_and_store_scores  # Import the function to compute scores
from database.init_mongo import news_collection, daily_scores_collection, weekly_scores_collection, test_collection # Import MongoDB collection
import logging
import pandas as pd
from flask_cors import CORS
from pymongo import DESCENDING
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app) 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/process_news', methods=['POST'])
def process_news_endpoint():
    try:
        logger.info("Received request at /process_news")

        if 'file1' not in request.files:
            abort(400, description="Invalid input: 'file1' field is required")

        file1 = request.files['file1']
        if file1.filename == '':
            abort(400, description="Invalid input: No file selected for 'file1'")

        logger.info(f"File received: {file1.filename}")

        df = pd.read_csv(file1)
        logger.info(f"CSV file read successfully. Shape: {df.shape}")

        if df.empty:
            logger.warning("Uploaded CSV file is empty")
            return jsonify({"status": "warning", "message": "Empty CSV file"}), 200
        
        # Process data in batches
        processed_entries = []
        for _, row in df.iterrows():
            result = process_news_entry(row.to_dict())
            if result and not result.get("ignored"):
                processed_entries.append(result)

        # Insert into MongoDB at once (batch insert)
        if processed_entries:
            news_collection.insert_many(processed_entries)
            logger.info(f"Inserted {len(processed_entries)} entries into MongoDB")

            # Compute and store sentiment scores
            compute_and_store_scores(processed_entries)
            logger.info("Computed and stored sentiment scores successfully")

        # ✅ Consistent success response
        return jsonify({
            "status": "success",
            "message": "File processed successfully",
            "processed_entries": len(processed_entries)
        }), 200

    except Exception as e:
        logger.error(f"Error in /process_news: {str(e)}", exc_info=True)
        # ✅ Consistent error response
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/api/sentiment.ts', methods=['GET'])
def get_sentiment_data():
    try:
        logger.info("Fetching sentiment data from MongoDB")

        # Fetch data from MongoDB
        # Get last 30 days' data
        daily = list(daily_scores_collection.find().sort('date', -1).limit(30))
        for item in daily:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string  # Replace with your query

        # Group by week
        weekly = list(weekly_scores_collection.aggregate([
            {
                '$group': {
                    '_id': { '$week': "$date" },
                    'positive': { '$sum': "$positive" },
                    'negative': { '$sum': "$negative" },
                    'neutral': { '$sum': "$neutral" },
                    'total': { '$sum': "$total" },
                    'weighted_score': { '$avg': "$weighted_score" }
                }
            },
            { '$sort': { '_id': -1 } },
            { '$limit': 10 }
        ]))

        return jsonify({
            'daily': daily,
            'weekly': weekly
        })

        # Transform the data if needed
        response = {
            "daily": daily_data,
            "weekly": weekly_data,
        }

        logger.info("Sentiment data fetched successfully")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error fetching sentiment data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    
# Endpoint to get daily sentiment data
@app.route('/get-daily-sentiment', methods=['GET'])
def get_daily_sentiment():
    # Find the latest available date in the database
    latest_doc = daily_scores_collection.find_one(
        {}, 
        sort=[('date', DESCENDING)]
    )

    if latest_doc:
        latest_date = latest_doc['date']
        start_of_period = latest_date - timedelta(days=20)  # Last 20 days
        start_of_period = start_of_period.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = latest_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        data = daily_scores_collection.find({
            'date': {'$gte': start_of_period, '$lte': end_of_day}
        })

        result = []
        for doc in data:
            result.append({
                'date': doc['date'].strftime('%Y-%m-%d'),
                'positive': doc['positive'],
                'neutral': doc['neutral'],
                'negative': doc['negative'],
                'weighted_score': doc['weighted_score']
            })

        return jsonify(result)
    
    return jsonify([])  # Return empty list if no data is found

# Endpoint to get weekly sentiment data
@app.route('/get-weekly-sentiment', methods=['GET'])
def get_weekly_sentiment():
    try:
        # Find the latest available week in the database
        latest_doc = weekly_scores_collection.find_one(
            {}, 
            sort=[('week', DESCENDING)]
        )

        if not latest_doc:
            return jsonify([])

        # Get the latest week's start date (first part of the week range)
        latest_week_start_str = latest_doc['week'].split('/')[0]
        latest_week_start = datetime.strptime(latest_week_start_str, '%Y-%m-%d')
        
        # Calculate the start of our 20-week period
        start_of_period = latest_week_start - timedelta(weeks=20)
        
        # Fetch only the last 20 weeks of data
        weekly_data = weekly_scores_collection.find({
            'week': {
                '$gte': f"{start_of_period.strftime('%Y-%m-%d')}/{latest_week_start.strftime('%Y-%m-%d')}"
            }
        }).sort('week', -1).limit(20)

        result = []
        for doc in weekly_data:
            week_start_str = doc['week'].split('/')[0]
            week_start_date = datetime.strptime(week_start_str, '%Y-%m-%d')
            
            result.append({
                'date': doc['week'],  # Keep the original week range string
                'week_start': week_start_date.isoformat(),
                'positive': doc['positive'],
                'neutral': doc['neutral'],
                'negative': doc['negative'],
                'weighted_score': doc['weighted_score']
            })

        # Sort by week_start date in descending order (most recent first)
        result.sort(key=lambda x: x['week_start'], reverse=True)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error fetching weekly sentiment: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch weekly sentiment data',
            'details': str(e)
        }), 500  # Return empty list if no data is found

    
if __name__ == '__main__':
    app.run(debug=True)