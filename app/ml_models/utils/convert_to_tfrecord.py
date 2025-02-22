import ast
import tensorflow as tf
import pandas as pd
import os
from app.utils.logging import logger

RAW_PATH = os.path.join("/app", "ml_models", "data", "raw")
PROCESSED_PATH = os.path.join("/app", "ml_models", "data", "processed")

os.makedirs(RAW_PATH, exist_ok=True)
os.makedirs(PROCESSED_PATH, exist_ok=True)


def convert_csv_to_tfrecord(csv_filename, tfrecord_filename):
    df = pd.read_csv(csv_filename)

    df["Value"] = df["Rows"].apply(
        lambda x: ast.literal_eval(x)["Value"] if pd.notnull(x) else 0
    )

    features = df[["Value"]].values
    labels = (df["Status"] == "Success").astype(int).values

    with tf.io.TFRecordWriter(tfrecord_filename) as writer:
        for f, l in zip(features, labels):
            writer.write(serialize_example(f, l))

    logger.info(f"Converted {csv_filename} to {tfrecord_filename}")


def serialize_example(feature, label):
    feature_dict = {
        "feature": tf.train.Feature(float_list=tf.train.FloatList(value=feature)),
        "label": tf.train.Feature(int64_list=tf.train.Int64List(value=[label])),
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature_dict))
    return example_proto.SerializeToString()


if __name__ == "__main__":
    for file in os.listdir(RAW_PATH):
        if file.endswith(".csv"):
            csv_file = os.path.join(RAW_PATH, file)
            tfrecord_file = os.path.join(
                PROCESSED_PATH, file.replace(".csv", ".tfrecord")
            )
            convert_csv_to_tfrecord(csv_file, tfrecord_file)
