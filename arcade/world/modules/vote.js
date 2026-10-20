import {text} from './surface.js?v=18';
import {worldWeather} from './screen-fx.js?v=18';
const room=new Image();room.src='/arcade/world/assets/arcade-room-v16.png';
function cabinet(ctx,x,y,w,h,p){
 ctx.save();ctx.translate(x,y);ctx.scale(w/150,h/200);
 ctx.beginPath();[[20,0],[127,4],[144,128],[137,200],[17,200],[0,39]].forEach(([a,b],i)=>i?ctx.lineTo(a,b):ctx.moveTo(a,b));ctx.closePath();ctx.clip();
 ctx.filter='hue-rotate('+p.hue+'deg)';
 if(room.complete&&room.naturalWidth)ctx.drawImage(room,245,28,750,913,0,0,150,200);
 ctx.restore();
}
export function drawVote(ctx,s,t=0){
 ctx.fillStyle='#10081e';ctx.fillRect(0,0,640,420);
 worldWeather(ctx,t,640,420,.45);
 text(ctx,'ST / TEAM COLOR CLASH',320,39,28,'#fff','center');
 text(ctx,s.locked?'TEAM '+(s.seriesWinner+1)+' CLAIMED THE CABINET':'FIRST TO 3 MATCH WINS CLAIMS THE CAB',320,72,18,'#e7b6de','center');
 (s.teams||[]).forEach((team,i)=>{
  const x=i*320,p=s.palettes[team.palette],color=i?'#45d9ff':'#ff31c8';
  text(ctx,'TEAM '+(i+1),x+160,107,25,color,'center');
  cabinet(ctx,x+102,121+Math.round(Math.sin(t*2+i)),116,159,p);
  text(ctx,p.name,x+160,302,24,p.color,'center');
  text(ctx,(s.matchWins?.[i]||0)+' MATCHES / '+(s.roundWins?.[i]||0)+' ROUNDS',x+160,328,16,color,'center');
  text(ctx,team.members+' VIEWERS',x+160,350,14,'#cfbad8','center');
  team.paletteVotes.forEach((n,j)=>{
   ctx.fillStyle=s.palettes[j].color;ctx.fillRect(x+24+j*73,365,65,20);
   text(ctx,(j+1)+':'+n,x+56+j*73,381,14,'#10081e','center');
  });
 });
 text(ctx,'VS',320,207,23,'#fff','center');
 text(ctx,s.locked?'COLORS LOCKED / EXHIBITION PLAY CONTINUES':'!team 1 / 2    !palette 1 / 2 / 3 / 4',320,411,18,'#dec8ee','center');
}
