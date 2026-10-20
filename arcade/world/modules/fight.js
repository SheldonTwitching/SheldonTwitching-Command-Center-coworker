import {stageFrame} from '/arcade/stages.js';
let environment={};async function environmentPoll(){try{environment=await(await fetch('/api/studio/environment',{cache:'no-store'})).json();}catch{}setTimeout(environmentPoll,2000);}environmentPoll();
import {text} from './surface.js?v=18';
import {drawIdle} from './idle.js?v=18';
import {worldWeather} from './screen-fx.js?v=18';
import {drawLoss,drawVictory,lossPose,attackClock,shakeOffset,impactBurst} from './impact.js?v=18';
const idle=new Image();idle.src='/arcade/world/assets/fighters.png';
const attacks=new Image();attacks.src='/arcade/world/assets/fighters-moves-v2.png';
const arena=new Image();arena.src='/arcade/world/assets/fighting-arena-v6.png';
const oldBounds=[[[8,150,254,434],[287,159,344,425]],[[10,714,265,432],[260,736,365,410]]];
// Individual source rectangles preserve the complete generated silhouettes.
const poses=[
 {fireball:[0,235,410,370],jump:[383,165,380,279],dragonpunch:[775,50,209,542],block:[996,229,248,373]},
 {fireball:[0,839,405,370],jump:[331,769,383,279],dragonpunch:[731,661,218,540],block:[993,839,255,373]}
];
function sprite(ctx,img,b,x,bottom,h,alpha=1){
 if(!img.complete||!img.naturalWidth)return;
 const [sx,sy,sw,sh]=b,w=sw/sh*h;ctx.save();ctx.globalAlpha=alpha;ctx.drawImage(img,sx,sy,sw,sh,Math.round(x-w/2),Math.round(bottom-h),w,h);ctx.restore();
}
function projectile(ctx,x,y,color,dir,t){
 ctx.fillStyle=color;ctx.fillRect(x-10,y-8,23,16);ctx.fillRect(x-6,y-12,16,24);
 for(let j=0;j<4;j++)ctx.fillRect(x-dir*(16+j*8),y-5+((j+Math.floor(t*18))%3)*3,7,5);
 ctx.fillStyle='#fff9ef';ctx.fillRect(x-3,y-5,11,10);ctx.fillRect(x+dir*5,y-2,5,4);
}
export function drawFight(ctx,s,t,p){
 const sincePoll=Math.max(0,(performance.now()-(s._receivedAt||performance.now()))/1000);
 const rawElapsed=s.revealElapsed+sincePoll;
 const elapsed=attackClock(rawElapsed),revealing=s.phase==='reveal';
 const fighters=s.displayPlayers||s.players;
 const struck=fighters.find(f=>f.hitElapsed>=0&&f.hitElapsed<.8);
 const hitTime=struck?struck.hitElapsed+sincePoll:-1;
 const [shakeX,shakeY]=shakeOffset(hitTime);
 ctx.save();ctx.translate(shakeX,shakeY);
 ctx.fillStyle='#110a24';ctx.fillRect(0,0,512,300);
 ctx.imageSmoothingEnabled=false;
 stageFrame(ctx,512,300,t,{...environment,motion:s.motion||environment.motion,audio:{...s.audio,connected:s.audioConnected}});
 // Quiet HUD backplates keep the detailed stage readable under match information.
 ctx.fillStyle='#100d20e8';ctx.fillRect(0,0,512,96);ctx.fillRect(0,256,512,44);
 ctx.fillStyle='#6540c5';ctx.fillRect(0,95,512,1);
 ctx.fillStyle='#43b5f0';ctx.fillRect(0,256,512,1);
 text(ctx,'ST / TEAM CLASH',256,16,11,p.accent,'center');
 text(ctx,'MATCH '+(s.matchIndex||1)+'/5  ROUND '+(s.roundIndex||1)+'/3',256,34,11,'#fff','center');
 text(ctx,'MATCH WINS '+(s.matchWins||[0,0]).join(' : '),256,48,10,p.accent,'center');
 const progress=Math.min(1,elapsed/2);
 fighters.forEach((f,i)=>{
  f={...f,hitElapsed:f.hitElapsed>=0?f.hitElapsed+sincePoll:-1};
  let color=i?p.accent:p.color,side=i?-1:1;
  text(ctx,f.name.slice(0,21),i?496:16,58,12,color,i?'right':'left');
  for(let hit=0;hit<3;hit++){ctx.fillStyle=hit<3-(f.hits||0)?color:'#503149';ctx.fillRect((i?292:20)+hit*68,67,62,8);}
  const votes=s.teams?.[i]?.moveVotes||0;
  const label=s.phase==='entry'?'STANDBY':s.phase==='bot_choose'?(f.bot?'CPU PICKING...':'VOTES LOCKED'):s.phase==='choose'?('RW '+(s.roundWins?.[i]||0)+'/2 | '+(f.bot?'CPU':votes+' VOTES')):'ROUND WINS '+(s.roundWins?.[i]||0)+'/2';
  text(ctx,label,i?496:16,89,10,color,i?'right':'left');
  let x=i?347:165,bottom=238,h=145;
  if(f.defeated&&f.hitElapsed>=0&&lossPose(f.hitElapsed,i).state!=='idle'){
   drawLoss(ctx,f,t,i,x,bottom);
  }else if(!f.defeated&&f.hitElapsed>=0&&f.hitElapsed<.75){
   drawIdle(ctx,f,t,i,x,bottom);
  }else if(s.phase==='result'&&s.nextKind!=='exchange'&&s.winner===i&&rawElapsed<3.2){
   drawVictory(ctx,i,x,bottom);
  }else if(revealing&&elapsed<1.7&&!(s.winner!==null&&i!==s.winner&&elapsed>=.95)){
   if(f.action==='jump'){x+=side*Math.sin(progress*Math.PI)*75;bottom-=Math.sin(progress*Math.PI)*88;h=99;}
   if(f.action==='dragonpunch'){x+=side*Math.sin(progress*Math.PI)*24;bottom-=Math.sin(progress*Math.PI)*54;h=172;}
   if(f.action==='block')h=145;
   // Cast burst first, then a travelling projectile detached from the fighter.
   if(f.action==='fireball'&&progress>.16){sprite(ctx,idle,oldBounds[i][1],x,bottom,145);}
   else sprite(ctx,attacks,poses[i][f.action]||poses[i].block,x,bottom,h);
   if(f.action==='fireball'&&progress>.12&&progress<.82){
    let travel=Math.min(1,(progress-.12)/.7);projectile(ctx,x+side*(37+travel*193),179,color,side,t);
   }
   if(f.action==='dragonpunch'){ctx.fillStyle=color;for(let k=0;k<4;k++)ctx.fillRect(x-side*(10+k*4),bottom+4+k*6,5,3);}
  }else{drawIdle(ctx,f,t,i,x,bottom);}
 });
 if(struck){const index=fighters.indexOf(struck);impactBurst(ctx,hitTime,index?331:181,160,index?p.color:p.accent);}
 if(revealing&&s.winner===null&&rawElapsed>.95&&rawElapsed<1.2){impactBurst(ctx,rawElapsed-.95,256,165,'#84f5ff');}
 if(s.phase==='entry'&&fighters.length){
  text(ctx,'JOIN YOUR TEAM / !team 1 OR !team 2',256,254,12,p.color,'center');
 }else if(s.phase==='entry'){
  ctx.fillStyle='#110a24ee';ctx.fillRect(16,96,480,151);
  text(ctx,'ENTER THE NEXT DUEL',256,127,24,p.color,'center');
  text(ctx,'RANDOM DRAW IN '+s.phaseRemaining,256,157,17,'#fff','center');
  text(ctx,'!join OR SEND AN ATTACK',256,184,14,p.accent,'center');
  text(ctx,'ONE VIEWER? FACE DAIGOTRON9000',256,215,12,'#d3a9d5','center');
 }
 if(s.phase==='choose'){text(ctx,'TEAM VOTE / '+s.phaseRemaining,256,112,18,'#fff','center');}
 if(s.phase==='bot_choose'){text(ctx,'DAIGOTRON IS PICKING...',256,112,16,p.accent,'center');}
 if(s.phase==='result'){ctx.fillStyle='#12081def';ctx.fillRect(17,239,478,20);text(ctx,s.result.slice(0,32),256,254,15,'#fff','center');}
 text(ctx,'!fireball  !jump  !dragonpunch  !block',256,267,12,p.accent,'center');
 text(ctx,'JUMP > FIREBALL > DRAGONPUNCH > JUMP',256,284,10,'#ebcbe8','center');
 text(ctx,(s.demo?'DEMO / ':'')+'!team 1 / !team 2  |  '+s.queue+' VOTERS',256,298,9,'#d3a9d5','center');
 ctx.restore();
}
