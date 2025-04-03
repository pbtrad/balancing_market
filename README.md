# Balancing Market ML Project

**Overview**

This project aims to develop a machine learning pipeline for forecasting electricity demand and balancing market trends using EirGrid data. The system integrates real-time data scraping, historical data downloads, and ML model training for improved market predictions.

**Features**

* Real-Time Data Collection: Scrapes live market data from EirGrid’s Smart Grid Dashboard.

* Historical Data Processing: Downloads and cleans SEMO CSV files for model training.

**Machine Learning Models**

* Demand Forecasting: Predict future electricity demand.

* Market Price Prediction: Estimate balancing market prices.

* FastAPI Endpoint: Exposes trained models via API for predictions.

**Project Plan (Updated)**

* Automate the pipeline:

- EirGrid scraper runs every few minutes (lambdas)

- Raw data is saved to S3

- Data is ingested continuously  (more lambdas)

- The model trains and predicts regularly (e.g., daily)  (even more lambdas)

- Forecasts are stored in the database  (RDS)

- API can serve those forecasts to the frontend
