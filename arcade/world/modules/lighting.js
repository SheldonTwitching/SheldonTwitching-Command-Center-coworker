export class Lighting{
 constructor(){this.seen=0;this.pulse=0;this.player=0;this.level=0;this.bass=0;this.time=0;}
 events(events){for(const e of events){if(e.id<=this.seen)continue;if(e.kind==='action'&&e.action!=='block'){this.pulse=e.action==='dragonpunch'?.9:.55;this.player=e.player;}if(e.kind==='hit')this.pulse=.7;if(e.kind==='ko')this.pulse=1;if(e.kind==='palette')this.pulse=.6;this.seen=e.id;}}
 draw(ctx,s,dt,p){this.time+=dt;this.pulse=Math.max(0,this.pulse-dt*2);this.level+=(s.audio.level-this.level)*Math.min(1,dt*8);this.bass+=(s.audio.bass-this.bass)*Math.min(1,dt*8);ctx.save();ctx.globalCompositeOperation='screen';
  // Cabinet attract illumination runs gently at idle; music adds energy only
  // when a real audio signal arrives. Dots stay on existing trim, not screens.
  const breath=.045+.025*Math.sin(this.time*1.7),energy=breath+this.bass*.12+this.pulse*.13;
  ctx.strokeStyle='#80d7ff';ctx.globalAlpha=energy;ctx.lineWidth=3;
  for(const points of [[[318,35],[318,194],[306,245],[317,580],[367,646]],[[1137,63],[1134,183],[1122,231],[1141,542],[1170,587]]]){
   ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.stroke();
  }
  const phase=(this.time*.13)%1;
  // The wall tag and nearby painted surfaces share the marquees' real signal.
  ctx.save();ctx.fillStyle='#80d7ff';ctx.globalAlpha=this.level*.13;
  ctx.beginPath();[[24,181],[94,132],[72,179],[113,173],[74,243],[88,195],[27,217]].forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fill();ctx.restore();
  // Short reflected flecks near the light-emitting trim; never full-room flashes.
  if(this.level>.45){for(let k=0;k<6;k++){const age=(this.time*1.4+k*.19)%1;ctx.globalAlpha=(1-age)*this.level*.25;ctx.fillStyle=k%2?'#9664ed':'#80d7ff';const x=326+(k%2?560:0)+(k%2?1:-1)*age*25,y=140+k*63+age*12;ctx.fillRect(Math.round(x),Math.round(y),2+Math.round(age*3),1);}}
  ctx.fillStyle='#bdefff';ctx.globalAlpha=.35+this.bass*.25;
  for(const x of [316,1135]){const y=Math.round(84+phase*95);ctx.fillRect(x,y,3,8);}
  // Shallow pixel pools under the marquee and the illuminated speaker bridge.
  ctx.fillStyle='#9664ed';for(let j=0;j<5;j++){ctx.globalAlpha=energy*(1-j/6);ctx.fillRect(344,222+j*3,520,2);}
  ctx.fillStyle='#43b5f0';ctx.globalAlpha=.08+this.level*.4;ctx.fillRect(1308,221,109,3);
  // Sparse dust glints in the light shafts; deterministic independent motion.
  for(let k=0;k<12;k++){const x=45+(k*137)%1580,y=90+((k*79+this.time*(4+k%3))%740);ctx.globalAlpha=(.04+.08*Math.max(0,Math.sin(this.time*.9+k)))*(1+this.level);ctx.fillRect(Math.round(x+Math.sin(this.time*.3+k)*5),Math.round(y),2,2);}
  // Localized pixel reflections and illumination, not a full-screen flash.
  const a=this.pulse*.3+this.bass*.16+this.level*.12;ctx.fillStyle=p.color;ctx.globalAlpha=a;ctx.fillRect(343,550,514,3);ctx.fillRect(335,570,547,2);ctx.fillRect(318,65,3,145);ctx.fillRect(889,280,3,280);
  for(let j=0;j<10;j++){ctx.globalAlpha=Math.max(0,a*(1-j/12)*.6);ctx.fillRect(355-j*10,843+j*8,510+j*20,3);}
  ctx.fillStyle=p.accent;for(let j=0;j<12;j++){ctx.globalAlpha=this.level*.25*(1-j/14);ctx.fillRect(1000+j*8,872+j*4,500-j*14,2);}
  // Ceiling tubes and matching patches on floor react to the music's low end.
  ctx.globalAlpha=this.bass*.28;ctx.fillStyle=p.color;ctx.fillRect(320,0,230,5);ctx.fillRect(1260,15,260,5);ctx.fillRect(58,650,64,4);ctx.fillRect(100,695,92,3);ctx.restore();
 }
}
