// Start webpage

const dataUrl = "./data/projections.json"
const audioUrl = "./data/audio.flac"
const spriteUrl = "./data/audio_sprite.jpg"
const hopSize = 0.48; //"Clip Duration"
const windowSize = 1; // clip duration
const nLoops = 4;
//let dataUrl, audioUrl, spriteUrl;
const configUrl = "./data/config.json";

let bufferData = null;
let bufferDataArray

// load config Json
fetch(configUrl)
    .then(function(resp) {
        return resp.json(); 
    })
    .then(function(data){        
        configData = data;
        const dataUrl2 = configData.projectionsFile;
        const audioUrl2 = configData.audioFile;
        const spriteUrl2 = configData.spriteFile;
        console.log(`Audio ${audioUrl2} data ${dataUrl2} Sprite ${spriteUrl2}`);
    })

const containerElement = document.getElementById('container');
// 
// const metadata  = [];
// data.projection.forEach((vector, index) => {
//    const labelIndex = data.labels[index];
//    dataPoints.push(vector);
//    metadata.push({
//      labelIndex,
//      label: data.labelNames[labelIndex],
//    });
//  });
///

    
// **************** Web audio *****************

const context = new (window.AudioContext || window.webkitAudioContext)();

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
            console.log("loop")
            source.loop = true;
            source.loopStart = point*hopSize;
            source.loopEnd =  point*hopSize + windowSize;
            source.start(now,point*hopSize);
            source.stop(now + windowSize*nLoops);
        }
    }
};

function renderDataset(dataArray){
    const dataset = new ScatterGL.Dataset(dataArray.spherical,dataArray.idx);
    dataset.setSpriteMetadata({
        spriteImage: spriteUrl,
        singleSpriteSize: [150, 150],
        // Uncomment the following line to only use the first sprite for every point
        //spriteIndices: dataArray.projections.map(d => 0),
      });
    const scatterGL = new ScatterGL(containerElement,{
        onClick: (point) => {playSounds(bufferData,point,"on-click")},
        onHover: (point) => {playSounds(bufferData,point,"on-hoover")},
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
                scaleSelected: 1.2,
                scaleHover: 1.2,
              },
            sprites: {
                minPointSize: 8.0,
                imageSize: 200,
                colorUnselected: '#ffffff',
                colorNoSelection: '#ffffff',
                    },
            }      
            
        });
    
    scatterGL.render(dataset);
    //scatterGL.setSpriteRenderMode();
    return scatterGL;
    };

loadSoundfetch(context,audioUrl);
// load Json data
fetch(dataUrl)
    .then(function(resp) {
        return resp.json(); 
    })
    .then(function(data){        
        return data;
    })
    .then((dataArray)=>{console.log("data loaded");
                return scatterGL = renderDataset(dataArray)})

// Add in a resize observer for automatic window resize.
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
        console.log("points");
      } else if (inputElement.value === 'sprites') {
        scatterGL.setSpriteRenderMode();
      } else if (inputElement.value === 'text') {
        scatterGL.setTextRenderMode();
      }
    });
  });

// toogle Orbit 
const toggleOrbitButton = document.getElementById('toggle-orbit');
toggleOrbitButton.addEventListener('click', () => {
  if (scatterGL.isOrbiting()) { 
    scatterGL.stopOrbitAnimation();
  } else {
    scatterGL.startOrbitAnimation();
  }
});