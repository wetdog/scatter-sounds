let prjName = "fold2";
let configUrl = `./data/${prjName}_config.json`;
let dataUrl, audioUrl, spriteUrl
let hopSize = 0.96; //"all embeddings 0.48,on clip project change to 0.96
let windowSize = 0.96; // clip duration
let nLabels = 10; // for color mapping
const nLoops = 4;

let bufferData = null;
let dataProj;
let configData;

const context = new (window.AudioContext || window.webkitAudioContext)();
const containerElement = document.getElementById('container');
const messagesElement = document.getElementById('messages');

const setMessage = (message) => {
  const messageStr = `🔥 ${message}`;
  messagesElement.innerHTML = messageStr;
}; 

fetch(configUrl)
    .then(function(resp) {
        return resp.json(); 
    })
    .then(function(data){        
        configData = data;
        dataUrl = configData.projectionsFile;
        audioUrl = configData.audioFile;
        spriteUrl = configData.spriteFile;
        console.log(`Audio ${audioUrl} data ${dataUrl} Sprite ${spriteUrl}`);
        loadSoundfetch(context,audioUrl);
        })
        .then(()=>{
            console.log("Config loaded");
            fetch(dataUrl)
            .then(function(resp) {
                return resp.json(); 
            })
            .then(function(data){        
                return data;
            })
            .then((dataArray)=>{
                console.log("data loaded");
                dataProj = dataArray;
                return scatterGL = renderDataset(dataArray);})
        })

// **************** Web audio *****************

async function loadSoundfetch(audioContext, url){              
    try {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        bufferData = audioBuffer;
        // Debug message
        document.getElementById('msg').textContent = `Duration: ${audioBuffer.duration}
          Vector Length: ${audioBuffer.length} 
          Sample rate: ${audioBuffer.sampleRate} 
          Number of channels: ${audioBuffer.numberOfChannels}`;
        alert("Sound loaded");
    } catch (error) {
        console.log(`Error: ${error}`);
    }
    };

function projectSpherical(array,sphereRadius=2){
    let Q;
    let magnitude;
    let projections = [];

    for (let n = 0; n < array.length; n++){
        Q = 0;
        magnitude = 0;
        for (let dim =0; dim < array[n].length; dim ++){
            magnitude += array[n][dim]**2;
        }
        Q = sphereRadius/magnitude**(0.5);
        let tempPoint = [];
        for (let dim =0; dim < array[n].length; dim ++){
            tempPoint.push(array[n][dim] * Q);
        }
        projections.push(tempPoint);

    }
    return projections;
}

function playSounds(buffer,point,typeCall){
    if(point){ 
        const now = context.currentTime;
        const source = new AudioBufferSourceNode(context);
        const amp = new GainNode(context);
        // Create a stereo panner
        const panNode = context.createStereoPanner();

        document.addEventListener('mousemove', (event) => {
            let panValue = 2*(event.clientX / screen.width) - 1;
            panNode.pan.setValueAtTime(panValue, context.currentTime)
        });
        
        source.connect(amp)
            .connect(panNode)
            .connect(context.destination);
        source.buffer = buffer;

        if (typeCall === "on-hoover"){
            source.start(now,point*hopSize);
            source.stop(now + windowSize);
        }
        if (typeCall === "on-click"){
            source.loop = true;
            source.loopStart = point*hopSize;
            source.loopEnd =  point*hopSize + windowSize;
            source.start(now,point*hopSize);
            source.stop(now + windowSize*nLoops);
        }
    }
};

function play3dSounds(buffer,points){
    if(points){ 
        const now = context.currentTime;
        const source = new AudioBufferSourceNode(context);
        const amp = new GainNode(context);
        // Create a stereo panner
        const pan3dNode = context.createPanner();
        pan3dNode.
        document.addEventListener('mousemove', (event) => {
            let panValue = 2*(event.clientX / screen.width) - 1;
            panNode.pan.setValueAtTime(panValue, context.currentTime)
        });
        
        source.connect(amp)
            .connect(pan3dNode)
            .connect(context.destination);
        source.buffer = buffer;
        source.loop = true;
        source.loopStart = point*hopSize;
        source.loopEnd =  point*hopSize + windowSize;
        source.start(now,point*hopSize);
        source.stop(now + windowSize*nLoops);
        }
    }

function renderDataset(dataArray){
    const dataset = new ScatterGL.Dataset(dataArray.projections,dataArray.metadata);
    dataset.setSpriteMetadata({
        spriteImage: spriteUrl,
        singleSpriteSize: [150, 150],
      });
    const scatterGL = new ScatterGL(containerElement,{
        //play clip on loop
        onClick: (point) => {playSounds(bufferData,point,"on-click");
                            if(point){
                                setMessage(`playing on loop ${nLoops} times \n
                                Filenames: ${dataset.metadata["filenames"][point]}`);
                                }
                            },
        // play clip
        onHover: (point) => {playSounds(bufferData,point,"on-hoover");
                            if(point){
                                let msg = `filename: ${dataset.metadata["filenames"][point]},
                                            spectral centroid: ${dataset.metadata["s_centroid"][point]},
                                            spectral rolloff: ${dataset.metadata["s_rolloff"][point]},
                                            spectral bandwidth: ${dataset.metadata["s_bandwidth"][point]}
                                            label: ${dataset.metadata["labelnames"][point]}`;

                                setMessage(msg);
                                }
                            },
        // play random selected clip on loop
        onSelect: (points) => {
                            randIdx = Math.floor(Math.random()*points.length);
                            playSounds(bufferData,points[randIdx],"on-click");
                            },
        styles: {
            backgroundColor: '#fffb96',
            axesVisible: false,
            fog: {
                color: '#ffffff',
                enabled: false,
                threshold: 15000,
              },
            point: {
                colorUnselected: 'rgba(227, 227, 227)',
                colorNoSelection: 'rgba(1,205,254)',
                colorSelected: 'rgba(2, 255, 161)',
                colorHover: 'rgba(255, 113, 206)',
                scaleDefault: 1.0,
                scaleSelected: 1.4,
                scaleHover: 1.4,
              },
            sprites: {
                minPointSize: 2.0,
                imageSize: 50,
                colorUnselected: '#ffffff',
                colorNoSelection: '#ffffff',
                    },
            }      
            
        });
    
    scatterGL.render(dataset);
    scatterGL.setSpriteRenderMode();
    return scatterGL;
    };

// DOM and interactions
window.addEventListener('resize', () => {
    scatterGL.resize();
  });

window.addEventListener('load', (event) => {
    console.log('page is fully loaded');
  });

// interactions
  document
  .querySelectorAll('input[name="interactions"]')
  .forEach(inputElement => {
    inputElement.addEventListener('change', () => {
      if (inputElement.value === 'pan') {
        scatterGL.setPanMode();
      } else if (inputElement.value === 'select') {
        scatterGL.setSelectMode();
      }
    });
  });

// render mode selection
document
  .querySelectorAll('input[name="render"]')
  .forEach(inputElement => {
    inputElement.addEventListener('change', () => {
      renderMode = inputElement.value;
      if (inputElement.value === 'points') {
        scatterGL.setPointRenderMode();
      } else if (inputElement.value === 'sprites') {
        scatterGL.setSpriteRenderMode();
      }
    });
  });
// color mapping 
const hues = [...new Array(nLabels)].map((_, i) => Math.floor((370 / nLabels) * i));
console.log(hues);
const lightTransparentColorsByLabel = hues.map(
  hue => `hsla(${hue}, 100%, 50%, 0.05)`
);
const heavyTransparentColorsByLabel = hues.map(
  hue => `hsla(${hue}, 100%, 50%, 0.75)`
);
const opaqueColorsByLabel = hues.map(hue => `hsla(${hue}, 100%, ${50 + Math.floor(Math.random()*20)}%, 1)`);


document
  .querySelectorAll('input[name="color"]')
  .forEach(inputElement => {
    inputElement.addEventListener('change', () => {
      if (inputElement.value === 'default') {
        scatterGL.setPointColorer(null);
      } else if (inputElement.value === 'label') {
        scatterGL.setPointColorer((i, selectedIndices, hoverIndex) => {
          const labelIndex = dataProj.metadata['labels'][i];
          const opaque = 1;
          if (opaque) {
            return opaqueColorsByLabel[labelIndex];
          } else {
            if (hoverIndex === i) {
              return 'red';
            }

            // If nothing is selected, return the heavy color
            if (selectedIndices.size === 0) {
              return heavyTransparentColorsByLabel[labelIndex];
            }
            // Otherwise, keep the selected points heavy and non-selected light
            else {
              const isSelected = selectedIndices.has(i);
              return isSelected
                ? heavyTransparentColorsByLabel[labelIndex]
                : lightTransparentColorsByLabel[labelIndex];
            }
          }
        });
      }
    });
  });

// projection
document
.querySelectorAll('input[name="projection"]')
.forEach(inputElement => {
  inputElement.addEventListener('change', () => {
    renderMode = inputElement.value;
    if (inputElement.value === 'cartesian') {
        const dataset = new ScatterGL.Dataset(dataProj.projections,dataProj.idx);
        dataset.setSpriteMetadata({
        spriteImage: spriteUrl,
        singleSpriteSize: [150, 150],
        });
        scatterGL.updateDataset(dataset);
        scatterGL.startOrbitAnimation();

    } else if (inputElement.value === 'spherical') {
        const sphDataset = new ScatterGL.Dataset(dataProj.spherical,dataProj.idx);
        sphDataset.setSpriteMetadata({
        spriteImage: spriteUrl,
        singleSpriteSize: [150, 150],
        });
        scatterGL.updateDataset(sphDataset);
        scatterGL.startOrbitAnimation();
    } 
  });
});
// Orbit 
const toggleOrbitButton = document.getElementById('toggle-orbit');
toggleOrbitButton.addEventListener('click', () => {
  if (scatterGL.isOrbiting) { 
    scatterGL.stopOrbitAnimation();
  } else {
    scatterGL.startOrbitAnimation();
  }
});

const datasetSelector = document.getElementById("dataset-selector");
datasetSelector.addEventListener('change', () => {
    console.log(datasetSelector.value);
    });
