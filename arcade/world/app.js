import {FrameClock} from '/arcade/frame-clock.js';
const roomClock=new FrameClock(),brandClock=new FrameClock();let frameFps=30;
import {surface} from './modules/surface.js?v=18';
import {drawCountdown,drawLowerThird} from './modules/countdown.js?v=18';
import {drawVote} from './modules/vote.js?v=18';
import {drawFight} from './modules/fight.js?v=18';
import {drawControls} from './modules/controls.js?v=18';
import {createAttract,drawAttract} from './modules/attract.js?v=18';
import {Lighting} from './modules/lighting.js?v=18';
import {drawBrand} from './modules/brand.js?v=18';
import {InputViewer} from './modules/input-viewer.js?v=18';
import {Groove} from './modules/groove.js?v=18';
import {ObsAudio} from './modules/obs-audio.js?v=18';
import {createWidgetLayout} from './modules/widget-layout.js?v=18';
import {crt} from './modules/screen-fx.js?v=18';
import {IntroSequence} from './modules/intro.js?v=18';

const params=new URLSearchParams(location.search),brb=params.get('scene')==='brb';
document.querySelector('#controls').hidden=!params.has('controls');
const intro=new IntroSequence(document.querySelector('#stage'));
if(['intro','stinger'].includes(params.get('scene')))intro.play(params.get('scene')==='stinger');
for(const [label,onlyStinger] of [['Play intro',false],['Preview stinger',true]]){const button=document.createElement('button');button.textContent=label;button.onclick=()=>intro.play(onlyStinger);document.querySelector('#controls').append(button);}
const sceneLink=document.createElement('a');sceneLink.href='/studio';sceneLink.textContent='Scene layouts';sceneLink.style.color='#80d7ff';document.querySelector('#controls').append(sceneLink);
const cabinetLink=document.createElement('a');cabinetLink.href='/arcade/editor';cabinetLink.textContent='Dimensional cabinet';cabinetLink.style.color='#80d7ff';document.querySelector('#controls').append(cabinetLink);
function fit(){
 const close=params.get('focus')==='cabinet',scale=close?Math.min(innerWidth/605,innerHeight/915):(params.has('cover')?Math.max(innerWidth/1672,innerHeight/941):Math.min(innerWidth/1672,innerHeight/941));
 const stage=document.querySelector('#stage');stage.style.transform=`translate(-50%,-50%) scale(${scale})`+(close?' translate(-538px,-9px)':'');
 stage.style.clipPath=close?'inset(28px 0 0 1071px)':'';
}
addEventListener('resize',fit);fit();
const fight=surface(512,300,[[344,255],[829,275],[855,550],[356,550]]);
if(params.get('focus')==='game'){
 document.querySelector('#stage').hidden=true;
 fight.canvas.className='fight-preview';fight.canvas.style.transform='translate(-50%,-50%)';
 document.querySelector('#viewport').append(fight.canvas);
}
const vote=surface(640,420,[[1182,268],[1521,268],[1543,505],[1193,505]]);
const timer=surface(500,110,[[1159,84],[1574,84],[1572,172],[1159,172]]);
const brand=surface(1000,270,[[340,58],[871,99],[871,212],[339,180]]);
const sponsor=surface(240,170,[[1018,260],[1075,248],[1075,315],[1018,329]]);
sponsor.fillStyle='#0b1020';sponsor.fillRect(0,0,240,170);sponsor.strokeStyle='#8a6d9a';sponsor.lineWidth=4;sponsor.strokeRect(3,3,234,164);sponsor.fillStyle='#ccb8cf';sponsor.font='bold 48px monospace';sponsor.textAlign='center';sponsor.fillText('AKKO',120,67);sponsor.font='bold 42px monospace';sponsor.fillText('FUNBOX',120,128);
const inputDeck=surface(600,100,[[1158,547],[1588,547],[1622,589],[1181,589]]),inputViewer=new InputViewer();
// Fightstick only; discard stale layout links from earlier previews.
if(params.has('layout')){const url=new URL(location.href);url.searchParams.delete('layout');history.replaceState(null,'',url);}
let brandEnergy=0;
function drawCabinetAssets(now=0){if(brandClock.sample(now,frameFps)!==null){drawBrand(brand,now/1000,brandEnergy);inputViewer.draw(inputDeck);}requestAnimationFrame(drawCabinetAssets);}drawCabinetAssets();
const machines=createAttract(),effects=document.querySelector('#effects').getContext('2d'),lighting=new Lighting();
const groove=new Groove();let groovePreview=false;
const widgetDock=createWidgetLayout(document.querySelector('#stage'));
widgetDock.hidden=params.get('focus')==='cabinet'||(!params.has('controls')&&!params.has('widget-preview'));
document.querySelector('#widget-samples').checked=!widgetDock.hidden;
document.querySelector('#widget-samples').onchange=e=>widgetDock.hidden=!e.target.checked;
document.querySelector('#groove-preview').onclick=()=>{groovePreview=!groovePreview;document.querySelector('#groove-preview').textContent=groovePreview?'Stop simulated groove':'Preview groove';document.querySelector('#stage').classList.toggle('simulated-audio',groovePreview);};
let lastDraw=0;
let state=null,token='',last=performance.now(),connected=false;
async function post(path,data){if(!token)throw Error('Not connected');const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Arcade-Token':token},body:JSON.stringify(data)});if(!r.ok)throw Error('Connection failed');return r.json();}
async function poll(){try{if(!token)token=(await(await fetch('/api/bootstrap')).json()).token;const r=await fetch('/api/state');if(!r.ok)throw Error('offline');state=await r.json();frameFps=state.motion?.fps||30;state._receivedAt=performance.now();connected=true;document.querySelector('#connection').textContent=state.demo?'DEMO MODE — SIMULATED FIGHTS':'';document.querySelector('#demo').textContent=state.demo?'End demo / new live session':'Start demo fights';}catch{connected=false;document.querySelector('#connection').textContent='OVERLAY CONNECTION LOST';}setTimeout(poll,80);}
poll();
function frame(now){
 if(roomClock.sample(now,frameFps)===null){requestAnimationFrame(frame);return;}
 const dt=Math.min(.1,(now-last)/1000),t=now/1000;last=now;
 if(state){
  const p=state.palettes[state.palette];
  const audio=groovePreview?{level:.12+.66*Math.pow(Math.max(0,Math.sin(t*5.5)),3),bass:0,treble:0}:state.audio;
  const visualState={...state,audio};groove.update(audio,dt);
  document.querySelector('#cabinetTint').style.filter=`hue-rotate(${p.hue}deg)`;
  drawFight(fight,state,t,p);crt(fight,t);drawVote(vote,state,t);groove.screen(vote);crt(vote,t);
  if(params.get('countdown')==='both')drawCountdown(timer,state,p,brb);else groove.marquee(timer);
  drawAttract(machines,t,p);effects.clearRect(0,0,1672,941);
  lighting.events(state.events);lighting.draw(effects,visualState,dt,p);
  brandEnergy=groove.level;inputViewer.energy=groove.level;
  const attackTime=state.revealElapsed+Math.max(0,(performance.now()-state._receivedAt)/1000);
  drawControls(effects,state.players.map(f=>({...f,action:state.phase==='reveal'?f.action:'idle',elapsed:attackTime})),p,groove.level);
  inputViewer.drawPhysicalStick(effects);
  groove.deck(effects,t);
  if(params.get('countdown')!=='marquee'&&params.get('focus')!=='cabinet')drawLowerThird(effects,state,p,brb);
 }intro.draw(now,brandEnergy);requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
document.querySelector('#demo').onclick=async()=>{try{await post('/api/admin',{action:'demo',enabled:!state?.demo});}catch(e){document.querySelector('#status').textContent=e.message;}};
document.querySelector('#reset').onclick=()=>post('/api/admin',{action:'reset'}).catch(e=>document.querySelector('#status').textContent=e.message);

let audioStream=null,audioContext=null,audioTimer=null;
function disconnectAudio(){if(audioTimer)clearInterval(audioTimer);audioTimer=null;audioStream?.getTracks().forEach(t=>t.stop());audioStream=null;audioContext?.close();audioContext=null;document.querySelector('#audio').textContent='Connect music audio';document.querySelector('#status').textContent='Audio disconnected';}
document.querySelector('#audio').onclick=async()=>{
 if(audioStream){disconnectAudio();return;}
 try{
  obs.disconnect();
  const stream=await navigator.mediaDevices.getDisplayMedia({video:true,audio:true});
  if(!stream.getAudioTracks().length){stream.getTracks().forEach(t=>t.stop());throw Error('No shared audio. Choose a source with audio enabled.');}
  audioStream=stream;audioContext=new AudioContext();await audioContext.resume();let analyser=audioContext.createAnalyser();analyser.fftSize=1024;audioContext.createMediaStreamSource(stream).connect(analyser);let wave=new Float32Array(analyser.fftSize),freq=new Uint8Array(analyser.frequencyBinCount);let sending=false;
  audioTimer=setInterval(async()=>{if(sending)return;analyser.getFloatTimeDomainData(wave);analyser.getByteFrequencyData(freq);let rms=Math.sqrt(wave.reduce((sum,v)=>sum+v*v,0)/wave.length);let mean=(a,b)=>freq.slice(a,b).reduce((s,v)=>s+v,0)/((b-a)*255);sending=true;try{await post('/api/audio',{level:Math.min(1,rms*5),bass:mean(1,6),treble:mean(45,110)});}catch{}finally{sending=false;}},70);
  stream.getVideoTracks()[0]?.addEventListener('ended',disconnectAudio,{once:true});document.querySelector('#audio').textContent='Disconnect music audio';document.querySelector('#status').textContent='Music audio connected / not recorded';
 }catch(e){disconnectAudio();document.querySelector('#status').textContent=e.message;}
};

let obsSending=false,obsSentAt=0;
const obs=new ObsAudio({
 onLevel:async level=>{
  if(!token||obsSending||performance.now()-obsSentAt<75)return;
  obsSending=true;obsSentAt=performance.now();
  try{await post('/api/audio',{level,bass:0,treble:0});}catch{}finally{obsSending=false;}
 },
 onStatus:message=>document.querySelector('#status').textContent=message,
 onInputs:inputs=>{
  const select=document.querySelector('#obs-source');select.replaceChildren();
  const blank=document.createElement('option');blank.value='';blank.textContent='Choose music source';select.append(blank);
  for(const input of inputs){const option=document.createElement('option');option.value=input.inputName;option.textContent=input.inputName;select.append(option);}
 }
});
document.querySelector('#obs-form').onsubmit=e=>{
 e.preventDefault();const port=Number(document.querySelector('#obs-port').value);
 if(!Number.isInteger(port)||port<1||port>65535)return;
 disconnectAudio();const password=document.querySelector('#obs-password').value;
 document.querySelector('#obs-password').value='';obs.connect(port,password);
};
document.querySelector('#obs-source').onchange=e=>obs.select(e.target.value);
document.querySelector('#obs-stop').onclick=()=>{obs.disconnect();document.querySelector('#status').textContent='OBS disconnected';};
addEventListener('pagehide',()=>obs.disconnect(),{once:true});
