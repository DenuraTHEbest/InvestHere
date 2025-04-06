from pymongo import MongoClient
import certifi
import datetime

# MongoDB URI
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"

# Connect to MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['aspi_database']
collection = db['aspi_data']

print("✅ Connected to MongoDB Atlas successfully!")

# Fetch the lengthy document (starting from May 16, 2024)
document = collection.find_one({"Date": datetime.datetime(2024, 5, 16)})

if not document:
    print("❌ Document for May 16, 2024, not found!")
    exit()

# Extract the predicted values
predicted_values = [document[f"Predicted_Day_{i}"] for i in range(1, 21)]

# Define the starting date (May 16, 2024)
start_date = datetime.datetime(2024, 5, 16)

# Generate 20 trading days (CSE trading days)
trading_days = []
current_date = start_date
while len(trading_days) < 20:
    # Skip weekends (Saturday and Sunday)
    if current_date.weekday() < 5:  # 0 = Monday, 4 = Friday
        trading_days.append(current_date)
    current_date += datetime.timedelta(days=1)

# Create 20 new documents
new_documents = []
for i, date in enumerate(trading_days):
    new_documents.append({
        "Date": date,
        "Predicted_Day_1": predicted_values[i]
    })

# Insert the new documents into the database
collection.insert_many(new_documents)

print(f"✅ Successfully split the document into {len(new_documents)} smaller documents!")