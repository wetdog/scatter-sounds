import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import soundfile as sf
import resampy
import os
from sklearn.manifold import TSNE
import json 


# load audio 

audio_file = "../long_audio.wav"
assert os.path.isfile(audio_file), "Invalid audio path"

# Load models from TF-hub
yamnet = hub.load('https://tfhub.dev/google/yamnet/1')

def load_audio_16khz(audio_file):
    x, sample_rate = sf.read(audio_file)
    # check for mono file
    if x.shape[1] > 1:
        x = x.mean(axis=1)
    # check sample rate of audio
    if sample_rate != 16000:
        x = resampy.resample(x,sample_rate,16000)
        sample_rate = 16000
    return x

#waveform = tf.Variable(x,dtype=tf.float32)
def get_random_signal(n_seconds,sample_rate):
    return np.random.rand(sample_rate*n_seconds)

sample_rate = 16000
x =  get_random_signal(n_seconds=40,sample_rate=sample_rate)
duration = x.shape[0] / sample_rate

waveform = tf.Variable(x,dtype=tf.float32)
print(f"Audio shape: {waveform.shape}")
print(f"Audio duration: {duration} seconds")

# get embedding
scores, embeddings, spectrograms = yamnet(waveform)

print(f"embedding shape: {embeddings.shape}")
print(f"Embedding duration: {duration / embeddings.shape[0]}")

# dimensionality reduction 

tsne = TSNE(n_components=3)
projected_embeddings = tsne.fit_transform(embeddings)

print(f"Projected embeddings shape {projected_embeddings.shape}")

with open("projections.json","w") as json_file:
    json.dump({"projections":list(projected_embeddings)},json_file)
