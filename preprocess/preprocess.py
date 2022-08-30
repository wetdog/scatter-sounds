import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import soundfile as sf
import resampy
import os
from sklearn.manifold import TSNE
import json 
import umap
from PIL import Image
from matplotlib import cm

from utils import *

# load audio 
audio_file = "../long_audio.wav"
audio_name = os.path.basename(audio_file).split(".")[0]
assert os.path.isfile(audio_file), "Invalid audio path"

# Load models from TF-hub
yamnet = hub.load('https://tfhub.dev/google/yamnet/1')

sample_rate = 16000
hop_size = 0.48
window_size = 0.96

#x =  get_random_signal(n_seconds=4,sample_rate=sample_rate)
x = load_audio_16khz(audio_file)
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

projected_embeddings = reduce_dim(method="UMAP")
norm_projected_embeddings = projected_embeddings / projected_embeddings.max()

print(projected_embeddings.max())
print(f"Projected embeddings shape {projected_embeddings.shape}")

start_samples = [int(i*hop_size*sample_rate) for i in range(n_windows)]
end_samples = [int((i*hop_size + window_size)*sample_rate) for i in range(n_windows)]
ids = [i for i in range(n_windows)]

json_dict = {"idx":ids,
            "start_sample": start_samples,
            "end_sample":end_samples,
            "projections":projected_embeddings.tolist()}

with open("projections.json","w") as json_file:
    json.dump(json_dict,json_file)


## spritesheet

# create sprite image
if type(spectrograms).__name__ != 'ndarray':
  spectrograms = spectrograms.numpy()

if len(spectrograms.shape) > 2:
  spectrograms = np.squeeze(spectrograms,axis=0)

img_dim = 150
step = int(np.floor(spectrograms.shape[0] / embeddings.shape[0]))
spectrograms = spectrograms[:,::-1]
spectrograms_scaled = spectrograms + np.abs(np.min(spectrograms))
spectrograms_scaled = spectrograms_scaled / spectrograms_scaled.max()

images = [Image.fromarray((np.uint8(cm.viridis(spectrograms_scaled[i:i+step,:].T)*255))).resize(size=(img_dim,img_dim)) for i in range(0,spectrograms_scaled.shape[0],step)]

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

sprite_file = f"{audio_name}_sprite.jpg"
spriteimage.convert("RGB").save(sprite_file, transparency=0)