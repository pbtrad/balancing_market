import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model("ml_models/models/model.h5")


def predict(features):
    features = np.array(features).reshape(1, -1)
    prediction = model.predict(features)
    return prediction[0]
