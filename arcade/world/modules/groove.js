import {text} from './surface.js?v=18';
export class Groove{
 constructor(){this.level=0;this.peak=0;this.time=0;this.bars=Array(32).fill(0);this.caps=Array(32).fill(0);}
 update(audio,dt){
  this.time+=dt;const target=Math.max(0,Math.min(1,audio?.level||0));
  this.level+=(target-this.level)*Math.min(1,dt*(target>this.level?20:5));
  this.peak=Math.max(this.level,this.peak-dt*.45);
  for(let i=0;i<32;i++){
   // Choreographed amplitude columns, not claimed frequency spectrum bins.
   const envelope=.24+.76*Math.abs(Math.sin(i*.41+this.time*(1.4+i%4*.22)));
   const value=this.level*envelope;
   this.bars[i]+=(value-this.bars[i])*Math.min(1,dt*(value>this.bars[i]?23:7));
   this.caps[i]=Math.max(this.bars[i],this.caps[i]-dt*.32);
  }
 }
 marquee(ctx){
  ctx.fillStyle='#070c19';ctx.fillRect(0,0,500,110);
  text(ctx,'ST / SOUND SYSTEM',250,18,14,'#bd9fe6','center');
  for(let i=0;i<32;i++){
   const h=Math.round(this.bars[i]*69),cap=Math.round(this.caps[i]*69);
   ctx.fillStyle='#20253c';ctx.fillRect(27+i*14,29,9,66);
   for(let y=0;y<h;y+=5){ctx.fillStyle=y>45?'#d38bff':y>22?'#6e8dff':'#43b5f0';ctx.fillRect(27+i*14,92-y,9,3);}
   if(cap>3){ctx.fillStyle='#e3f7ff';ctx.fillRect(27+i*14,90-cap,9,2);}
   ctx.globalAlpha=.12;ctx.fillStyle='#43b5f0';ctx.fillRect(27+i*14,98,9,Math.min(7,h*.12));ctx.globalAlpha=1;
  }
  ctx.fillStyle='#9664ed';ctx.globalAlpha=.25+this.level*.6;ctx.fillRect(20,24,460,1);ctx.fillRect(20,107,460,2);ctx.globalAlpha=1;
 }
 screen(ctx){
  ctx.save();ctx.strokeStyle='#80d7ff';ctx.globalAlpha=.12+this.level*.6;ctx.lineWidth=2;ctx.strokeRect(3,3,634,414);
  for(let i=0;i<14;i++){const on=i<this.level*14;ctx.fillStyle=i>10?'#b589ff':'#43b5f0';ctx.globalAlpha=on?.75:.06;ctx.fillRect(6,395-i*21,5,14);ctx.fillRect(629,395-i*21,5,14);}ctx.restore();
 }
 deck(ctx,t){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(const [x,y,w] of [[383,640,558],[1191,589,416]]){
   ctx.fillStyle='#80d7ff';ctx.globalAlpha=.16+this.level*.5;ctx.fillRect(x,y,w,2);
   for(let i=0;i<24;i++){const phase=(t*.32+i/24)%1;ctx.globalAlpha=.05+Math.pow(Math.max(0,Math.sin(phase*Math.PI)),8)*(.2+this.level*.5);ctx.fillStyle=i%3?'#43b5f0':'#9664ed';ctx.fillRect(x+i*(w/24),y-4,Math.max(3,w/24-5),2);}
  }
  // Low-angle lacquer glints travel across each sloped art panel.
  for(const points of [[[351,586],[900,582],[947,636],[368,643]],[[1158,545],[1585,545],[1624,590],[1183,590]]]){
   ctx.save();ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.clip();
   const start=points[0][0],width=points[1][0]-start,px=start+((t*.11)%1)*(width+100)-50;
   ctx.globalAlpha=.10+this.level*.18;ctx.fillStyle='#bfe9ff';ctx.beginPath();ctx.moveTo(px,530);ctx.lineTo(px+10,530);ctx.lineTo(px+60,650);ctx.lineTo(px+50,650);ctx.closePath();ctx.fill();ctx.restore();
  }
  ctx.restore();
 }
}
