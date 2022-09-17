# scatter-sounds

This a web visualization and listening project based on scatter-gl, web-audio and tensorflow-hub AI sound models. Most of the time sound datasets are explored visually mainly through spectrograms or other time-frequency representation. This is an effort to show how fast you can overview a dataset through hearing it ordered in a similarity space. 

Python preprocessing scripts are provided to handle single long audios, or datasets of sound clips that are stored in a single folder like ESC-50 or urbansound8k. The model used to generate the similarity space is [YAMNet](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet) which is easily aviable throug the [tensorflow-hub](https://tfhub.dev/google/yamnet/1) repository.

## Usage 

The wepbage need 4 files to render the sound dataset.

* **config.json:** Store metadata of the dataset and paths to the data files.
* **projections.json:** Store the 3d projections of the YAMNet embeddings, labels and other useful metadata of the dataset. 
* **sprite.jpg:** The spritesheet image of log-melspectrograms that uses the YAMNet model for each clip of the dataset.
* **audio.flac:** The "spriteclip" audio with all the dataset clips merged.

### Data preprocessing

The python preprocessing script would receive as input a path to a folder that contains audio clips, or a path to a long audio file. 

For the dataset case that has clips on a folder(Eg. Esc50, UB8k), you will run:

```cd preprocess 
python preprocess.py -d <path_to_audio_folder>```

This would try to:
1. Load all the audios in the folder
2. Extract a clip region around the signal maximum amplitude of 0.96 seconds(YAMNet window analysis size). If the clip has a duration less than 0.96 seconds it would be padded with zeros.
3. Merge all trimmed clips, and resample the merged audio to the expected model sample rate(16Khz).
4. Get the the YAMNet embeddings and Log-melspectrogram of the merged signal.
5. Compute audio descriptors and parse labels from clip filenames for the metadata.
6. Reduce the dimensionality of the YAMNet emb(1024) to 3 components.
7. Generate the spritesheet image, the sprite clip, and the projections file. 




