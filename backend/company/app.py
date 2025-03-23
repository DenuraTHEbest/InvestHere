from flask import Flask, request, jsonify
import os
import pandas as pd
import joblib
import certifi
from pymongo import MongoClient
from flask_cors import CORS

# Flask app
app = Flask(__name__)
CORS(app)

# MongoDB configuration
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["IndividualDB3"]
collection = db["Company_Predictions3"]

# Model Path
model_path = r"20daysModel.pkl"
model = joblib.load(model_path)
print("✅ Model loaded successfully!")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}


# Function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/process_news', methods=['POST'])
def process_news():
    if 'file1' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})

    file1 = request.files['file1']
    if file1.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})

    if file1 and allowed_file(file1.filename):
        filename = os.path.join("uploads", file1.filename)
        file1.save(filename)

        try:
            # Process file here
            df_features = pd.read_csv(filename)

            # Placeholder for prediction logic
            predictions = []  # Example predictions
            for _ in range(20):  # Dummy loop to simulate 20-day prediction
                predictions.append([0])

            # Convert to DataFrame and save to MongoDB
            df_preds = pd.DataFrame(predictions, columns=[f"Predicted_Day_{i + 1}" for i in range(20)])
            df_preds.insert(0, "Company_Name", file1.filename)
            df_preds["Date"] = "2023-09-30"  # Replace with actual date logic

            # Insert records into MongoDB
            records_to_insert = df_preds.to_dict(orient="records")
            collection.insert_many(records_to_insert)
            print(f"✅ Records inserted into MongoDB for {file1.filename}")

            return jsonify({"status": "success", "message": "File uploaded and processed successfully!"})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    return jsonify({"status": "error", "message": "Invalid file type or no file uploaded"})


if __name__ == '__main__':
    app.run(debug=True)
