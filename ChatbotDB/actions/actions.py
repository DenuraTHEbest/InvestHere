from statistics import stdev, mean
import requests
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from pymongo import MongoClient
import certifi

# MongoDB Atlas connection string
username = "kavishanvishwajith"
password = "BjNG7kGpWeLUJXNc"
cluster_url = "cluster01.e5p2x.mongodb.net"
database_name = "aspi_database"

# Construct the connection string
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=true&w=majority"

# Connect to MongoDB Atlas with SSL
try:
    client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
    db = client[database_name]
    aspi_predictions_collection = db["aspi_predictions"]
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")

# Load pre-trained GPT-2 model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Set pad_token to eos_token (End of Sequence) to handle padding correctly
tokenizer.pad_token = tokenizer.eos_token

# Put the model in evaluation mode
model.eval()

class ActionStockPrice(Action):
    def name(self):
        return "action_stock_price"

    def run(self, dispatcher, tracker, domain):
        company_symbol = tracker.get_slot("company_symbol")
        if not company_symbol:
            dispatcher.utter_message("Please provide a company symbol.")
            return []

        api_key = "WSBJ9P3L1ZCVEMFJ"
        api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={company_symbol}&interval=1min&apikey={api_key}"
        response = requests.get(api_url).json()

        try:
            last_refreshed = response["Meta Data"]["3. Last Refreshed"]
            closing_price = response["Time Series (1min)"][last_refreshed]["4. close"]
            dispatcher.utter_message(f"The latest closing price of {company_symbol} is ${closing_price}.")
        except KeyError:
            dispatcher.utter_message("Sorry, I couldn't retrieve the stock price. Please ensure the company symbol is correct.")

        return []
    
class ActionAnalyzeCompanyStock(Action):
    def name(self):
        return "action_analyze_company_stock"

    def run(self, dispatcher, tracker, domain):
        company_symbol = tracker.get_slot("company_symbol")
        print(f"Company symbol: {company_symbol}")
        
        # Dummy stock price predictions for the next 7 days for different companies
        stock_predictions = {
            "DIAL": [150, 152, 155, 157, 160, 158, 162],  
            "COMB": [2800, 2825, 2830, 2840, 2855, 2845, 2860],  
            "HHL": [3450, 3470, 3500, 3510, 3525, 3540, 3555], 
            "HNB": [700, 715, 720, 725, 730, 735, 740], 
            "LIOC": [300, 305, 310, 315, 320, 318, 325],  
            "JKH": [150, 148, 149, 151, 153, 152, 155]  
        }

        if not company_symbol or company_symbol not in stock_predictions:
            dispatcher.utter_message("Sorry, I don't have stock predictions for that company. Please try another one.")
            return []

        predicted_prices = stock_predictions[company_symbol]

        # Calculate insights
        avg_price = mean(predicted_prices)
        price_volatility = stdev(predicted_prices)
        trend = "increase" if predicted_prices[-1] > predicted_prices[0] else "decrease"
        week_change = ((predicted_prices[-1] - predicted_prices[0]) / predicted_prices[0]) * 100

        # Send insights to user
        dispatcher.utter_message(f"📈 Stock Analysis for {company_symbol}:")
        dispatcher.utter_message(f"🔹 The stock price is predicted to {trend} over the next week.")
        dispatcher.utter_message(f"🔹 Average predicted price: ${avg_price:.2f}")
        dispatcher.utter_message(f"🔹 Volatility: {price_volatility:.2f} ({'high' if price_volatility > 2 else 'low'} fluctuations)")
        dispatcher.utter_message(f"🔹 Expected percentage change for the week: {week_change:.2f}%")

        if trend == "increase":
            dispatcher.utter_message(f"🚀 A price increase suggests positive market sentiment for {company_symbol}.")
        else:
            dispatcher.utter_message(f"📉 A price decrease suggests possible market corrections or concerns for {company_symbol}.")

        return []

class ActionSentimentAnalysis(Action):
    def name(self):
        return "action_sentiment_analysis"

    def run(self, dispatcher, tracker, domain):
        company_symbol = tracker.get_slot("company_symbol")
        if not company_symbol:
            dispatcher.utter_message("Please provide a company symbol.")
            return []

        api_key = "WSBJ9P3L1ZCVEMFJ"
        api_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={company_symbol}&apikey={api_key}"
        response = requests.get(api_url).json()

        try:
            sentiment_score = response["feed"][0]["overall_sentiment_score"]
            dispatcher.utter_message(f"The current sentiment score for {company_symbol} is {sentiment_score}.")
        except (KeyError, IndexError):
            dispatcher.utter_message("Sorry, I couldn't retrieve the sentiment data. Please ensure the company symbol is correct.")

        return []
    
class ActionAnalyzeSentiment(Action):
    def name(self):
        return "action_analyze_sentiment"

    def run(self, dispatcher, tracker, domain):
        # Dummy sentiment scores for the past week
        sentiment_scores = [0.2, -0.1, 0.3, -0.2, 0.4, -0.05, 0.35]

        # Calculate the average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        # Calculate volatility (standard deviation)
        sentiment_volatility = stdev(sentiment_scores)

        # Determine trend (positive, negative, or neutral)
        if avg_sentiment > 0.1:
            trend = "positive"
        elif avg_sentiment < -0.1:
            trend = "negative"
        else:
            trend = "neutral"

        # Generate insights
        dispatcher.utter_message(f"Over the past week, the sentiment trend for the market is {trend}.")
        dispatcher.utter_message(f"The average sentiment score is {avg_sentiment:.2f}, indicating a {trend} sentiment.")
        dispatcher.utter_message(f"Market sentiment volatility is {sentiment_volatility:.2f}, suggesting {('high' if sentiment_volatility > 0.2 else 'low')} fluctuations.")
        
        if trend == "positive":
            dispatcher.utter_message("A positive sentiment trend often indicates investor confidence, potentially driving stock prices up.")
        elif trend == "negative":
            dispatcher.utter_message("A negative sentiment trend might indicate uncertainty or bad news, possibly leading to a stock price decline.")
        else:
            dispatcher.utter_message("A neutral sentiment trend suggests a balanced market with no strong movement in either direction.")

        return []

class ActionOpenAIChat(Action):
    def name(self):
        return "action_openai_chat"

    def run(self, dispatcher, tracker, domain):
        user_message = tracker.latest_message.get("text")

        # Encode user input into tokens
        inputs = tokenizer(user_message, return_tensors="pt", padding=True, truncation=True)

        # Explicitly create an attention mask
        attention_mask = inputs['attention_mask']

        # Generate response from GPT-2
        with torch.no_grad():
            output = model.generate(
                inputs['input_ids'],
                attention_mask=attention_mask,
                max_length=min(len(user_message) + 40, 100),  # Dynamic max length
                temperature=0.7,
                top_p=0.9,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True
            )

        # Decode response and clean up
        ai_reply = tokenizer.decode(output[0], skip_special_tokens=True).strip()

        # Filter out repeated prompts
        if user_message.lower() in ai_reply.lower():
            ai_reply = ai_reply.split(user_message, 1)[-1].strip()

        # Fallback message for low-quality responses
        if "i don't know" in ai_reply.lower() or len(ai_reply.split()) < 3:
            ai_reply = "I'm not sure about that. Could you clarify or ask something else?"

        dispatcher.utter_message(ai_reply)
        return []

class ActionASPI(Action):
    def name(self):
        return "action_aspi_price"

    def run(self, dispatcher, tracker, domain):
        api_key = "c7240bd59cc3483:tfbxk4l1hy3pdcg"
        url = "https://api.tradingeconomics.com/markets/cseall:ind"
        headers = {
            "Authorization": f"Basic {api_key}"
        }

        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            if response.status_code == 200 and isinstance(data, list) and data:
                aspi_value = data[0].get("value")
                if aspi_value is not None:
                    dispatcher.utter_message(f"The current ASPI value is {aspi_value}.")
                else:
                    dispatcher.utter_message("Sorry, I couldn't retrieve the ASPI value.")
            else:
                dispatcher.utter_message("Sorry, I couldn't retrieve the ASPI value.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message("An error occurred while fetching ASPI data.")

        return []
    
class ActionAnalyzeASPI(Action): 
    def name(self):
        return "action_analyze_aspi"

    def run(self, dispatcher, tracker, domain):
        try:
            # Retrieve the latest predicted ASPI values
            predicted_data = aspi_predictions_collection.find_one({}, sort=[("Date", -1)])  
            
            # Debugging: Print the retrieved data
            print("Retrieved predicted data from MongoDB:", predicted_data)
            
            if predicted_data and all(f"Predicted_Day_{i}" in predicted_data for i in range(1, 21)):
                # Extract predicted ASPI values for the next 20 days
                predicted_aspi = [predicted_data[f"Predicted_Day_{i}"] for i in range(1, 21)]
                
                # Debugging: Print the extracted predicted ASPI values
                print("Extracted predicted ASPI values:", predicted_aspi)
                
                # Calculate trend (simple: check if last value is higher than the first)
                trend = "increase 📈" if predicted_aspi[-1] > predicted_aspi[0] else "decrease 📉"
                
                # Calculate volatility (standard deviation)
                volatility = stdev(predicted_aspi)
                
                # Calculate overall percentage change from Day 2 to Day 21
                overall_change = ((predicted_aspi[-1] - predicted_aspi[0]) / predicted_aspi[0]) * 100
                
                # Mean ASPI prediction for the 20-day period
                avg_aspi = mean(predicted_aspi)

                # Generate insights for the user
                dispatcher.utter_message(f"📊 The ASPI is expected to **{trend}** over the next 20 days.")
                dispatcher.utter_message(f"📈 The average predicted ASPI value is **{avg_aspi:.2f}**.")
                dispatcher.utter_message(f"📉 The market volatility is estimated at **{volatility:.2f} points**.")
                dispatcher.utter_message(f"📊 Over the 20-day period, the ASPI is predicted to change by **{overall_change:.2f}%** compared to the start.")

            else:
                dispatcher.utter_message("⚠️ Sorry, I couldn't retrieve the predicted ASPI data from the database.")
        except Exception as e:
            # Debugging: Print any exceptions that occur
            print(f"❌ An error occurred while retrieving or processing predicted ASPI data: {e}")
            dispatcher.utter_message("⚠️ An error occurred while analyzing the ASPI data.")

        return []