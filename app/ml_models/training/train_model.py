import tensorflow as tf
import argparse
import os
from tensorflow.python import keras
from tensorflow.python.keras import layers
from app.utils.logging import logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    # Load data from the SageMaker training channel
    train_data_path = os.environ.get("SM_CHANNEL_TRAINING")
    if not train_data_path:
        raise ValueError("SM_CHANNEL_TRAINING environment variable is not set.")

    dataset = tf.data.experimental.make_csv_dataset(
        os.path.join(train_data_path, "training_data.csv"), batch_size=args.batch_size
    )

    # Define the neural network model
    model = keras.Sequential(
        [
            layers.Dense(64, activation="relu"),
            layers.Dense(32, activation="relu"),
            layers.Dense(1, activation="linear"),
        ]
    )
    model.compile(optimizer="adam", loss="mse")

    # Train the model
    model.fit(dataset, epochs=args.epochs)

    # Save the model to the SageMaker model directory
    model_dir = "/opt/ml/model"
    model.save(model_dir)
    logger.info(f"Model saved to {model_dir}")


if __name__ == "__main__":
    main()
