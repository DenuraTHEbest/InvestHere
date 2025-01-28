from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
import requests  # Assuming the model is accessible via an API

class ActionGetBuySellSignals(Action):
    def name(self) -> str:
        return "action_get_buy_sell_signals"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # Call the prediction model (mocked for now)
        try:
            # Example: Replace this with an API call or model function
            response = requests.get("http://localhost:5000/get_buy_sell_signals")
            if response.status_code == 200:
                signals = response.json()  # Assuming the API returns JSON
                buy_stocks = signals.get("buy", [])
                sell_stocks = signals.get("sell", [])
                message = f"📈 Buy: {', '.join(buy_stocks)}\n📉 Sell: {', '.join(sell_stocks)}"
            else:
                message = "Sorry, I couldn't fetch the buy/sell signals right now. Please try again later."
        except Exception as e:
            message = f"An error occurred: {str(e)}"
        
        dispatcher.utter_message(text=message)
        return []


class ActionGetMarketSentiment(Action):
    def name(self) -> str:
        return "action_get_market_sentiment"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        try:
            # Replace this with actual API/model integration
            response = requests.get("http://localhost:5000/get_market_sentiment")
            if response.status_code == 200:
                sentiment_data = response.json()
                sentiment = sentiment_data.get("sentiment", "neutral")
                key_factors = sentiment_data.get("factors", [])
                message = f"📊 Current market sentiment is '{sentiment}'.\n\nKey factors:\n- " + "\n- ".join(key_factors)
            else:
                message = "Sorry, I couldn't fetch the market sentiment at the moment. Please try again later."
        except Exception as e:
            message = f"An error occurred: {str(e)}"
        
        dispatcher.utter_message(text=message)
        return []
    

class ActionAnalyzeScenario(Action):
    def name(self) -> str:
        return "action_analyze_scenario"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # Extract user inputs from slots
        sector = tracker.get_slot("sector")
        percentage = tracker.get_slot("percentage")
        direction = tracker.get_slot("direction")

        # Mocked response logic
        if sector and percentage and direction:
            if direction == "increase":
                impact = f"If the {sector} sector increases by {percentage}%, your portfolio value might rise proportionally depending on exposure."
            elif direction == "decrease":
                impact = f"If the {sector} sector decreases by {percentage}%, there could be a decline in your portfolio's value."
            else:
                impact = "I'm unsure about the direction of change."
        else:
            impact = "Please provide a valid sector, percentage, and direction."

        dispatcher.utter_message(text=impact)
        return []
    

class ActionGetDailySummary(Action):
    def name(self) -> str:
        return "action_get_daily_summary"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        try:
            # Example: Replace this with real API or model integration
            daily_summary = {
                "aspi_movement": "+1.5%",
                "top_sectors": ["Technology", "Energy", "Finance"],
                "opportunities": ["AAPL (Buy)", "GOOGL (Buy)", "AMZN (Hold)"]
            }

            message = (
                f"📊 **Daily Market Summary**:\n"
                f"- ASPI Movement: {daily_summary['aspi_movement']}\n"
                f"- Top Performing Sectors: {', '.join(daily_summary['top_sectors'])}\n"
                f"- Opportunities:\n  • {', '.join(daily_summary['opportunities'])}"
            )
        except Exception as e:
            message = f"An error occurred while fetching the daily report: {str(e)}"

        dispatcher.utter_message(text=message)
        return []





















































# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
