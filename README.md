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

**Project Plan(so far)**

Data Collection and Preprocessing: Scrape real-time market data, automate CSV downloads, develop preprocessing scripts

Model Development: Train demand forecasting model, train market price prediction model, evaluate models

API Integration and Deployment: Deploy models via FastAPI, set up Docker, expose endpoints for predictions

**AWS Plan**

Either preprocess data locally or with a SageMaker processing job.

Upload processed data to S3.

Start a SageMaker training job, pointing it to the data in S3.

Deploy the trained model on SageMaker for inference.

**Infrastructure as Code**

Networking: VPC, subnets, security groups etc

Database: RDS instance (postgres), will need read replica if I decide to use Grafana.

Storage: S3 buckets (S3 Glacier for archiving).

Containers: ECS (docker etc).

Machine Learning: SageMaker for training and deploying models.

Logging: CloudWatch.
