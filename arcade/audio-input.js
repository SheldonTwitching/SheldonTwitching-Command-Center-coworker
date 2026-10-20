// Capture only after an explicit operator gesture. No audio recording or playback.
export class AudioInput {
 constructor(report){this.report=report;this.generation=0;}
 async devices(){
  if(!navigator.mediaDevices?.enumerateDevices)throw Error('Audio capture is unavailable in this browser. Use the OBS relay.');
  return (await navigator.mediaDevices.enumerateDevices()).filter(d=>d.kind==='audioinput');
 }
 async start(config){
  this.stop();const generation=this.generation;
  if(!config.enabled||config.mode==='relay'){this.report('OBS relay selected. Keep its audio sender active.');return;}
  let stream,context;
  try{
   stream=config.mode==='desktop'?await navigator.mediaDevices.getDisplayMedia({video:true,audio:true}):await navigator.mediaDevices.getUserMedia({video:false,audio:{deviceId:config.deviceId?{exact:config.deviceId}:undefined,echoCancellation:false,noiseSuppression:false,autoGainControl:false}});
   if(generation!==this.generation){stream.getTracks().forEach(t=>t.stop());return;}
   if(!stream.getAudioTracks().length)throw Error('No audio was shared. Choose a source and enable Share audio, or select an audio input.');
   this.stream=stream;context=new AudioContext();this.context=context;await context.resume();
   if(generation!==this.generation){stream.getTracks().forEach(t=>t.stop());await context.close();return;}
   const source=context.createMediaStreamSource(stream),analyser=context.createAnalyser();analyser.fftSize=1024;analyser.smoothingTimeConstant=config.smoothing;source.connect(analyser);
   const frequency=new Uint8Array(analyser.frequencyBinCount),wave=new Float32Array(analyser.fftSize),token=(await fetch('/api/bootstrap').then(r=>r.json())).token;
   const mean=(low,high)=>{let total=0,count=0;for(let i=0;i<frequency.length;i++){const hz=i*context.sampleRate/analyser.fftSize;if(hz>=low&&hz<high){total+=frequency[i]/255;count++;}}return count?Math.min(1,total/count*config.gain):0;};
   if(generation!==this.generation)return;
   let sending=false;
   this.timer=setInterval(async()=>{
    if(sending||generation!==this.generation)return;sending=true;
    try{analyser.getByteFrequencyData(frequency);analyser.getFloatTimeDomainData(wave);const rms=Math.sqrt(wave.reduce((sum,v)=>sum+v*v,0)/wave.length);
     const levels={source:config.mode,level:Math.min(1,rms*4*config.gain),bass:mean(30,250),treble:mean(2500,12000)};
     const result=await fetch('/api/audio',{method:'POST',headers:{'Content-Type':'application/json','X-Arcade-Token':token},body:JSON.stringify(levels)});if(!result.ok)throw Error('Audio bridge rejected signal');
     this.report('Listening · '+(stream.getAudioTracks()[0].label||'selected audio')+' · '+Math.round(levels.level*100)+'%',levels);
    }catch(e){this.report(e.message);}finally{sending=false;}
   },80);
   stream.getTracks().forEach(t=>t.addEventListener('ended',()=>{if(generation===this.generation){this.stop();this.report('Capture ended. Lighting will settle to idle.');}}));
  }catch(e){stream?.getTracks().forEach(t=>t.stop());if(context&&context!==this.context)await context.close();this.stop();this.report(e.message);}
 }
 stop(){this.generation++;clearInterval(this.timer);this.stream?.getTracks().forEach(t=>t.stop());this.stream=null;if(this.context){this.context.close().catch(()=>{});this.context=null;}}
}
