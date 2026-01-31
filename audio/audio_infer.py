import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import librosa
import pandas as pd
import subprocess
import os
import sys

print("Recording audio...", flush=True)

subprocess.run(
    ["arecord", "-f", "S16_LE", "-r", "16000", "-c", "1", "-d", "3", "audio.wav"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print("Loading audio...", flush=True)
y, _ = librosa.load("audio.wav", sr=16000, mono=True)

print("Loading YAMNet...", flush=True)
yamnet = hub.load("https://tfhub.dev/google/yamnet/1")

print("Running inference...", flush=True)
scores, _, _ = yamnet(tf.convert_to_tensor(y, tf.float32))

labels_path = tf.keras.utils.get_file(
    "yamnet_class_map.csv",
    "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
)
labels = pd.read_csv(labels_path)["display_name"].tolist()

top = np.argmax(tf.reduce_mean(scores, axis=0))
print(labels[top], flush=True)
