import {drawIdle} from './idle.js?v=18';
let sheet;
const bounds=[
 [[35,75,392,310],[465,263,509,151],[1014,140,285,285],[1433,0,276,438]],
 [[25,504,400,319],[447,700,514,160],[1023,586,288,276],[1421,446,290,435]]
];
export function lossPose(hit,index=0){
 const away=index?1:-1;
 if(hit<0||hit>=3.5)return {state:'idle',offset:0};
 if(hit<.1)return {state:'hitstop',offset:0};
 if(hit<.32)return {state:'hit',offset:away*18*(hit-.1)/.22};
 if(hit<.7)return {state:'falling',frame:0,offset:away*(18+18*(hit-.32)/.38)};
 if(hit<2.5)return {state:'defeated',frame:1,offset:away*36};
 if(hit<3.05)return {state:'rising',frame:2,offset:away*36*(1-(hit-2.5)/.55)};
 return {state:'recover',offset:0};
}
export function attackClock(elapsed){
 // A 100 ms impact freeze; do not advance attacking poses or projectiles through it.
 return elapsed<.95?elapsed:elapsed<1.05?.95:elapsed-.1;
}
export function shakeOffset(hit){
 if(hit<.1||hit>.32)return [0,0];
 let strength=1-(hit-.1)/.22;
 return [Math.round(Math.sin(hit*130)*4*strength),Math.round(Math.cos(hit*110)*2*strength)];
}
function poseSprite(ctx,index,frame,x,bottom,h,width=null){
 if(!sheet){sheet=new Image();sheet.src='/arcade/world/assets/fighters-defeat-v5.png';}
 if(!sheet.complete||!sheet.naturalWidth)return;
 const [sx,sy,sw,sh]=bounds[index][frame],w=width??sw/sh*h;
 ctx.drawImage(sheet,sx,sy,sw,sh,Math.round(x-w/2),Math.round(bottom-h),w,h);
}
export function drawLoss(ctx,player,time,index,x,bottom=238){
 const pose=lossPose(player.hitElapsed,index);
 ctx.fillStyle='#080415bb';ctx.fillRect(x+pose.offset-29,bottom,58,4);
 if(pose.state==='hitstop'||pose.state==='hit'){
  // Hold the recoil pose during hit-stop, then push it away from the impact.
  drawIdle(ctx,{...player,hitElapsed:.1},time,index,x+pose.offset,bottom);
 }else if(pose.state==='falling'){
  const u=(player.hitElapsed-.32)/.38;
  poseSprite(ctx,index,0,x+pose.offset,bottom-12*Math.sin(u*Math.PI),108);
 }else if(pose.state==='defeated'){
  poseSprite(ctx,index,1,x+pose.offset,bottom,46,153);
 }else if(pose.state==='rising'){
  poseSprite(ctx,index,2,x+pose.offset,bottom,110);
 }else{
  drawIdle(ctx,{...player,hitElapsed:pose.state==='recover'?.5:-1},time,index,x,bottom);
 }
}
export function drawVictory(ctx,index,x,bottom=238){poseSprite(ctx,index,3,x,bottom,159);}
export function impactBurst(ctx,hit,x,y,color){
 if(hit<0||hit>.3)return;
 const u=Math.min(1,hit/.3),r=13+u*24;
 ctx.save();ctx.globalAlpha=1-u;ctx.fillStyle=color;
 for(let k=0;k<8;k++){const a=k*Math.PI/4;ctx.fillRect(Math.round(x+Math.cos(a)*r)-4,Math.round(y+Math.sin(a)*r)-4,8,8);}
 ctx.fillStyle='#fff4e9';ctx.fillRect(x-3,y-18*(1-u),6,36*(1-u));ctx.fillRect(x-19*(1-u),y-3,38*(1-u),6);ctx.restore();
}
