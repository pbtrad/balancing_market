import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

RAW_PATH = "app/ml_models/data/raw"
PROCESSED_PATH = "app/ml_models/data/processed"
os.makedirs(PROCESSED_PATH, exist_ok=True)


def preprocess_data(csv_path, output_path):
    df = pd.read_csv(csv_path)

    scaler = StandardScaler()
    df[df.columns] = scaler.fit_transform(df)

    df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")


if __name__ == "__main__":
    for file_name in os.listdir(RAW_PATH):
        raw_file = os.path.join(RAW_PATH, file_name)
        processed_file = os.path.join(PROCESSED_PATH, file_name)

        print(f"Preprocessing {raw_file}...")
        preprocess_data(raw_file, processed_file)
