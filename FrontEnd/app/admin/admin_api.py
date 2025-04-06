from flask import Flask, request, jsonify
from pymongo import MongoClient
import subprocess

app = Flask(__name__)

# MongoDB connection details
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/test?retryWrites=true&w=majority"
DB_NAME = "test"          # Replace with your database name
COLLECTION_NAME = "daily_scores"  # Replace with your collection name

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

@app.route('/process_news', methods=['POST'])
def process_news():
    try:
        # Fetch the latest document from the collection
        latest_document = collection.find_one(
            sort=[("date", -1)],  # Sort by date in descending order
            projection={"_id": 0, "weighted_score": 1}  # Only include the weighted_score field
        )

        if not latest_document:
            return jsonify({"status": "error", "message": "No data found"}), 404

        # Get the weighted score
        weighted_score = latest_document["weighted_score"]

        # Get the decimal value from the frontend
        decimal_value = request.form.get('decimalValue')
        if not decimal_value:
            return jsonify({"status": "error", "message": "decimalValue is required"}), 400

        # Call featureEngineeringPipeline.py with the decimal value
        feature_result = subprocess.run(
            ["python", "featureEngineeringPipeline.py", str(decimal_value), str(weighted_score)],
            capture_output=True,
            text=True
        )

        if feature_result.returncode != 0:
            return jsonify({"status": "error", "message": feature_result.stderr}), 500

        # Call adminpipeline.py
        admin_result = subprocess.run(
            ["python", "adminpipeline.py", str(decimal_value)],  
            capture_output=True,
            text=True
        )

        if admin_result.returncode != 0:
            return jsonify({"status": "error", "message": admin_result.stderr}), 500

        # Return success response with the weighted score and pipeline results
        return jsonify({
            "status": "success",
            "weighted_score": weighted_score,
            "feature_pipeline_output": feature_result.stdout,
            "admin_pipeline_output": admin_result.stdout
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500