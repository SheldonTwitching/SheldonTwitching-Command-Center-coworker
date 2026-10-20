// Shared pixel-art material language: cropped cabinet vinyl, hard bevels,
// broken neon edges and a quiet text well. No character portraits or chrome.
const plate=new Image();plate.src='/arcade/world/assets/arcade-room-v16.png';
export const nameplateReady=new Promise(resolve=>{if(plate.complete)resolve();else{plate.addEventListener('load',resolve,{once:true});plate.addEventListener('error',resolve,{once:true});}});
export function nameplate(ctx,x,y,w,h,accent='#80d7ff'){
 ctx.save();ctx.translate(x,y);
 ctx.fillStyle='#080b17';ctx.beginPath();[[10,0],[w-18,0],[w,14],[w,h-9],[w-10,h],[0,h],[0,10]].forEach(([a,b],i)=>i?ctx.lineTo(a,b):ctx.moveTo(a,b));ctx.closePath();ctx.fill();ctx.clip();
 if(plate.complete&&plate.naturalWidth){ctx.globalAlpha=.85;ctx.drawImage(plate,1165,546,445,48,0,0,w,h);ctx.globalAlpha=1;}
 // Graffiti shows around the rim; central information remains readable.
 ctx.fillStyle='#0b0c1bef';ctx.beginPath();ctx.moveTo(64,9);ctx.lineTo(w-27,9);ctx.lineTo(w-10,22);ctx.lineTo(w-10,h-12);ctx.lineTo(76,h-12);ctx.lineTo(64,h-25);ctx.closePath();ctx.fill();
 ctx.fillStyle='#8ab1cb';ctx.fillRect(12,0,w-42,2);ctx.fillStyle='#080a15';ctx.fillRect(0,h-5,w,5);
 ctx.fillStyle=accent;ctx.fillRect(11,3,w*.28,2);ctx.fillRect(w-29,17,3,h-30);
 ctx.fillStyle='#9664ed';ctx.fillRect(w*.52,h-7,w*.37,2);
 ctx.fillStyle='#d3b6ff';for(const [a,b] of [[9,10],[w-13,h-13]]){ctx.fillRect(a,b,3,3);ctx.fillStyle='#353149';ctx.fillRect(a+1,b+1,1,1);}
 ctx.restore();
}
