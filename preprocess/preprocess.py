import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import soundfile as sf
import resampy
import os
from sklearn.manifold import TSNE
import json 
import umap


# load audio 
audio_file = "../long_audio.wav"
assert os.path.isfile(audio_file), "Invalid audio path"

# Load models from TF-hub
yamnet = hub.load('https://tfhub.dev/google/yamnet/1')

def load_audio_16khz(audio_file):
    x, sample_rate = sf.read(audio_file)
    # check for mono file
    if len(x.shape) > 1:
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
hop_size = 0.48
window_size = 0.96
x =  get_random_signal(n_seconds=4,sample_rate=sample_rate)
#x = load_audio_16khz(audio_file)
duration = x.shape[0] / sample_rate
waveform = tf.Variable(x,dtype=tf.float32)
print(f"Audio shape: {waveform.shape}")
print(f"Audio duration: {duration} seconds")

# get embedding
scores, embeddings, spectrograms = yamnet(waveform)
n_windows = int(np.floor(duration/hop_size))
print(f"N windows = {n_windows}")
print(f"embedding shape: {embeddings.shape}")
print(f"Embedding duration: {duration / embeddings.shape[0]}")

# dimensionality reduction 
def reduce_dim(method="UMAP"):
    if method == "TSNE":
        tsne_reducer = TSNE(n_components=3)
        projected_embeddings = tsne_reducer.fit_transform(embeddings)
        return projected_embeddings

    elif method =="UMAP":
        umap_reducer = umap.UMAP(n_components=3)
        projected_embeddings = umap_reducer.fit_transform(embeddings)
        return projected_embeddings

projected_embeddings = reduce_dim(method="UMAP")

norm_projected_embeddings = projected_embeddings / projected_embeddings.max()

print(projected_embeddings.max())

print(f"Projected embeddings shape {projected_embeddings.shape}")

start_samples = [int(i*hop_size*sample_rate) for i in range(n_windows)]
end_samples = [int((i*hop_size + window_size)*sample_rate) for i in range(n_windows)]

json_dict = {"start_sample": start_samples,
            "end_sample":end_samples,
            "projections":projected_embeddings.tolist()}

with open("projections.json","w") as json_file:
    json.dump(json_dict,json_file)


