import tensorflow as tf
import pandas as pd
import os

RAW_PATH = os.path.join("/app", "ml_models", "data", "raw")
PROCESSED_PATH = os.path.join("/app", "ml_models", "data", "processed")

os.makedirs(RAW_PATH, exist_ok=True)
os.makedirs(PROCESSED_PATH, exist_ok=True)



def serialize_example(features, label):
    """Converts a single data row to TFRecord format."""
    feature_dict = {
        str(f): tf.train.Feature(float_list=tf.train.FloatList(value=[v]))
        for f, v in enumerate(features)
    }
    feature_dict["label"] = tf.train.Feature(
        float_list=tf.train.FloatList(value=[label])
    )
    example = tf.train.Example(features=tf.train.Features(feature=feature_dict))
    return example.SerializeToString()


def convert_csv_to_tfrecord(csv_filename, tfrecord_filename):
    """Converts a CSV file to a TFRecord file."""
    df = pd.read_csv(csv_filename)

    features = df.drop(columns=["target"]).values
    labels = df["target"].values

    with tf.io.TFRecordWriter(tfrecord_filename) as writer:
        for f, l in zip(features, labels):
            writer.write(serialize_example(f, l))

    print(f"Converted {csv_filename} to {tfrecord_filename}")


if __name__ == "__main__":
    for file in os.listdir(RAW_PATH):
        if file.endswith(".csv"):
            csv_file = os.path.join(RAW_PATH, file)
            tfrecord_file = os.path.join(
                PROCESSED_PATH, file.replace(".csv", ".tfrecord")
            )
            convert_csv_to_tfrecord(csv_file, tfrecord_file)
