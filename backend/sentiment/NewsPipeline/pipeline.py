import datetime
from db_connection import get_database
from categorizer import categorize_news
from sentiment_analyzer import analyze_sentiment

def process_news():
    db = get_database()
    raw_collection = db["raw_news"]
    business_collection = db["business_sentiment"]

    two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
    news_list = list(raw_collection.find({"timestamp": {"$gte": two_days_ago}}))

    if not news_list:
        print("No recent news to process")
        return

    for news in news_list:
        title = news["title"]
        category = categorize_news(title)

        if category == "business news":
            sentiment = analyze_sentiment(title)

            business_item = {
                "title": title,
                "category": category,
                "sentiment": sentiment,
                "date": news["date"],
                "timestamp": news["timestamp"]
            }
            business_collection.insert_one(business_item)

    print("News processing completed")
