from pymongo import MongoClient
import certifi

# MongoDB Atlas connection string
username = "kavishanvishwajith"
password = "BjNG7kGpWeLUJXNc"
cluster_url = "cluster01.e5p2x.mongodb.net"
database_name = "test"

# Construct the connection string
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=true&w=majority"

# Connect to MongoDB Atlas with SSL
try:
    client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
    db = client[database_name]
    news_collection = db["news"]
    predictions_collection = db["predictions"]
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")