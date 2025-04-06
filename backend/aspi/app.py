from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
import logging
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB Configuration
try:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/test?retryWrites=true&w=majority")
    DB_NAME_TEST = os.getenv("DB_NAME_TEST", "test")  # For daily_scores
    DB_NAME_ASPI = os.getenv("DB_NAME_ASPI", "aspi_database")  # For aspi_data
    
    client = MongoClient(MONGO_URI)
    
    # Connect to both databases
    db_test = client[DB_NAME_TEST]  # For daily_scores
    db_aspi = client[DB_NAME_ASPI]  # For aspi_data
    
    # Collections
    daily_scores_col = db_test["daily_scores"]  # In 'test' database
    aspi_data_col = db_aspi["aspi_data"]        # In 'aspi_database'
    
    logger.info("✅ MongoDB connected successfully to both databases")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    raise

@app.route('/api/process_aspi', methods=['POST'])
def process_aspi():
    try:
        # 1. Get decimal_value from frontend
        data = request.json
        decimal_value = float(data['decimalValue'])
        logger.debug(f"Received decimal_value: {decimal_value}")

        # 2. Fetch latest weighted_score from daily_scores (in 'test' database)
        weighted_score_doc = daily_scores_col.find_one(
            {}, 
            sort=[("date", -1)]  # Most recent entry
        )
        if not weighted_score_doc:
            return jsonify({"status": "error", "message": "No weighted score found"}), 400
        
        weighted_score = weighted_score_doc["weighted_score"]
        logger.debug(f"Fetched weighted_score: {weighted_score}")

        # 3. Call Feature Engineering Pipeline
        feature_proc = subprocess.run(
            ["python", "featureEngineeringPipeline.py", str(decimal_value), str(weighted_score)],
            capture_output=True,
            text=True
        )
        if feature_proc.returncode != 0:
            logger.error(f"Feature pipeline failed: {feature_proc.stderr}")
            return jsonify({"status": "error", "message": "Feature engineering failed"}), 500

        # 4. Call Admin Pipeline (Prediction)
        admin_proc = subprocess.run(
            ["python", "adminpipeline2.py", str(decimal_value)],
            capture_output=True,
            text=True
        )
        if admin_proc.returncode != 0:
            logger.error(f"Admin pipeline failed: {admin_proc.stderr}")
            return jsonify({"status": "error", "message": "Prediction failed"}), 500

        # 5. Parse prediction (assumes adminpipeline2.py prints the predicted value)
        predicted_value = float(admin_proc.stdout.strip())
        logger.debug(f"Predicted value: {predicted_value}")

        # 6. Save to aspi_data collection (now in 'aspi_database')
        aspi_data_col.insert_one({
            "Date": datetime.now(),
            "Predicted_Day_1": predicted_value,
            "Actual_Day_1": decimal_value,
        })
        logger.info("📊 Saved prediction to aspi_data in aspi_database")

        # 7. Return success
        return jsonify({
            "status": "success",
            "weighted_score": weighted_score,
            "predicted_value": predicted_value,
            "feature_output": feature_proc.stdout,
            "admin_output": admin_proc.stdout
        })

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get_predictions', methods=['GET'])
def get_predictions():
    try:
        predictions = list(aspi_data_col.find(
            {},
            {"_id": 0, "Date": 1, "Predicted_Day_1": 1, "Actual_Day_1": 1}
        ).sort("Date", -1).limit(20))
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"Failed to fetch predictions: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/update_prediction', methods=['POST'])
def update_prediction():
    try:
        data = request.json
        result = aspi_data_col.update_one(
            {"Date": data["Date"]},
            {"$set": {
                "Predicted_Day_1": data["Predicted_Day_1"],
                "Actual_Day_1": data["Actual_Day_1"]
            }},
            upsert=True  # Creates document if it doesn't exist
        )
        logger.debug(f"Update result: {result.raw_result}")
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Update failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(port=5050, debug=True)