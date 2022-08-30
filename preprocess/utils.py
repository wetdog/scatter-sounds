import numpy as np
import soundfile as sf
import resampy
import umap
from sklearn.manifold import TSNE


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

def get_random_signal(n_seconds,sample_rate):
    return np.random.rand(sample_rate*n_seconds)


def reduce_dim(method="UMAP"):
    if method == "TSNE":
        tsne_reducer = TSNE(n_components=3)
        projected_embeddings = tsne_reducer.fit_transform(embeddings)
        return projected_embeddings

    elif method =="UMAP":
        umap_reducer = umap.UMAP(n_components=3)
        projected_embeddings = umap_reducer.fit_transform(embeddings)
        return projected_embeddings