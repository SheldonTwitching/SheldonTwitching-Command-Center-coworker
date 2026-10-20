import {FrameClock} from './frame-clock.js';
const frameClock=new FrameClock();
import {stageFrame} from './stages.js';
import {defaultLayout,glassOnCanvas} from './layouts.js';
import {pixelText,creditsSample} from './world/modules/pixel-font.js';
const $=id=>document.getElementById(id),params=new URLSearchParams(location.search),preview=params.has('preview'),stage=$('stage'),ctx=$('background').getContext('2d');
let lastFrame=0;
let project,environment={},arcade={},scene='starting',vertical=false,layout,started=performance.now(),lastKey='';
function rect(el,r){Object.assign(el.style,{left:r[0]+'px',top:r[1]+'px',width:r[2]+'px',height:r[3]+'px'});}
function fit(){if(!project)return;stage.style.transform='scale('+Math.min(innerWidth/(vertical?1080:1920),innerHeight/(vertical?1920:1080))+')';}addEventListener('resize',fit);
async function poll(){try{
 const [p,e,a]=await Promise.all(['/api/studio/project','/api/studio/environment','/api/arcade/config'].map(u=>fetch(u,{cache:'no-store'}).then(r=>r.json())));project=p;environment=e;arcade=a;
 const next=params.get('scene')||p.scene,form=params.get('format')||p.format,key=next+form;if(key!==lastKey){lastKey=key;started=performance.now();}
 scene=next;vertical=form==='vertical';const w=vertical?1080:1920,h=vertical?1920:1080;stage.style.width=w+'px';stage.style.height=h+'px';if($('background').width!==w){$('background').width=w;$('background').height=h;}
 layout={...defaultLayout(scene,vertical),...(p.layouts[scene+':'+form]||{})};
 const room=['starting','intro'].includes(scene);$('room').hidden=!room;
 if(room){const u='/arcade/world/index.html?scene='+(scene==='brb'?'brb':scene==='intro'?'intro':'starting')+(vertical?'&cover=1':'');if($('room').getAttribute('src')!==u)$('room').src=u;rect($('room'),vertical?[0,0,1080,1120]:[0,0,w,h]);}
 $('cabinet').hidden=scene!=='gameplay';if(scene==='gameplay'){if(!$('cabinet').getAttribute('src'))$('cabinet').src='/studio/parts/all';rect($('cabinet'),layout.cabinet);}
 for(const id of ['labels','spotify','chat']){$(id).hidden=!p.widgets[id]||scene==='intro'||scene==='background';rect($(id),layout[id]);}
 $('custom').textContent=p.customCss;fit();$('guides').replaceChildren();
 if(preview){for(const name of scene==='gameplay'?['camera','game']:scene==='chatting'?['camera']:[]){const el=document.createElement('div');el.className='slot guide';el.textContent=name.toUpperCase()+' · OBS SOURCE GUIDE';rect(el,name==='game'?glassOnCanvas(layout.cabinet,true):layout[name]);$('guides').append(el);}$('caption').hidden=false;$('caption').textContent='EDITOR PREVIEW · '+(e.weather?.mode==='manual'?'MANUAL ':'')+(e.weather?.effective||'clear')+' · '+Math.floor(e.clock?.hour||0)+':00 · '+(e.stage||'');}
 }catch{if(preview){$('caption').hidden=false;$('caption').textContent='Bridge unavailable · retaining last scene';}}setTimeout(poll,1000);}poll();
let audioTarget={};async function audioPoll(){try{audioTarget=await(await fetch('/api/studio/audio',{cache:'no-store'})).json();}catch{}setTimeout(audioPoll,80);}audioPoll();
let smoothed=0;
function frame(now){const dt=frameClock.sample(now,environment.motion?.fps||30);if(dt===null){requestAnimationFrame(frame);return;}const target=audioTarget.connected?audioTarget.level:0;smoothed+=(target-smoothed)*Math.min(1,dt*(target>smoothed?24:6));environment.audio={...audioTarget,smoothed};if(project){const w=ctx.canvas.width,h=ctx.canvas.height,t=(now-started)/1000;ctx.clearRect(0,0,w,h);if(!['starting','intro'].includes(scene))stageFrame(ctx,w,h,now/1000,environment);
 if(scene==='gameplay'){const r=glassOnCanvas(layout.cabinet,true);ctx.clearRect(...r);ctx.clearRect(...layout.camera);}
 if(scene==='chatting'){ctx.clearRect(...layout.camera);}
 if(scene==='brb'){pixelText(ctx,'BE RIGHT BACK',w/2,h*.18,vertical?4:6,'#80d7ff');}
 if(scene==='ending'){const phase=creditsSample(t),x=w/2;ctx.fillStyle='#100d20bb';ctx.fillRect(w*.18,h*.25,w*.64,h*.6);const text=phase.phase==='title'?'THANKS FOR PLAYING':phase.phase==='hold'?'SEE YOU NEXT STREAM':'';if(text)pixelText(ctx,text,x,h*.37,vertical?4:6,'#80d7ff');else{ctx.save();ctx.beginPath();ctx.rect(w*.18,h*.25,w*.64,h*.6);ctx.clip();['ARCADE HOST','SHELDONTWITCHING','','THE PLAYERS','EVERYONE IN CHAT','','REFEREE','DAIGOTRON9000','','SPONSOR','AKKO FUNBOX'].forEach((s,i)=>pixelText(ctx,s,x,h*.85-phase.progress*(h*.6+1100)+i*100,4,i%3===0?'#9664ed':'#e4efff'));ctx.restore();}}
 }requestAnimationFrame(frame);}requestAnimationFrame(frame);
