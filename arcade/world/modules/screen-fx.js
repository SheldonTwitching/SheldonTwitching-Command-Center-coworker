// Fictional game-world weather stays inside the CRTs, not on indoor furniture.
export function worldWeather(ctx,t,w,h,intensity=1){
 ctx.save();ctx.strokeStyle='#7fa5cf';ctx.lineWidth=1;ctx.globalAlpha=.15*intensity;
 for(let i=0;i<42;i++){
  const x=(i*83+t*(17+i%4))%w,y=(i*47+t*(90+i%9*4))%h;
  ctx.beginPath();ctx.moveTo(Math.round(x),Math.round(y));ctx.lineTo(Math.round(x-3),Math.round(y+8+i%4));ctx.stroke();
 }
 ctx.globalAlpha=.12*intensity;ctx.fillStyle='#a0c6df';
 for(let i=0;i<9;i++){const age=(t*1.1+i*.17)%1;if(age>.3)continue;const x=(i*97)%w,y=h*.78+(i*13)%(h*.2);ctx.fillRect(Math.round(x),Math.round(y),Math.round(3+age*12),1);}
 ctx.restore();
}
export function crt(ctx,t){
 ctx.save();const {width:w,height:h}=ctx.canvas;ctx.fillStyle='#020512';ctx.globalAlpha=.075;
 for(let y=0;y<h;y+=3)ctx.fillRect(0,y,w,1);
 ctx.fillStyle='#96c5e8';ctx.globalAlpha=.018;ctx.fillRect(0,Math.round(t*11)%h,w,2);ctx.restore();
}
