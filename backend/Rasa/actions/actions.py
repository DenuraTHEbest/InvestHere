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

class ActionOpenAIChat(Action):
    def name(self):
        return "action_openai_chat"

    def run(self, dispatcher, tracker, domain):
        user_message = tracker.latest_message.get("text")

        API_KEY = "MkChCsEH6X7QUEYezIXrBj1czFAGsRQH" 
        API_URL = "https://api.mistral.ai/v1/chat/completions" 
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-large-latest",  
            "messages": [{"role": "user", "content": user_message}]
        }

        try:
            response = requests.post(API_URL, json=data, headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                ai_reply = response_data["choices"][0]["message"]["content"]

                # Filter out repeated prompts
                if user_message.lower() in ai_reply.lower():
                    ai_reply = ai_reply.split(user_message, 1)[-1].strip()

                # Fallback message for low-quality responses
                if "i don't know" in ai_reply.lower() or len(ai_reply.split()) < 3:
                    ai_reply = "I'm not sure about that. Could you clarify or ask something else?"
                
                # Send the response from Mistral back to the user
                dispatcher.utter_message(ai_reply)
            else:
                dispatcher.utter_message(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            dispatcher.utter_message(f"Error connecting to Mistral: {str(e)}")

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

        # Get company name and transform it
        company_symbol = tracker.get_slot("company_symbol")
        print(f"Company symbol: {company_symbol}")

        if not company_symbol:
            dispatcher.utter_message("It seems like an invalid company name. Can you provide a valid company name?")
            return []

        # Fetch the latest stock prediction for the given company
        stock_data = collection.find_one({"Company_Name": {"$regex": f"^{company_symbol}", "$options": "i"}})

        if not stock_data:
            dispatcher.utter_message(f"Sorry, there's no stock predictions found for {company_symbol}.")
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

        def simple_moving_average(prices, window=3):
            if len(prices) < window:
                return None
            return mean(prices[-window:])

        sma_3 = simple_moving_average(predicted_prices, window=3)

        support_level = min(predicted_prices)
        resistance_level = max(predicted_prices)

        momentum = predicted_prices[-1] - predicted_prices[0]
        rsi = 100 - (100 / (1 + (sum(predicted_prices[-3:]) / sum(predicted_prices[:3])))) if len(predicted_prices) >= 6 else None

        price_range = resistance_level - support_level
        volatility_index = (price_volatility / avg_price) * 100

        buy_signal = False
        sell_signal = False
        decision = "📊 Hold"

        if rsi is not None:
            if predicted_prices[-1] <= support_level * 1.05 and rsi < 30:
                buy_signal = True
                decision = "✅ Buy Signal: Price near support & oversold (RSI < 30)"
            elif predicted_prices[-1] >= resistance_level * 0.95 and rsi > 70:
                sell_signal = True
                decision = "❌ Sell Signal: Price near resistance & overbought (RSI > 70)"

        # Send insights to user  
        dispatcher.utter_message(
            f"📈 **Stock Analysis for {company_symbol}**\n\n"
            f"The stock price for {company_symbol} is expected to {trend} over the next week. "
            f"The average predicted price is ${avg_price:.2f}. "
            f"The expected change in price over the next week is {week_change:.2f}% ({'📈 Increase' if week_change > 0 else '📉 Decrease'}). "
            f"The volatility level is {price_volatility:.2f} ({'High' if price_volatility > 2 else 'Low'} fluctuations). "
            f"Here’s the technical analysis of the stock: "
            + (f"On average, the stock price over the last 3 days is ${sma_3:.2f}. " if sma_3 else "") 
            + f"The support level for the stock is ${support_level:.2f}. "
            f"The resistance level for the stock is ${resistance_level:.2f}. "
            f"The momentum for the stock is {'📈 Positive' if momentum > 0 else '📉 Negative'}. "
            + (f"The Relative Strength Index (RSI) is {rsi:.2f}, indicating that the stock is {'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'}. " if rsi else "") 
            + f"The volatility index for the stock is {volatility_index:.2f}%. "
            f"📢 **Trading Signal:** {decision}"
        )

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
            dispatcher.utter_message("Looks like there's no sentiment data from the past week.")
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
        dispatcher.utter_message(f"Over the past week, the market sentiment has been {trend}, with an average sentiment score of {avg_sentiment:.2f}. "  
                         f"Sentiment distribution over the past week: {negative_ratio*100:.1f}% negative, {neutral_ratio*100:.1f}% neutral, and {positive_ratio*100:.1f}% positive. "  
                         f"Market sentiment volatility is {sentiment_volatility:.2f}, indicating {('high' if sentiment_volatility > 0.2 else 'low')} fluctuations.")  
        if trend == "positive":  
            dispatcher.utter_message("Investor confidence is high, which could lead to upward stock price movements.")  
        elif trend == "negative":  
            dispatcher.utter_message("Market uncertainty is rising, which may cause stock prices to decline.")  
        else:  
            dispatcher.utter_message("The market remains neutral with no strong directional movement.")  
        if momentum > 0:  
            dispatcher.utter_message("Sentiment is trending upwards, suggesting increasing market optimism.")  
        elif momentum < 0:  
            dispatcher.utter_message("Sentiment is on a downward trend, indicating growing market concerns.")  
        else:  
            dispatcher.utter_message("Market sentiment has remained stable over the past week.")  
        dispatcher.utter_message(f"The highest sentiment score recorded this week was {highest_sentiment:.2f}, reflecting strong positive momentum, while the lowest sentiment score was {lowest_sentiment:.2f}, marking a significant negative shift on that day.")  
        if max_streak > 2:  
            dispatcher.utter_message(f"The market has shown a {streak_type} sentiment streak for {max_streak+1} consecutive days, signaling a strong short-term trend.")  

        return []

class ActionAnalyzeASPI(Action): 
    def name(self):
        return "action_analyze_aspi"

    def run(self, dispatcher, tracker, domain):
        try:
            database_name = "aspi_database"
            mongo_uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{database_name}?retryWrites=true&w=majority"
            client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
            db = client[database_name]
            aspi_predictions_collection = db["aspi_data"]

            # Retrieve predicted ASPI values from 2024-05-16 onward
            query = {"Date": {"$gte": datetime(2024, 5, 16)}}
            predicted_data = list(aspi_predictions_collection.find(query).sort("Date", 1))  
            
            # Debugging: Print the retrieved data
            print("Retrieved predicted data from MongoDB:", predicted_data)
            
            if predicted_data:
                # Extracting "Predicted_Day_1" values as the forecasted ASPI trend
                predicted_aspi = [entry["Predicted_Day_1"] for entry in predicted_data if "Predicted_Day_1" in entry]
                
                # Debugging: Print the extracted predicted ASPI values
                print("Extracted predicted ASPI values:", predicted_aspi)

                if len(predicted_aspi) > 1:
                    # **Basic Insights**
                    trend = "increase 📈" if predicted_aspi[-1] > predicted_aspi[0] else "decrease 📉"
                    volatility = stdev(predicted_aspi) if len(predicted_aspi) > 1 else 0
                    overall_change = ((predicted_aspi[-1] - predicted_aspi[0]) / predicted_aspi[0]) * 100
                    avg_aspi = mean(predicted_aspi)

                    # **Momentum Analysis**
                    daily_changes = [predicted_aspi[i] - predicted_aspi[i-1] for i in range(1, len(predicted_aspi))]
                    first_5_avg_change = mean(daily_changes[:5]) if len(daily_changes) >= 5 else 0
                    last_5_avg_change = mean(daily_changes[-5:]) if len(daily_changes) >= 5 else 0
                    momentum_trend = "increasing momentum 🚀" if last_5_avg_change > first_5_avg_change else "decreasing momentum 🛑"

                    # **Moving Averages**
                    def moving_average(data, window):
                        return sum(data[-window:]) / window if len(data) >= window else sum(data) / len(data)

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

                    dispatcher.utter_message(f"📊 The ASPI is expected to **{trend}** over the predicted period, with an average predicted value of **{avg_aspi:.2f}**. 📈 The highest projected ASPI value is **{high_aspi:.2f}**, while the lowest is **{low_aspi:.2f}**. 📉 Market volatility is estimated at **{volatility:.2f} points**, indicating potential fluctuations. 📊 The ASPI is forecasted to change by **{overall_change:.2f}%** compared to the starting value, exhibiting **{momentum_trend}** throughout this period. 📊 Trend analysis suggests a **{trend_type}** market movement. ⚠️ Market insight: {reversal_signal}") 

                else:
                    dispatcher.utter_message("⚠️ Not enough ASPI predictions available to analyze trends.")
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
                dispatcher.utter_message("📅 Please, can you provide a valid date to analyze ASPI insights?")
                return []

            # Convert user input into datetime format
            try:
                user_date = datetime.strptime(user_date, "%Y-%m-%d")
            except ValueError:
                dispatcher.utter_message("⚠️ Date format is invalid. Can you use YYYY-MM-DD.")
                return []

            # Connect to ASPI database
            database_name = "aspi_database"
            mongo_uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{database_name}?retryWrites=true&w=majority"
            client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
            db = client[database_name]
            aspi_predictions_collection = db["aspi_data"]

            # Retrieve ASPI data for the given date
            predicted_data = aspi_predictions_collection.find_one({"Date": user_date})
            if not predicted_data:
                dispatcher.utter_message(f"⚠️ There's no ASPI data available for {user_date}.")
                return []

            # Retrieve previous day's ASPI for comparison
            previous_date = user_date - timedelta(days=1)
            previous_data = aspi_predictions_collection.find_one({"Date": previous_date})
            if not previous_data:
                dispatcher.utter_message(f"⚠️ I'm unable to retrieve data for {previous_date}, so trends may be incomplete.")

            # Extract ASPI values
            aspi_today = predicted_data.get("Predicted_Day_1")
            aspi_yesterday = previous_data.get("Predicted_Day_1") if previous_data else None

            if aspi_today is None:
                dispatcher.utter_message(f"⚠️ There's no predicted ASPI value found for {user_date}.")
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
            dispatcher.utter_message(f"📊 ASPI Analysis for {user_date}: The ASPI value for {user_date} is **{aspi_today:.2f}**. The market trend is **{momentum}** with **{strength}** momentum, indicating that the market is moving {momentum.lower()}. The ASPI has changed by **{daily_change:.2f} points**, which is a **{daily_change_pct:.2f}%** change from the previous day. The volatility level for {user_date} is **{daily_volatility:.2f} points**, based on the last five days of data. The support level is **{support_level:.2f}** and the resistance level is **{resistance_level:.2f}**, indicating the key price levels to watch. Based on the current ASPI value, there is a **{signal}**.")

        except Exception as e:
            print(f"❌ Error analyzing ASPI data: {e}")
            dispatcher.utter_message("⚠️ An error occurred while analyzing the ASPI data.")

        return []  
    
class ActionFallback(Action):
    def name(self) -> str:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_message = tracker.latest_message.get('text')
        response = self.get_mistral_response(user_message)
        dispatcher.utter_message(text=response)
        return []

    def get_mistral_response(self, user_message: str) -> str:
        API_KEY = "MkChCsEH6X7QUEYezIXrBj1czFAGsRQH" 
        API_URL = "https://api.mistral.ai/v1/chat/completions"
        
        data = {
            "model": "mistral-large-latest",  
            "messages": [{"role": "user", "content": user_message}],
            "max_tokens": 50,  
            "temperature": 0.8, 
        } 
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        } 
        
        try:
            response = requests.post(API_URL, json=data, headers=headers)
            response.raise_for_status()  
            response_json = response.json()

            # Check if response contains the expected 'response' key
            return response_json.get("response", self.get_random_fallback())
        except requests.exceptions.RequestException as e:
            # Handle network errors or bad responses
            return "Looks like I hit a roadblock! Try again?"
        except Exception as e:
            # Generic error handling
            return "That didn’t go as planned. Mind asking again?"