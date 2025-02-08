import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

dataset = tf.data.experimental.make_csv_dataset("ml_models/data/processed/training_data.csv", batch_size=32)

model = keras.Sequential([
    layers.Dense(64, activation="relu"),
    layers.Dense(32, activation="relu"),
    layers.Dense(1, activation="linear")
])

model.compile(optimizer="adam", loss="mse")

model.fit(dataset, epochs=10)

model.save("ml_models/models/model.h5")
print("Model saved!")
