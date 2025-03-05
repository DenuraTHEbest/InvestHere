from statistics import stdev
import requests
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

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
        # Example predicted ASPI values (can be replaced with real prediction logic)
        predicted_aspi = [9000, 9100, 9200, 9300, 9400, 9350, 9450]

        # Calculate trend (simple: check if last value is higher than the first)
        trend = "increase" if predicted_aspi[-1] > predicted_aspi[0] else "decrease"
        
        # Calculate volatility (standard deviation)
        volatility = stdev(predicted_aspi)
        
        # Calculate week-over-week percentage change
        week_change = (predicted_aspi[-1] - predicted_aspi[0]) / predicted_aspi[0] * 100
        
        # Mean ASPI prediction for the week
        avg_aspi = torch.mean(torch.tensor(predicted_aspi, dtype=torch.float))

        # Generate insights for the user
        dispatcher.utter_message(f"Based on the predictions for the next week, the ASPI is expected to {trend}.")
        dispatcher.utter_message(f"The average predicted ASPI value is {avg_aspi:.2f}.")
        dispatcher.utter_message(f"The market is predicted to fluctuate with a volatility of {volatility:.2f} points.")
        dispatcher.utter_message(f"Comparing to the start of the week, the ASPI is predicted to change by {week_change:.2f}%.")
        
        # Reset the slot after the analysis is done
        return []