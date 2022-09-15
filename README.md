# scatter-sounds

This a web visualization and listening project based on scatter-gl, web-audio and tensorflow-hub AI sound models. Most of the time sound datasets are explored visually mainly through spectrograms or other time-frequency representation. This is an effort to show how fast you can overview a dataset through hearing it ordered in a similarity space. 

Python preprocessing scripts are provided to handle single long audios, or datasets of sound clips that are stored in a single folder like ESC-50 or urbansound8k. The model used to generate the similarity space is [YAMNet](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet) which is easily aviable throug the [tensorflow-hub](https://tfhub.dev/google/yamnet/1) repository.
