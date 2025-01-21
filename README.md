Sentiment Analysis for the Colombo Stock Exchange (CSE)

Project Overview

This component of the project focuses on analyzing the sentiment of Sinhala news articles to study their influence on stock price movements in the Colombo Stock Exchange (CSE). Given that most Sri Lankan news and investors are Sinhala-speaking, this analysis aims to capture potential sentiment-driven impacts on stock prices, particularly the All Share Price Index (ASPI).

Dataset

Source: A dataset containing approximately 50,000 Sinhala news articles over a span of three years.
Features: Each news article includes attributes such as publication date, title, and sentiment score.
Preprocessing: Sentiments were derived from the text using a pretrained SinBERT model, fine-tuned with a labeled dataset for improved accuracy.
Methodology

Model:
The SinBERT pretrained model was fine-tuned using a labeled sentiment dataset.
The fine-tuned model assigns sentiments to news articles as positive, neutral, or negative.
Sentiment Scoring:
Sentiments were quantified using a grid search method to determine optimal weights for sentiment influence.
Sentiment scores were correlated with percentage changes in ASPI values.
Analysis Levels:
Daily Analysis: Calculating daily sentiment scores and their relationship with daily ASPI changes.
Weekly Analysis: Aggregating sentiment scores weekly to study their relationship with ASPI changes over a broader period.
