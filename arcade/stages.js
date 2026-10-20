import {pixelText} from './world/modules/pixel-font.js';
const registry=await fetch('/arcade/stage-registry.json').then(r=>r.json());
const paths=Object.fromEntries(registry.stages.filter(s=>s.status==='ready'&&s.asset).map(s=>[s.id,s.asset]));
const images=Object.fromEntries(Object.entries(paths).map(([key,file])=>{const image=new Image();image.src='/arcade/world/assets/'+file;return [key,image];}));
export function stageFrame(ctx,w,h,t,environment={}){
 t=environment.motion?.enabled===false?0:Math.floor(t*(environment.motion?.fps||30)*(environment.motion?.speed||1))/(environment.motion?.fps||30);
 const name=environment.stage||'rooftop',im=images[name],hour=environment.clock?.hour??20,weather=environment.weather?.effective||'clear',intensity=environment.weather?.intensity??.6;
 ctx.save();ctx.imageSmoothingEnabled=false;ctx.fillStyle='#100d20';ctx.fillRect(0,0,w,h);
 if(im?.complete&&im.naturalWidth){const scale=Math.max(w/im.naturalWidth,h/im.naturalHeight),sw=w/scale,sh=h/scale;ctx.drawImage(im,(im.naturalWidth-sw)/2,(im.naturalHeight-sh)/2,sw,sh,0,0,w,h);}
 const night=hour<6||hour>=20,dusk=(hour>=17&&hour<20)||(hour>=6&&hour<8);
 ctx.fillStyle=night?'#080e39':dusk?'#71336c':'#b0dfff';ctx.globalAlpha=night?(name==='waterfront'?.52:.16):dusk?.22:name==='waterfront'?.02:.14;ctx.fillRect(0,0,w,h);ctx.globalAlpha=1;
 // Selected 24/30/60 fps cadence; motion stays on the pixel grid.
 // River glints, neon reflections and vent puffs continue in clear weather.
 const frame=Math.floor(t*(environment.motion?.fps||30));ctx.save();ctx.globalCompositeOperation='screen';
 ctx.fillStyle=night?'#80d7ff':'#b4ddff';ctx.globalAlpha=name==='waterfront'?.16:.08;
 for(let i=0;i<22;i++){const y=name==='waterfront'?h*(.44+(i%9)*.013):h*(.84+(i%6)*.018),x=(w*.33+i*37+(Math.floor(t*10)%16)*2)%w;ctx.fillRect(Math.round(x),Math.round(y),Math.max(2,w/130+(i%4)*w/150),Math.max(1,h/470));}
 ctx.globalAlpha=.045;ctx.fillStyle='#c4c5e7';for(let i=0;i<6;i++){const phase=(Math.floor(t*10)+i*5)%32,x=w*(.12+(i%2)*.015)+Math.sin(phase/8)*w*.004,y=h*(.57-phase*.0018);ctx.fillRect(Math.round(x),Math.round(y),w*.012+phase*w*.0002,h*.007);}
 ctx.restore();
 ctx.save();ctx.globalAlpha=night?.09:.16;ctx.fillStyle=night?'#6776a9':'#d0d7ef';
 for(let i=0;i<5;i++){const cx=Math.round(((i*.24*w+t*w*.0015)%(w*1.3))-w*.16),cy=Math.round(h*(.07+(i%3)*.04)),unit=Math.max(1,Math.round(w/320));for(const [dx,dy,cw,ch] of [[0,2,15,2],[3,0,7,2],[10,1,8,2]])ctx.fillRect(cx+dx*unit,cy+dy*unit,cw*unit,ch*unit);}
 ctx.restore();
 // Low-cost deterministic loops. Particle budget stays bounded at 140.
 if(weather==='rain'||weather==='storm'||weather==='snow'){
  const snow=weather==='snow',count=Math.round(35+intensity*105);ctx.fillStyle=snow?'#e4edff':'#80d7ff';ctx.globalAlpha=snow?.65:.3;
  for(let i=0;i<count;i++){const x=((i*71+t*(snow?8:42))%(w+30))-15,y=(i*43+t*(snow?23:230))%h;ctx.fillRect(Math.round(x),Math.round(y),snow?2:1,snow?2:Math.max(4,h/50));}
  if(!snow){ctx.globalAlpha=.2;for(let i=0;i<14;i++){const p=(t*2+i*.31)%1;ctx.fillRect((i*137)%w,h*(.82+(i%4)*.04),3+p*12,1);}}
 }
 if(weather==='fog'||weather==='cloudy'){const grad=ctx.createLinearGradient(0,h*.35,0,h);grad.addColorStop(0,'#b4c5ee00');grad.addColorStop(1,weather==='fog'?'#b4c5ee77':'#a9b7ce22');ctx.globalAlpha=intensity;ctx.fillStyle=grad;ctx.fillRect(0,0,w,h);}
 if(weather==='storm'&&Math.floor(t*10)%173===0){ctx.globalAlpha=.06*intensity;ctx.fillStyle='#e4efff';ctx.fillRect(0,0,w,h);}
 // A real foreground fixture: emission, backing shadow, wall receive, floor reflection.
 // Each stage shares the authored fixture, not a full-frame brightness adjustment.
 const energy=environment.audio?.connected?Math.max(0,Math.min(1,environment.audio.smoothed??environment.audio.level??0)):0;
 const bx=Math.round(w*.84),by=Math.round(h*.16),bw=Math.round(w*.115),bh=Math.round(h*.07),u=Math.max(1,Math.round(w/640));
 ctx.globalAlpha=1;ctx.fillStyle='#070b18';ctx.fillRect(bx+u*2,by+u*3,bw,bh);ctx.fillStyle='#15172e';ctx.fillRect(bx,by,bw,bh);
 ctx.save();ctx.globalCompositeOperation='screen';
 for(let i=4;i>0;i--){ctx.globalAlpha=energy*.025*(5-i);ctx.fillStyle='#80d7ff';ctx.fillRect(bx-i*u*2,by-i*u,bw+i*u*4,bh+i*u*2);}
 ctx.globalAlpha=.25+energy*.7;ctx.fillStyle='#80d7ff';ctx.fillRect(bx+u*2,by+u*2,bw-u*4,u);ctx.fillStyle='#9664ed';ctx.fillRect(bx+u*2,by+bh-u*3,bw-u*4,u);
 pixelText(ctx,'ST',bx+bw/2,by+bh*.6,Math.max(1,Math.round(w/640)),'#80d7ff');
 for(let i=0;i<8;i++){ctx.globalAlpha=energy*.055*(1-i/8);ctx.fillStyle=i%2?'#80d7ff':'#9664ed';ctx.fillRect(bx-i*u*2,h*.88+i*u*3,bw+i*u*4,u);}
 ctx.restore();
 ctx.restore();
}
