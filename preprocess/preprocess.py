import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import os
import json 
import argparse
from utils import *

# model parameters
model_sample_rate = 16000
hop_size = 0.48
window_size = 0.96
# preprocess parameters
global_sr = 44100 # sample rate of all the audio clips
sprite_img_dim = 150
reduce_method = "UMAP"
# to split very large audios
chunk_size_seconds = 900
max_audio_duration = 3600
parse_label_fn = get_label_ub8k
label_list = ub8k_labels 

parser = argparse.ArgumentParser(description='Preprocess audio files for scatter sound viz')
parser.add_argument("-f","--file" ,type=str)
parser.add_argument("-d","--dir",type=str)
args = parser.parse_args()
output_path = "../data" 

if args.file:
    audio_file = args.file
    assert os.path.isfile(audio_file), "Invalid audio path"
    audio_name = os.path.basename(audio_file).split(".")[0]
    x = load_audio_resample(audio_file,target_sr=model_sample_rate)
    metadata = get_metadata(x,filename=audio_name,hop_size=hop_size,window_size=window_size,sr=model_sample_rate)
else:
    audio_file = "../city_sound.wav"
    # https://freesound.org/people/soundsofeurope/sounds/170862/

if args.dir:
    audio_folder = args.dir
    assert os.path.isdir(audio_folder), "Invalid audio folder"
    audio_name = os.path.basename(audio_folder)
    x, metadata = process_clips_from_folder(audio_folder,parse_label_fn,label_list,
                    clip_dur=window_size,global_sr=global_sr,target_sr=model_sample_rate)
# Load models from TF-hub
yamnet = hub.load('https://tfhub.dev/google/yamnet/1')
#vggish = hub.load('https://tfhub.dev/google/vggish/1')

# output filenames
sprite_file = os.path.join(output_path,f"{audio_name}_sprite.jpg")
output_audiofile = os.path.join(output_path,f"{audio_name}.flac")
projections_file = os.path.join(output_path,f"{audio_name}_projections.json")
config_file = os.path.join(output_path,f"{audio_name}_config.json")

duration = x.shape[0] / model_sample_rate
if duration < max_audio_duration:    
    waveform = tf.Variable(x,dtype=tf.float32)
    print(f"Audio shape: {waveform.shape}")
    print(f"Audio duration: {duration} seconds")
    # get embedding
    scores, embeddings, spectrograms = yamnet(waveform)

else:
    chunk_size_samples = int(model_sample_rate * chunk_size_seconds) # 900 seconds audio chunks
    n_chunks = int(np.ceil(len(x)/chunk_size_samples))
    if len(x) < n_chunks*chunk_size_samples:
        pad_array = np.zeros(n_chunks*chunk_size_samples - len(x))
        x = np.hstack([x,pad_array])
        print("signal pad")
    embeddings_list= []
    scores_list = []
    spectrograms_list = []
    print(f"Audio duration: {duration} seconds")

    for sample_start in np.arange(0,len(x)-chunk_size_samples,chunk_size_samples):
        waveform = x[sample_start:sample_start+chunk_size_samples]
        waveform = tf.Variable(waveform,dtype=tf.float32)
        print(f"Audio shape: {waveform.shape}")
        # get embedding
        temp_scores, temp_embeddings, temp_spectrograms = yamnet(waveform)
        embeddings_list.append(temp_embeddings)
        spectrograms_list.append(temp_spectrograms)
        scores_list.append(temp_scores)

    embeddings = tf.concat(embeddings_list,axis=0)
    spectrograms = tf.concat(spectrograms_list,axis=0)
    scores = tf.concat(scores_list,axis=0)

print(f"embedding shape: {embeddings.shape}")
if args.dir:
    # Get rid of half window embedding for 0.96 second clips
    embeddings = embeddings[::2,:]
    n_windows = int(np.floor(duration/window_size))
else:
    n_windows = int(np.floor(duration/hop_size))

print(f"N windows = {n_windows}")
print(f"embedding shape: {embeddings.shape}")
print(f"Embedding duration: {duration / embeddings.shape[0]}")

# dimensionality reduction 
projected_embeddings = reduce_dim(embeddings, method=reduce_method)
norm_projected_embeddings = np.divide(projected_embeddings, projected_embeddings.max(axis=1).reshape(-1,1))
print(f"Projected embeddings shape {projected_embeddings.shape}")

# spherical projection
embedding_magnitude = np.sqrt(np.sum(np.power(projected_embeddings,2),axis=1))
sphere_radius = 10
Q = sphere_radius/embedding_magnitude
spherical = np.multiply( Q.reshape(-1,1),projected_embeddings)


#####################################################
################# OUTPUT FILES ######################

json_dict = {"idx":[i for i in range(n_windows)],
            "metadata":metadata,
            "projections":projected_embeddings.tolist(),
            "spherical":spherical.tolist()}

# write json file
with open(projections_file, "w") as json_file:
    json.dump(json_dict,json_file)

# create sprite image
spriteimage = create_spritesheet(spectrograms,n_examples=embeddings.shape[0],img_dim=sprite_img_dim)
spriteimage.convert("RGB").save(sprite_file, transparency=0)

# write output flac audio file
sf.write(file=output_audiofile, data=x, samplerate=model_sample_rate)

# write config file 
config_dict = {"audioFile":output_audiofile[1:],
                "spriteFile":sprite_file[1:],
                "projectionsFile":projections_file[1:],
                "imgDim":sprite_img_dim}

with open(config_file, "w") as json_file:
    json.dump(config_dict,json_file)