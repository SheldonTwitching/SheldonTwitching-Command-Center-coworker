import {FrameClock} from './frame-clock.js';
const frameClock=new FrameClock();
import {drawMarquee} from './graffiti-marquee.js';
const canvas=document.createElement('canvas');canvas.className='graffiti-marquee';canvas.width=1700;canvas.height=235;document.getElementById('original-art').append(canvas);const ctx=canvas.getContext('2d');
let config={},audio={},last=0,energy=0;
async function poll(){
 try{config=await(await fetch('/api/arcade/config',{cache:'no-store'})).json();document.documentElement.dataset.marqueeStyle=config.marqueeStyle;canvas.style.zIndex=String((config.layerOrder||[]).indexOf('marquee')+1);}catch{}
 try{audio=await(await fetch('/api/studio/audio',{cache:'no-store'})).json();}catch{audio={connected:false};}
 setTimeout(poll,100);
}poll();
function draw(now){const dt=frameClock.sample(now,audio.fps||30);if(dt!==null){const target=audio.connected?audio.level:0;energy+=(target-energy)*Math.min(1,dt*(target>energy?24:6));drawMarquee(ctx,1700,235,config,energy);}requestAnimationFrame(draw);}requestAnimationFrame(draw);
