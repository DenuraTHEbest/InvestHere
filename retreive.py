import os
import gridfs
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_CLUSTER')}/{os.getenv('MONGO_DB')}?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client[os.getenv("MONGO_DB")]
fs = gridfs.GridFS(db)

# Create "retrieved" folder if it doesn't exist
RETRIEVED_FOLDER = os.path.join(os.getcwd(), "retrieved")
os.makedirs(RETRIEVED_FOLDER, exist_ok=True)

def retrieve_files():
    """Retrieve all files from GridFS and save them locally."""
    print("🔍 Retrieving files from MongoDB...")

    # Fetch all files from GridFS
    for file in fs.find():
        filename = file.filename
        file_path = os.path.join(RETRIEVED_FOLDER, filename)

        # Write file contents to local storage
        with open(file_path, "wb") as f:
            f.write(file.read())

        print(f"✅ Retrieved: {filename} -> {file_path}")

    print("🎉 All files retrieved successfully!")

if __name__ == "__main__":
    retrieve_files()
