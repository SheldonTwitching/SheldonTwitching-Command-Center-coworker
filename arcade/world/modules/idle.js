// Separate pose sampling and sprite rendering. Feet stay anchored to the floor.
const cycle=[0,0,1,1,2,2,3,3,2,1];
let sheet;
export function sampleIdle(player,time,index=0){
 const hit=player.hitElapsed??-1;
 if(hit>=0&&hit<.24)return {frame:4,offset:(index?1:-1)*8*Math.sin(hit/.24*Math.PI/2),state:'hit'};
 if(hit>=.24&&hit<.75)return {frame:5,offset:(index?1:-1)*8*Math.pow(1-(hit-.24)/.51,2),state:'recover'};
 return {frame:cycle[Math.floor((time+index*.73)*5)%cycle.length],offset:0,state:'idle'};
}
export function drawIdle(ctx,player,time,index,x,bottom=238){
 if(!sheet){sheet=new Image();sheet.src='/arcade/world/assets/fighters-idle-v3.png';}
 if(!sheet.complete||!sheet.naturalWidth)return;
 const pose=sampleIdle(player,time,index),cw=sheet.naturalWidth/6,ch=sheet.naturalHeight/2,h=160,w=cw/ch*h;
 ctx.save();ctx.imageSmoothingEnabled=false;
 // Stable contact shadow makes a breathing/guard loop feel planted, not bobbing.
 ctx.fillStyle='#08041599';ctx.fillRect(x-26,bottom-1,52,4);ctx.fillRect(x-19,bottom+3,38,2);
 ctx.drawImage(sheet,pose.frame*cw,index*ch,cw,ch,Math.round(x+pose.offset-w/2),Math.round(bottom-h*.95),w,h);
 ctx.restore();
}
