import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(csv_path, output_path):
    df = pd.read_csv(csv_path)

    scaler = StandardScaler()
    df[df.columns] = scaler.fit_transform(df)

    df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")
