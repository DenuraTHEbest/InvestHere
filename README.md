# ASPI Prediction Component

This component focuses on predicting the All Share Price Index (ASPI) of the Colombo Stock Exchange (CSE). We employ a comparative modeling approach, evaluating several time series and machine learning models to achieve the most accurate predictions.

## Methodology

We explore various models for ASPI prediction, including:

*   **Classical Time Series Models:**
    *   ARIMA (Autoregressive Integrated Moving Average)
    *   SARIMA (Seasonal ARIMA)
*   **Machine Learning Models:**
    *   Linear Regression
    *   Gradient Boosting (e.g., XGBoost, LightGBM)
    *   Random Forest
    *   Neural Networks (e.g., Recurrent Neural Networks - RNNs, LSTMs)

Our methodology includes:

*   **Data Preprocessing:** Cleaning, transforming, and preparing the ASPI historical data.
*   **Feature Engineering:** Creating relevant features, potentially including technical indicators and lagged values.
*   **Sentiment Integration:** This model is built upon sentiment scores derived from a separate sentiment analysis component. These scores are incorporated as features to capture the impact of news sentiment on the ASPI.
*   **Model Training and Evaluation:** Training each model on historical data and evaluating their performance using appropriate metrics such as:
    *   Mean Absolute Error (MAE)
    *   Root Mean Squared Error (RMSE)
    *   R-squared (R²) - used to assess the goodness of fit of the models.
    *   Accuracy (for directional prediction)
*   **Validation:** Implementing time series cross-validation techniques (e.g., rolling window cross-validation) to ensure robust model evaluation.
*   **Model Comparison:** Comparing the performance of different models to select the best performing one.
*   **Testing:** Rigorous testing is carried out on the selected model to ensure its reliability and accuracy.

## Output

The output of this component includes:

*   **ASPI Value Prediction:** Predicted ASPI values for the next month (1-30 days).
*   **Directional Prediction:** Predicted direction of ASPI movement (upward or downward trend).
*   **Model Performance Metrics:** Evaluation metrics for each model, allowing for comparison and selection of the best model.

## Current Status

Work in progress. Currently, we are:

*   Experimenting with different model architectures and hyperparameters.
*   Refining the feature engineering process.
*   Conducting rigorous validation tests.

## Future Work

*   Explore more advanced time series models (e.g., Prophet).
*   Contribute to the implimentation of a comprehensive system with a UI.
*   Commercialization of the solution
*   Incorporate external factors (e.g., economic indicators, global market trends).
*   Develop a more robust and automated prediction pipeline.
