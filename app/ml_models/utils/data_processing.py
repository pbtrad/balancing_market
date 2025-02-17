import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from app.utils.logging import logger

RAW_PATH = "app/ml_models/data/raw"
CLEANED_PATH = "app/ml_models/data/cleaned"
PROCESSED_PATH = "app/ml_models/data/processed"

os.makedirs(CLEANED_PATH, exist_ok=True)
os.makedirs(PROCESSED_PATH, exist_ok=True)


# Clean raw data by removing duplicates and filling missing values.
def clean_data(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df = df.drop_duplicates()
    df.fillna(df.median(), inplace=True)

    df.to_csv(output_csv, index=False)
    logger.info(f"Cleaned data saved to {output_csv}")


# Preprocesses data by scaling all numeric columns
def preprocess_data(csv_path, output_path):
    df = pd.read_csv(csv_path)

    scaler = StandardScaler()
    df[df.columns] = scaler.fit_transform(df)

    df.to_csv(output_path, index=False)
    logger.info(f"Processed data saved to {output_path}")


def main():
    for filename in os.listdir(RAW_PATH):
        if filename.endswith(".csv"):
            raw_file = os.path.join(RAW_PATH, filename)
            cleaned_file = os.path.join(CLEANED_PATH, filename)
            processed_file = os.path.join(PROCESSED_PATH, filename)

            logger.info(f"Processing file: {raw_file}")

            clean_data(raw_file, cleaned_file)

            preprocess_data(cleaned_file, processed_file)

            logger.info(f"Completed processing for: {filename}\n")


if __name__ == "__main__":
    main()
