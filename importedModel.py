from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load the trained model
model = joblib.load('aspi_forecast_model.pkl')

# Endpoint for prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get input data as JSON
    data = request.get_json()

    # Convert the input JSON data to a DataFrame (if necessary)
    input_df = pd.DataFrame([data])

    # Ensure the input data has the same columns as the model's features
    # Ensure you remove 'Date' and any other non-feature columns (like target columns)
    features = input_df.drop(columns=['Date'])  # Adjust if you have other columns to drop

    # Make predictions using the trained model
    prediction = model.predict(features)

    # Convert the prediction to a list or array and send it back
    prediction = prediction.tolist()

    return jsonify({'predictions': prediction})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
