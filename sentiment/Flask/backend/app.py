from flask import Flask, request, jsonify, abort
from process_news import process_batch, process_news_entry
from aggregate_sentiment import aggregate_sentiment
from database.init_mongo import predictions_collection, news_collection
import logging
import pandas as pd
from io import StringIO

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
        import pandas as pd
        df = pd.read_csv(file)
        logger.info(f"CSV file read successfully. Shape: {df.shape}")

        if df.empty:
            logger.warning("Uploaded CSV file is empty")
            return jsonify({"status": "warning", "message": "Empty CSV file"}), 400
        
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

        return jsonify({"status": "success", "processed_entries": len(processed_entries)}), 200

    except Exception as e:
        logger.error(f"Error in /process_news: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)