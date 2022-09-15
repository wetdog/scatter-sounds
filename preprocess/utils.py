import numpy as np
import soundfile as sf
import resampy
import umap
from sklearn.manifold import TSNE
from PIL import Image
from matplotlib import cm
from matplotlib.colors import ListedColormap
import os
from tqdm import tqdm
import librosa


def load_audio_resample(audio_file: str, target_sr:int=16000):
    """Load wav file and resample to a target frequency
        returns mono resampled signal"""

    x, sample_rate = sf.read(audio_file)
    # check for mono file
    if len(x.shape) > 1:
        x = x.mean(axis=1)
    # check sample rate of audio
    if sample_rate != target_sr:
        x = resampy.resample(x,sample_rate,target_sr)
    return x


def get_metadata(x, hop_size:float=0.48, window_size:float=0.96,sr:int=16000):
    """Get predefined audio descriptors from a signal
        returns dictionary as metadata
    """

    window_size_samples = int(window_size*sr)
    hop_size_samples = int(hop_size*sr)
    metadata_dict = {
    "labels" : [],
    "filenames": [],
    "s_centroid": [],
    "s_rolloff": [],
    "s_bandwidth": [],
        }

    for fstart in range(0,len(x)-window_size_samples,hop_size_samples):
        frame = x[fstart:fstart+window_size_samples]
        
        spectral_centroid = librosa.feature.spectral_centroid(y=frame, sr=sr)
        spectral_rolloff =  librosa.feature.spectral_rolloff(y=frame, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=frame, sr=sr)  
        start_time = fstart/sr
        metadata_dict["filenames"].append(f"{start_time:.2f}")
        metadata_dict["s_centroid"].append(np.round(np.mean(spectral_centroid),2))
        metadata_dict["s_rolloff"].append(np.round(np.mean(spectral_rolloff),2))
        metadata_dict["s_bandwidth"].append(np.round(np.mean(spectral_bandwidth),2)) 
    
    return metadata_dict

def get_label_ub8k(filename):
    """get label from ub8k dataset"""
    return filename.split(".")[0].split("-")[1]

def get_label_esc50(filename):
    """get label from esc-50 dataset"""
    return filename.split(".")[0].split("-")[1]

def process_clips_from_folder(audio_folder: str,clip_dur: float=0.96,global_sr:float=44100,target_sr: int=16000):
    """ Process audio clips inside a folder to extract equal size fragments,
        and build a metadata dictionary with audio descriptors, labels and filenames """

    audio_files = [os.path.join(audio_folder,f) for f in os.listdir(audio_folder) if f.endswith("wav")]
    clip_list = []
    metadata_dict = {
        "labels" : [],
        "filenames": [],
        "s_centroid": [],
        "s_rolloff": [],
        "s_bandwidth": [],
        "labelnames":[]
    }
    ub8k_labels = ["air_conditioner","car_horn","children_playing","dog_bark","drilling",
                    "engine_idling","gun_shot","jackhammer","siren","street_music"]

    for audio in tqdm(audio_files):
        x, fs = sf.read(audio)
        if len(x.shape) > 1:
            x = x.mean(axis=1)
        if fs != global_sr:
            x = resampy.resample(x,sr_new=global_sr,sr_orig=fs)
            fs = global_sr

        segment = get_clip_selection(x,fs=fs,clip_dur=clip_dur)
        spectral_centroid = librosa.feature.spectral_centroid(y=segment, sr=fs)
        spectral_rolloff =  librosa.feature.spectral_rolloff(y=segment, sr=fs)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=segment, sr=fs)
        clip_list.append(segment)

        # metadata
        filename = os.path.basename(audio)
        label = get_label_ub8k(filename)
        metadata_dict["filenames"].append(filename)
        metadata_dict["labels"].append(label)
        metadata_dict["labelnames"].append(ub8k_labels[int(label)])
        metadata_dict["s_centroid"].append(np.round(np.mean(spectral_centroid),2))
        metadata_dict["s_rolloff"].append(np.round(np.mean(spectral_rolloff),2))
        metadata_dict["s_bandwidth"].append(np.round(np.mean(spectral_bandwidth),2))


    flat_list = [sample for clip in clip_list for sample in clip]
    x = np.asarray(flat_list)
    merged_audio = resampy.resample(x,global_sr,target_sr)
    return merged_audio,metadata_dict


def get_clip_selection(x,fs,clip_dur:float=0.96):
    """ Select a region of a defined duration in seconds around the signal maximum"""
    clip_dur_samples = int(clip_dur*fs)
    if len(x) < clip_dur_samples:
      pad_array = np.zeros(clip_dur_samples - len(x))
      x = np.hstack([x,pad_array])
    idx_max = np.argmax(x)
    start = int(idx_max - clip_dur_samples/2)
    end = int(idx_max + clip_dur_samples/2)
    if end > (len(x)):
        end = len(x)
        start = int(end - (clip_dur_samples))
    if start < 0:
        start = 0
        end = clip_dur_samples
    selection = x[start:end]
    return selection


def reduce_dim(embeddings,method: str="UMAP"):
    """reduce the Dimensionality of the Yamnet embeddings"""
    if method == "TSNE":
        tsne_reducer = TSNE(n_components=3)
        projected_embeddings = tsne_reducer.fit_transform(embeddings)
        return projected_embeddings

    elif method =="UMAP":
        umap_reducer = umap.UMAP(n_components=3,
                                n_neighbors=15,
                                metric="minkowski")
        projected_embeddings = umap_reducer.fit_transform(embeddings)
        return projected_embeddings


def create_spritesheet(spectrogram,n_examples:int,img_dim:int=50):
    """Create spritesheet from the mel-spectrogram computed by the yamnet model"""

    # new cmap
    vaporwave= ["#94D0FF", "#8795E8", "#966bff", "#AD8CFF", "#C774E8",
    "#c774a9", "#FF6AD5", "#ff6a8b", "#ff8b8b", "#ffa58b", "#ffde8b",
     "#cdde8b", "#8bde8b", "#20de8b"]
    vpcmap = ListedColormap(vaporwave)

    if type(spectrogram).__name__ != 'ndarray':
        spectrogram = spectrogram.numpy()

    if len(spectrogram.shape) > 2:
        spectrogram = np.squeeze(spectrogram,axis=0)

    step = int(np.floor(spectrogram.shape[0] / n_examples))
    spectrogram = spectrogram[:,::-1]
    spectrogram_scaled = spectrogram + np.abs(np.min(spectrogram))
    spectrogram_scaled = spectrogram_scaled / spectrogram_scaled.max()

    images = [Image.fromarray((np.uint8(vpcmap(spectrogram_scaled[i:i+step,:].T)*255))).resize(size=(img_dim,img_dim)) for i in range(0,spectrogram_scaled.shape[0],step)]

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
