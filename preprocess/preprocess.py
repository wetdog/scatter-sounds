import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import os
import json 
import argparse
from tqdm import tqdm
from utils import *

parser = argparse.ArgumentParser(description='Preprocess audio files for scatter sound viz')
parser.add_argument("-f","--file" ,type=str)
parser.add_argument("-d","--dir",type=str)
args = parser.parse_args()
output_path = "../data" 

if args.file:
    audio_file = args.file
    assert os.path.isfile(audio_file), "Invalid audio path"
    audio_name = os.path.basename(audio_file).split(".")[0]
    model_sample_rate = 16000
    x = load_audio_resample(audio_file,target_sr=model_sample_rate)

else:
    audio_file = "../city_sound.wav"
    # https://freesound.org/people/soundsofeurope/sounds/170862/
if args.dir:

    audio_folder = args.dir
    assert os.path.isdir(audio_folder), "Invalid audio folder"
    audio_name = os.path.basename(audio_folder)
    x = load_clips_from_folder(audio_folder,clip_dur=1,target_sr=16000)

# Load models from TF-hub
yamnet = hub.load('https://tfhub.dev/google/yamnet/1')
vggish = hub.load('https://tfhub.dev/google/vggish/1')


sprite_img_dim = 150
sprite_file = os.path.join(output_path,f"{audio_name}_sprite.jpg")
output_audiofile = os.path.join(output_path,f"{audio_name}.flac")
projections_file = os.path.join(output_path,"projections.json")
config_file = os.path.join(output_path,"config.json")

model_sample_rate = 16000
hop_size = 0.48
window_size = 0.96

# load audio 
# #x =  get_random_signal(n_seconds=4,sample_rate=sample_rate)

duration = x.shape[0] / model_sample_rate
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
projected_embeddings = reduce_dim(embeddings, method="UMAP")
norm_projected_embeddings = np.divide(projected_embeddings, projected_embeddings.max(axis=1).reshape(-1,1))
print(f"Projected embeddings shape {projected_embeddings.shape}")

# spherical projection
embedding_magnitude = np.sqrt(np.sum(np.power(norm_projected_embeddings,2),axis=1))
sphere_radius = 10
Q = sphere_radius/embedding_magnitude
spherical = np.multiply( Q.reshape(-1,1),norm_projected_embeddings)

start_seconds = [int(i*hop_size) for i in range(n_windows)]
end_seconds = [int((i*hop_size + window_size)) for i in range(n_windows)]
ids = [i for i in range(n_windows)]

json_dict = {"idx":ids,
            "start_seconds": start_seconds,
            "end_seconds":end_seconds,
            "projections":projected_embeddings.tolist(),
            "spherical":spherical.tolist()}

# write json file
with open(projections_file, "w") as json_file:
    json.dump(json_dict,json_file)

## spritesheet
# create sprite image
spriteimage = create_spritesheet(spectrograms,n_examples=embeddings.shape[0],img_dim=sprite_img_dim)
spriteimage.convert("RGB").save(sprite_file, transparency=0)

# write audio file
sf.write(file=output_audiofile, data=x, samplerate=model_sample_rate)

# write config file 
config_dict = {"audioFile":output_audiofile,
                "spriteFile":sprite_file,
                "imgDim":sprite_img_dim,
                "projectionsFile":projections_file}

with open(config_file, "w") as json_file:
    json.dump(config_dict,json_file)