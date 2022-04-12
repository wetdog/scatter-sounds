
var containerElement = document.getElementById('container');
// Create random point vector

var randPoints = [];
var nPoints = 500;

for (let i=0; i<nPoints; i++){
    var tmpPoint = [0,0,0];
    for (let j=0; j<3; j++){
        tmpPoint[j] = Math.random()
    }
    //console.log(tmpPoint)
    randPoints.push(tmpPoint)
}

// **************** Web audio *****************
const context = new AudioContext();
let bufferData = null;
const audioUrl = "/sounds/37.wav";

function playTone(freq,gain){
    // create  nodes
    const osc = new OscillatorNode(context);
    const amp = new GainNode(context);

    // connect the nodes
    osc.connect(amp);
    amp.connect(context.destination);

    // Set properties
    osc.frequency.value = freq;
    amp.gain.value = gain;
    osc.start();
    osc.stop(context.currentTime + 1);
}


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
        document.getElementById('msg').textContent ='Duration: ' + audioBuffer.duration
         + ' Vector Length: ' + audioBuffer.length + ' Sample rate: ' 
         + audioBuffer.sampleRate + ' Number of channels: ' + audioBuffer.numberOfChannels;
    } catch (error) {
        console.log(`Error: ${error}`);
    }
    }

function playSounds(buffer){
    const now = context.currentTime;
    const source = new AudioBufferSourceNode(context);
    const amp = new GainNode(context);
    source.connect(amp).connect(context.destination);

    source.buffer = buffer;
    source.start();
    source.stop(now + buffer.duration);
}


loadSoundfetch(context,audioUrl);

const dataset = new ScatterGL.Dataset(randPoints);
const scatterGL = new ScatterGL(containerElement,
//        {
//            onClick: (point) => playTone(400 + Math.random()*1500,0.8),

//        }
        {
            onHover: (point) => playSounds(bufferData)
        }
    );

scatterGL.render(dataset);
// Add in a resize observer for automatic window resize.
window.addEventListener('resize', () => {
    scatterGL.resize();
  });

