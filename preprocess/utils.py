import numpy as np
import soundfile as sf
import resampy
import umap
from sklearn.manifold import TSNE
from PIL import Image
from matplotlib import cm

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


def reduce_dim(embeddings,method="UMAP"):
    if method == "TSNE":
        tsne_reducer = TSNE(n_components=3)
        projected_embeddings = tsne_reducer.fit_transform(embeddings)
        return projected_embeddings

    elif method =="UMAP":
        umap_reducer = umap.UMAP(n_components=3)
        projected_embeddings = umap_reducer.fit_transform(embeddings)
        return projected_embeddings


# vaporwave pallete
"""vaporwave": ["#94D0FF", "#8795E8", "#966bff", "#AD8CFF", "#C774E8",
 "#c774a9", "#FF6AD5", "#ff6a8b", "#ff8b8b", "#ffa58b", "#ffde8b", "#cdde8b", "#8bde8b", "#20de8b"],
"""
def create_spritesheet(spectrogram,n_examples,img_dim=50):

    if type(spectrogram).__name__ != 'ndarray':
        spectrogram = spectrogram.numpy()

    if len(spectrogram.shape) > 2:
        spectrogram = np.squeeze(spectrogram,axis=0)

    step = int(np.floor(spectrogram.shape[0] / n_examples))
    spectrogram = spectrogram[:,::-1]
    spectrogram_scaled = spectrogram + np.abs(np.min(spectrogram))
    spectrogram_scaled = spectrogram_scaled / spectrogram_scaled.max()

    images = [Image.fromarray((np.uint8(cm.plasma(spectrogram_scaled[i:i+step,:].T)*255))).resize(size=(img_dim,img_dim)) for i in range(0,spectrogram_scaled.shape[0],step)]

    image_width, image_height = images[0].size
    one_square_size = int(np.ceil(np.sqrt(len(images))))
    master_width = (image_width * one_square_size) 
    master_height = image_height * one_square_size
    spriteimage = Image.new(
        mode='RGBA',
        size=(master_width, master_height),
        color=(0,0,0,0))  # fully transparent
    for count, image in enumerate(images):
        div, mod = divmod(count,one_square_size)
        h_loc = image_width*div
        w_loc = image_width*mod    
        spriteimage.paste(image,(w_loc,h_loc))
    return spriteimage
