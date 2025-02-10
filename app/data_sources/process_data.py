import os

from ml_models.utils.data_preprocessing import preprocess_data

RAW_PATH = "ml_models/data/raw"
CLEANED_PATH = "ml_models/data/cleaned"
PROCESSED_PATH = "ml_models/data/processed"

os.makedirs(CLEANED_PATH, exist_ok=True)
os.makedirs(PROCESSED_PATH, exist_ok=True)


def clean_data(input_csv, output_csv):
    import pandas as pd

    df = pd.read_csv(input_csv)

    df = df.drop_duplicates()
    df.fillna(df.median(), inplace=True)
    df.to_csv(output_csv, index=False)
    print(f"Cleaned data saved to {output_csv}")


def main():
    for filename in os.listdir(RAW_PATH):
        if filename.endswith(".csv"):
            raw_file = os.path.join(RAW_PATH, filename)
            cleaned_file = os.path.join(CLEANED_PATH, filename)
            processed_file = os.path.join(PROCESSED_PATH, filename)

            clean_data(raw_file, cleaned_file)

            preprocess_data(cleaned_file, processed_file)

            print(f"Processed data saved to {processed_file}")


if __name__ == "__main__":
    main()
