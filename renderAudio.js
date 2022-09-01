
// Load json File projections
const dataUrl = "./data/projections.json"
const audioUrl = "./data/city_sound.flac";

let dataArray;
let bufferData = null;
let bufferDataArray

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

// load Json data
fetch(dataUrl)
    .then(function(resp) {
        return resp.json(); 
    })
    .then(function(data){        
        dataArray = data;
    })
    
// **************** Web audio *****************

const context = new window.AudioContext();

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

function playSounds(buffer,point,typeCall){
    console.log(point);
    console.log("Start time:" + point*0.48);

    if(point){ 
        const now = context.currentTime;
        const source = new AudioBufferSourceNode(context);
        const amp = new GainNode(context);
        source.connect(amp).connect(context.destination);
        source.buffer = buffer;
        
        if (typeCall === "on-hoover"){
            source.start(now,point*0.48);
            source.stop(now + 1);
        }
        if (typeCall === "on-click"){
            console.log("loop")
            source.loop = true
            source.start(now,point*0.48);
            source.stop(now + 4);
        }
    }
}

loadSoundfetch(context,audioUrl);



function renderDataset(){
    const dataset = new ScatterGL.Dataset(dataArray.projections,dataArray.idx);
    dataset.setSpriteMetadata({
        spriteImage: './data/city_sound_sprite.jpg',
        singleSpriteSize: [150, 150],
        // Uncomment the following line to only use the first sprite for every point
        //spriteIndices: dataArray.projections.map(d => 0),
      });
    const scatterGL = new ScatterGL(containerElement,{
        onClick: (point) => playSounds(bufferData,point,"on-click"),
        onHover: (point) => playSounds(bufferData,point,"on-hoover"),
        styles: {
            backgroundColor: '#fffb96',
            axesVisible: false,
            fog: {
                color: '#ffffff',
                enabled: false,
                threshold: 15000,
              },
            sprites: {
                minPointSize: 5.0,
                imageSize: 150,
                colorUnselected: '#ffffff',
                colorNoSelection: '#ffffff',
                    },
            }   
  
    });
    
    scatterGL.render(dataset);
    scatterGL.setSpriteRenderMode();
    
    }

setTimeout(renderDataset,3000)


// Add in a resize observer for automatic window resize.
window.addEventListener('resize', () => {
    scatterGL.resize();
  });

window.addEventListener('load', (event) => {
    console.log('page is fully loaded');
  });