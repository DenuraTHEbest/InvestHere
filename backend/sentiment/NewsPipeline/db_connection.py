from pymongo import MongoClient

def get_database():
    client = MongoClient("mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01")
    db = client["news_database"]
    return db
