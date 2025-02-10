import os
from tensorflow.python import keras

import numpy as np

MODEL_PATH = os.path.join("/app", "ml_models", "models", "model.h5")
model = keras.models.load_model(MODEL_PATH)


def predict(features):
    features = np.array(features).reshape(1, -1)
    prediction = model.predict(features)
    return prediction[0]
