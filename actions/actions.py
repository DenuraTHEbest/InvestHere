from statistics import stdev, mean
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from pymongo import MongoClient
import certifi
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime, timedelta
from typing import Any, Text, Dict, List

# MongoDB Atlas connection string
USERNAME = "kavishanvishwajith"
PASSWORD = "BjNG7kGpWeLUJXNc"
CLUSTER_URL = "cluster01.e5p2x.mongodb.net"

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
    
class ActionAnalyzeCompanyStock(Action):
    def name(self):
        return "action_analyze_company_stock"

    def run(self, dispatcher, tracker, domain):
        # Connect to ASPI database
        database_name = "IndividualDB"
        mongo_uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{database_name}?retryWrites=true&w=majority"
        client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
        db = client[database_name]
        collection = db["Compnay_Predictions"] 

        company_symbol = tracker.get_slot("company_symbol")
        print(f"Company symbol: {company_symbol}")

        if not company_symbol:
            dispatcher.utter_message("Please provide a valid company name or symbol.")
            return [] 

        # Fetch the latest stock prediction for the given company
        stock_data = collection.find_one({"Company_Name": {"$regex": f"^{company_symbol}", "$options": "i"}})

        if not stock_data:
            dispatcher.utter_message(f"Sorry, no stock predictions found for {company_symbol}.")
            return []

        # Extract predicted prices for the next 7 days
        predicted_prices = [
            stock_data.get(f"Predicted_Day_{i}", None) for i in range(1, 21)
        ]

        # Remove None values in case of missing data
        predicted_prices = [price for price in predicted_prices if price is not None]

        if len(predicted_prices) < 2:
            dispatcher.utter_message(f"Insufficient data to analyze {company_symbol}.")
            return []

        # Compute insights
        avg_price = mean(predicted_prices)
        price_volatility = stdev(predicted_prices) if len(predicted_prices) > 1 else 0
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
    
class ActionAnalyzeSentiment(Action):
    def name(self):
        return "action_analyze_sentiment"

    def run(self, dispatcher, tracker, domain):
        # Connect to ASPI database
        database_name = "test"
        mongo_uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{database_name}?retryWrites=true&w=majority"
        client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
        db = client[database_name]
        collection = db["test"] 

        # Fetch sentiment scores from the last 20 days
        recent_data = list(collection.find().sort("date", -1).limit(20))

        # Extract weighted sentiment scores
        sentiment_scores = [doc["weighted_score"] for doc in recent_data]

        if not sentiment_scores:
            dispatcher.utter_message("No sentiment data found for the past week.")
            return []

        # Calculate the average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        # Calculate volatility (standard deviation)
        sentiment_volatility = stdev(sentiment_scores) if len(sentiment_scores) > 1 else 0

        # Determine trend (positive, negative, or neutral)
        if avg_sentiment > 0.1:
            trend = "positive"
        elif avg_sentiment < -0.1:
            trend = "negative"
        else:
            trend = "neutral"

        # Sentiment Distribution
        negative_ratio = sum(1 for s in sentiment_scores if s < 0) / len(sentiment_scores)
        neutral_ratio = sum(1 for s in sentiment_scores if s == 0) / len(sentiment_scores)
        positive_ratio = sum(1 for s in sentiment_scores if s > 0) / len(sentiment_scores)

        # Sentiment Momentum
        momentum = sentiment_scores[-1] - sentiment_scores[0]

        # Highest & Lowest Sentiment Days
        highest_sentiment = max(sentiment_scores)
        lowest_sentiment = min(sentiment_scores)

        # Consecutive Positive or Negative Streak
        streak = 0
        max_streak = 0
        streak_type = None

        for i in range(1, len(sentiment_scores)):
            if (sentiment_scores[i] > 0 and sentiment_scores[i - 1] > 0) or (sentiment_scores[i] < 0 and sentiment_scores[i - 1] < 0):
                streak += 1
                max_streak = max(max_streak, streak)
                streak_type = "positive" if sentiment_scores[i] > 0 else "negative"
            else:
                streak = 0

        # General Market Sentiment
        dispatcher.utter_message("📊 Sentiment scores range from -1 (very negative) to 1 (very positive), with 0 being neutral.")
        dispatcher.utter_message(f"Over the past week, the market sentiment has been {trend}, with an average sentiment score of {avg_sentiment:.2f}.")  

        if trend == "positive":  
            dispatcher.utter_message("Investor confidence is high, which could lead to upward stock price movements.")  
        elif trend == "negative":  
            dispatcher.utter_message("Market uncertainty is rising, which may cause stock prices to decline.")  
        else:  
            dispatcher.utter_message("The market remains neutral with no strong directional movement.")  

        dispatcher.utter_message(f"Sentiment distribution over the past week: {negative_ratio*100:.1f}% negative, {neutral_ratio*100:.1f}% neutral, and {positive_ratio*100:.1f}% positive.")  
        dispatcher.utter_message(f"Market sentiment volatility is {sentiment_volatility:.2f}, indicating {('high' if sentiment_volatility > 0.2 else 'low')} fluctuations.")  

        if momentum > 0:  
            dispatcher.utter_message("Sentiment is trending upwards, suggesting increasing market optimism.")  
        elif momentum < 0:  
            dispatcher.utter_message("Sentiment is on a downward trend, indicating growing market concerns.")  
        else:  
            dispatcher.utter_message("Market sentiment has remained stable over the past week.")  

        dispatcher.utter_message(f"The highest sentiment score recorded this week was {highest_sentiment:.2f}, reflecting strong positive momentum.")  
        dispatcher.utter_message(f"The lowest sentiment score was {lowest_sentiment:.2f}, marking a significant negative shift on that day.")  

        if max_streak > 2:  
            dispatcher.utter_message(f"The market has shown a {streak_type} sentiment streak for {max_streak+1} consecutive days, signaling a strong short-term trend.")  

        return []

class ActionAnalyzeASPI(Action): 
    def name(self):
        return "action_analyze_aspi"

    def run(self, dispatcher, tracker, domain):
        try:
            # Connect to ASPI database
            database_name = "aspi_database"
            mongo_uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{database_name}?retryWrites=true&w=majority"
            client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
            db = client[database_name]
            aspi_predictions_collection = db["aspi_data"]

            # Retrieve the latest predicted ASPI values
            predicted_data = aspi_predictions_collection.find_one({}, sort=[("Date", -1)])  
            
            # Debugging: Print the retrieved data
            print("Retrieved predicted data from MongoDB:", predicted_data)
            
            if predicted_data and all(f"Predicted_Day_{i}" in predicted_data for i in range(1, 21)):
                # Extract predicted ASPI values for the next 20 days
                predicted_aspi = [predicted_data[f"Predicted_Day_{i}"] for i in range(1, 21)]
                
                # Debugging: Print the extracted predicted ASPI values
                print("Extracted predicted ASPI values:", predicted_aspi)
                
                # **Basic Insights**
                trend = "increase 📈" if predicted_aspi[-1] > predicted_aspi[0] else "decrease 📉"
                volatility = stdev(predicted_aspi)
                overall_change = ((predicted_aspi[-1] - predicted_aspi[0]) / predicted_aspi[0]) * 100
                avg_aspi = mean(predicted_aspi)

                # **Momentum Analysis**
                daily_changes = [predicted_aspi[i] - predicted_aspi[i-1] for i in range(1, len(predicted_aspi))]
                first_5_avg_change = mean(daily_changes[:5])
                last_5_avg_change = mean(daily_changes[-5:])
                momentum_trend = "increasing momentum 🚀" if last_5_avg_change > first_5_avg_change else "decreasing momentum 🛑"

                # **Moving Averages**
                def moving_average(data, window):
                    return sum(data[-window:]) / window  

                sma_5 = moving_average(predicted_aspi, 5)
                sma_10 = moving_average(predicted_aspi, 10)
                sma_20 = moving_average(predicted_aspi, 20)
                trend_type = "bullish 📈" if sma_5 > sma_10 > sma_20 else "bearish 📉"

                # **Predicted Highs & Lows**
                high_aspi = max(predicted_aspi)
                low_aspi = min(predicted_aspi)

                # **Trend Reversal Detection**
                if (predicted_aspi[-1] > predicted_aspi[-5] and predicted_aspi[-5] < predicted_aspi[0]) or \
                   (predicted_aspi[-1] < predicted_aspi[-5] and predicted_aspi[-5] > predicted_aspi[0]):
                    reversal_signal = "potential trend reversal 🔄 detected!"
                else:
                    reversal_signal = "no trend reversal expected ✅."

                dispatcher.utter_message(f"📊 The ASPI is expected to **{trend}** over the next 20 days.")  
                dispatcher.utter_message(f"📈 The average predicted ASPI value over this period is **{avg_aspi:.2f}**.")  
                dispatcher.utter_message(f"📈 The highest projected ASPI value is **{high_aspi:.2f}**, while the lowest is **{low_aspi:.2f}**.")  
                dispatcher.utter_message(f"📉 Market volatility is estimated at **{volatility:.2f} points**, indicating potential fluctuations.")  
                dispatcher.utter_message(f"📊 Over 20 days, the ASPI is forecasted to change by **{overall_change:.2f}%** compared to the starting value.")  
                dispatcher.utter_message(f"📊 The market exhibits **{momentum_trend}** throughout this period.")  
                dispatcher.utter_message(f"📊 Trend analysis based on moving averages suggests a **{trend_type}** market movement.")  
                dispatcher.utter_message(f"⚠️ Market insight: {reversal_signal}")  

            else:
                dispatcher.utter_message("⚠️ Sorry, I couldn't retrieve the predicted ASPI data from the database.")
        except Exception as e:
            print(f"❌ An error occurred while retrieving or processing predicted ASPI data: {e}")
            dispatcher.utter_message("⚠️ An error occurred while analyzing the ASPI data.")

        return []

class ActionAnalyzeASPISpecificDate(Action): 
    def name(self):
        return "action_analyze_aspi_specific_date"

    def run(self, dispatcher, tracker, domain):
        try:
            # Retrieve the date input from user
            user_date = tracker.get_slot("specific_date")
            if not user_date:
                dispatcher.utter_message("📅 Please provide a valid date to analyze ASPI insights.")
                return []

            # Convert user input into datetime format
            try:
                user_date = datetime.strptime(user_date, "%Y-%m-%d").date()
            except ValueError:
                dispatcher.utter_message("⚠️ Invalid date format. Please use YYYY-MM-DD.")
                return []

            # Connect to ASPI database
            database_name = "aspi_database"
            mongo_uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{database_name}?retryWrites=true&w=majority"
            client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
            db = client[database_name]
            aspi_predictions_collection = db["aspi_data"]

            # Retrieve ASPI data for the given date
            query_date = user_date.strftime("%Y-%m-%dT00:00:00.000+00:00")
            predicted_data = aspi_predictions_collection.find_one({"Date": query_date})
            if not predicted_data:
                dispatcher.utter_message(f"⚠️ No ASPI data available for {user_date}.")
                return []

            # Retrieve previous day's ASPI for comparison
            previous_date = user_date - timedelta(days=1)
            previous_query_date = previous_date.strftime("%Y-%m-%dT00:00:00.000+00:00")
            previous_data = aspi_predictions_collection.find_one({"Date": previous_query_date})
            if not previous_data:
                dispatcher.utter_message(f"⚠️ Unable to retrieve data for {previous_date}, so trends may be incomplete.")

            # Extract ASPI values
            aspi_today = predicted_data.get("Predicted_Day_1")
            aspi_yesterday = previous_data.get("Predicted_Day_1") if previous_data else None

            if aspi_today is None:
                dispatcher.utter_message(f"⚠️ No predicted ASPI value found for {user_date}.")
                return []

            # **Daily Change & Momentum**
            daily_change = aspi_today - (aspi_yesterday if aspi_yesterday else aspi_today)
            daily_change_pct = (daily_change / aspi_yesterday) * 100 if aspi_yesterday else 0
            momentum = "bullish 📈" if daily_change > 0 else "bearish 📉"
            strength = "strong" if abs(daily_change_pct) > 1.5 else "weak"

            # **Volatility & Range**
            last_five_days = [doc["Predicted_ASPI"] for doc in aspi_predictions_collection.find({"Date": {"$lte": str(user_date)}}).sort("Date", -1).limit(5)]
            daily_volatility = stdev(last_five_days) if len(last_five_days) >= 2 else 0

            # **Support & Resistance Levels**
            support_level = min(last_five_days) if last_five_days else aspi_today
            resistance_level = max(last_five_days) if last_five_days else aspi_today

            # **Trading Signal**
            if aspi_today > resistance_level * 0.98:  
                signal = "🔼 Possible breakout above resistance!"
            elif aspi_today < support_level * 1.02:  
                signal = "🔽 Possible breakdown below support!"
            else:
                signal = "✅ Market remains within expected range."

            # **Output Insights**
            dispatcher.utter_message(f"📊 ASPI value for {user_date}: **{aspi_today:.2f}**")  
            dispatcher.utter_message(f"📉 Market trend: **{momentum}** with **{strength}** momentum.")  
            dispatcher.utter_message(f"📊 ASPI change: **{daily_change:.2f} points ({daily_change_pct:.2f}%)**")  
            dispatcher.utter_message(f"⚡ Volatility level: **{daily_volatility:.2f} points**")  
            dispatcher.utter_message(f"🔍 Support: **{support_level:.2f}**, Resistance: **{resistance_level:.2f}**")  
            dispatcher.utter_message(f"⚠️ Trading insight: {signal}")  

        except Exception as e:
            print(f"❌ Error analyzing ASPI data: {e}")
            dispatcher.utter_message("⚠️ An error occurred while analyzing the ASPI data.")

        return []  

