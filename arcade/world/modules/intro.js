import {introSample} from './intro-timing.js?v=18';
const logo=new Image();logo.src='/arcade/world/assets/logo-glacier-violet.png';
export class IntroSequence{
 constructor(stage){this.canvas=document.createElement('canvas');this.canvas.id='intro-sequence';this.canvas.width=1672;this.canvas.height=941;this.ctx=this.canvas.getContext('2d');this.canvas.hidden=true;stage.append(this.canvas);this.started=null;this.active=false;}
 play(stingerOnly=false){this.started=null;this.active=true;this.stingerOnly=stingerOnly;this.cut=false;this.canvas.hidden=false;}
 draw(now,energy=0){
  if(!this.active)return;
  const ctx=this.ctx;ctx.clearRect(0,0,1672,941);ctx.imageSmoothingEnabled=false;
  if(!logo.complete||!logo.naturalWidth){ctx.fillStyle='#080c1d';ctx.fillRect(0,0,1672,941);return;}
  if(this.started===null)this.started=now;
  const s=introSample((now-this.started)/1000,this.stingerOnly);
  if(s.phase==='complete'){this.active=false;this.canvas.hidden=true;ctx.clearRect(0,0,1672,941);return;}
  if(['boot','logo','charge','wipe-in'].includes(s.phase)&&!this.stingerOnly){
   ctx.fillStyle='#070b19f7';ctx.fillRect(0,0,1672,941);
   // Pixel-cut paint strokes echo the cabinet skins rather than a new style.
   for(let i=0;i<12;i++){const x=i%2?1250:130,y=140+i*53;ctx.fillStyle=i%3?'#6540c5':'#43b5f0';ctx.globalAlpha=.15;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+210,y-52);ctx.lineTo(x+110,y+6);ctx.lineTo(x-30,y+36);ctx.closePath();ctx.fill();}ctx.globalAlpha=1;
   const boot=s.phase==='boot';ctx.globalAlpha=boot?.15:s.phase==='logo'?s.progress:1;
   const w=1040,h=w*logo.naturalHeight/logo.naturalWidth;ctx.drawImage(logo,316,180,w,h);ctx.globalAlpha=1;
   ctx.fillStyle='#80d7ff';ctx.font='bold 24px monospace';ctx.textAlign='center';ctx.fillText(boot?'ST / SYSTEM ONLINE':'THE ARCADE IS OPEN',836,765);
   const charge=s.phase==='charge'?s.progress:boot?s.progress:1;
   ctx.fillStyle='#302345';ctx.fillRect(456,811,760,5);ctx.fillStyle='#9664ed';ctx.fillRect(456,811,Math.round(760*charge),5);
   ctx.fillStyle='#80d7ff';ctx.globalAlpha=.25+energy*.5;ctx.fillRect(456,822,760,2);ctx.globalAlpha=1;
  }
  if(['wipe-in','cut','wipe-out'].includes(s.phase)){
   // A fully opaque cut interval hides a future OBS scene switch.
   if(s.phase==='cut'){ctx.fillStyle='#090c1c';ctx.fillRect(0,0,1672,941);}
   else{
    const edge=-250+(1672+941*.22+500)*s.progress,incoming=s.phase==='wipe-in';
    ctx.fillStyle='#090c1c';ctx.beginPath();
    if(incoming){ctx.moveTo(-300,0);ctx.lineTo(edge,0);ctx.lineTo(edge-941*.22,941);ctx.lineTo(-300,941);}
    else{ctx.moveTo(edge,0);ctx.lineTo(1972,0);ctx.lineTo(1972,941);ctx.lineTo(edge-941*.22,941);}
    ctx.closePath();ctx.fill();
    for(let i=0;i<3;i++){const x=edge+(incoming?-1:1)*i*18;ctx.fillStyle=i===0?'#80d7ff':i===1?'#9664ed':'#ed39bd';ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x+(incoming?-8:8),0);ctx.lineTo(x+(incoming?-8:8)-941*.22,941);ctx.lineTo(x-941*.22,941);ctx.closePath();ctx.fill();}
   }
  }
  if(s.phase==='cut'&&!this.cut){this.cut=true;dispatchEvent(new CustomEvent('arcade-intro-cut'));}
 }
}
