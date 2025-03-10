from flask import Flask, request, jsonify, abort
from process_news import process_news_entry  # Import the function to process individual entries
from aggregate_sentiment import compute_and_store_scores  # Import the function to compute scores
from database.init_mongo import news_collection  # Import MongoDB collection
import logging
import pandas as pd

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/process_news', methods=['POST'])
def process_news_endpoint():
    try:
        logger.info("Received request at /process_news")

        # Check if file exists in request
        if 'file' not in request.files:
            abort(400, description="Invalid input: 'file' field is required")

        file = request.files['file']
        if file.filename == '':
            abort(400, description="Invalid input: No file selected")

        logger.info(f"File received: {file.filename}")

        # Read CSV
        df = pd.read_csv(file)
        logger.info(f"CSV file read successfully. Shape: {df.shape}")

        if df.empty:
            logger.warning("Uploaded CSV file is empty")
            return jsonify({"status": "warning", "message": "Empty CSV file"}), 400
        
        # Process data in batches
        processed_entries = []
        for _, row in df.iterrows():
            result = process_news_entry(row.to_dict())  # Process each row
            if result and not result.get("ignored"):  # Skip ignored entries
                processed_entries.append(result)

        # Insert into MongoDB at once (batch insert)
        if processed_entries:
            news_collection.insert_many(processed_entries)
            logger.info(f"Inserted {len(processed_entries)} entries into MongoDB")

            # Compute and store sentiment scores
            compute_and_store_scores(processed_entries)
            logger.info("Computed and stored sentiment scores successfully")

        return jsonify({"status": "success", "processed_entries": len(processed_entries)}), 200

    except Exception as e:
        logger.error(f"Error in /process_news: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)