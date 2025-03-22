from pymongo import MongoClient
import certifi
import joblib
import pandas as pd
import datetime

# =============================================
# MongoDB URI & Connection
# =============================================
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['Individual_comp_predicitons']
collection = db['Individual_comp_predicitons']

print("✅ Connected to MongoDB Atlas successfully!")

# =============================================
# Load the trained model
# =============================================
model_path = "model.pkl"  # Must match your saved file from the training script
model = joblib.load(model_path)
print("✅ Model loaded successfully!")

# =============================================
# Load test target results (actual values)x values
# =============================================
target_path = "aspi_test_targets.csv" #
target = pd.read_csv(target_path)

# =============================================
# Load test dataset (features for predictions)
# =============================================
test_data_path = "aspi_test_features.csv"  # Update with your actual path,y values
test_data = pd.read_csv(test_data_path)

# =============================================
# Predict ASPI prices (Multi-day example)
# =============================================
# If your model is actually single-day, you'll want to adapt how you produce 20 days of predictions.
# For demonstration, let's assume the shape is correct for multi-day.
predictions = model.predict(test_data)

# Convert predictions into a DataFrame
# We'll assume your snippet wants 20 future days:
predictions_df = pd.DataFrame(
    predictions, columns=[f'Predicted_Day_{i}' for i in range(1, 21)]
)

predictions_df.insert(0, 'Date', test_data['Date'])  # Add Date column from test data

# =============================================
# Convert 'Date' column from Unix -> normal date
# =============================================
def convert_date(unix_time):
    return datetime.datetime.fromtimestamp(int(unix_time)).strftime('%Y-%m-%d')

predictions_df['Date'] = predictions_df['Date'].apply(convert_date)

# =============================================
# Match actual target values to predictions
# =============================================
target_values_for_predictions = target.iloc[-len(predictions_df):]  # last N rows
for i in range(1, 21):
    predictions_df[f'Actual_Day_{i}'] = target_values_for_predictions[f'Target_{i}'].values

# =============================================
# Convert to dictionary (for MongoDB)
# =============================================
predictions_dict = predictions_df.to_dict(orient="records")

# Insert only the last row if you want
last_prediction = predictions_dict[-1]
predictions_dict = [last_prediction]  # or skip this step if you want them all

collection.insert_many(predictions_dict)
print("✅ Inserted last row predictions into MongoDB successfully!")

# =============================================
# Insert more rows or a slice
# For example, rows [-40:-20] with limited columns
# =============================================
predictions_dict_full = predictions_df.to_dict(orient="records")

required_data = [
    {
        "Date": entry["Date"],
        "Predicted_Day_1": entry["Predicted_Day_1"],
        "Actual_Day_1": entry["Actual_Day_1"]
    }
    for entry in predictions_dict_full[-40:-20]
]
collection.insert_many(required_data)
print("✅ Inserted [-40:-20] partial predictions into MongoDB!")

# =============================================
# Verify one document
# =============================================
sample_prediction = collection.find_one()
print("Sample prediction from MongoDB:", sample_prediction)
