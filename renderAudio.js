

// Load json File projections
const dataUrl = "./preprocess/projections.json"
const audioUrl = "long_audio_2.wav";
let dataArray;
let bufferData = null;
let bufferDataArray

const containerElement = document.getElementById('container');

async function loadSoundfetch(audioContext, url){              
    try {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        bufferData = audioBuffer;
        console.log('Duration: ' + audioBuffer.duration);
        console.log('Vector Length: ' + audioBuffer.length);
        console.log('Sample rate: ' + audioBuffer.sampleRate);
        console.log('Number of channels: ' + audioBuffer.numberOfChannels);
        // Debug message
        document.getElementById('msg').textContent ='Duration: ' + audioBuffer.duration
         + ' Vector Length: ' + audioBuffer.length + ' Sample rate: ' 
         + audioBuffer.sampleRate + ' Number of channels: ' + audioBuffer.numberOfChannels;
    } catch (error) {
        console.log(`Error: ${error}`);
    }
    }

function playSounds(buffer,point){
    console.log(point);
    console.log("Start time:" + point*0.48);

    if(point){
        const now = context.currentTime;
        const source = new AudioBufferSourceNode(context);
        const amp = new GainNode(context);
        source.connect(amp).connect(context.destination);
        
        source.buffer = buffer;
        source.start(now,point*0.48);
        source.stop(now + 1);
    }
}

// load Json data
fetch(dataUrl)
    .then(function(resp) {
        return resp.json(); 
    })
    .then(function(data){        
        dataArray = data;
    })
    
// **************** Web audio *****************
const context = new AudioContext();
loadSoundfetch(context,audioUrl);

function renderDataset(){
    const dataset = new ScatterGL.Dataset(dataArray.projections);
    const scatterGL = new ScatterGL(containerElement,
            //{
              //onClick: (point) => playSounds(bufferData,point)

            //},
            {
               onHover: (point) => playSounds(bufferData,point)
            }
        );

    scatterGL.render(dataset);
    }

setTimeout(renderDataset,3000)
// Add in a resize observer for automatic window resize.
window.addEventListener('resize', () => {
    scatterGL.resize();
  });

