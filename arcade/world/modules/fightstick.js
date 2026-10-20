function mix(a,b,t){return '#'+[0,1,2].map(i=>Math.round(parseInt(a.slice(1+i*2,3+i*2),16)*(1-t)+parseInt(b.slice(1+i*2,3+i*2),16)*t).toString(16).padStart(2,'0')).join('');}
function oval(ctx,x,y,rx,ry,color){ctx.fillStyle=color;for(let dy=-ry;dy<=ry;dy+=2){const half=Math.floor(rx*Math.sqrt(Math.max(0,1-dy*dy/(ry*ry))));ctx.fillRect(Math.round(x-half),Math.round(y+dy),half*2,2);}}
export function drawButton(ctx,x,y,r,on,color='#43b5f0',energy=0){
 const down=on?4:0;
 if(energy>.01){ctx.save();ctx.globalAlpha=Math.min(.45,energy*.45);oval(ctx,x,y+5,r+7,r*.7,color);ctx.restore();}
 color=mix(color,'#bfeaff',Math.min(.25,energy*.25));
 oval(ctx,x,y+6,r+4,r*.6,'#060914');oval(ctx,x,y+5,r+1,r*.59,'#191827');
 oval(ctx,x,y+3+down,r,r*.56,mix(color,'#0a0920',.66));
 oval(ctx,x,y-1+down,r,r*.55,mix(color,'#0a0920',.2));
 oval(ctx,x,y-4+down,r-2,r*.43,on?'#e6f8ff':color);
 ctx.fillStyle=on?'#fffaff':mix(color,'#ffffff',.7);ctx.fillRect(Math.round(x-r*.6),Math.round(y-r*.4+down),Math.round(r*.85),2);
 ctx.fillStyle=mix(color,'#ffffff',.22);ctx.fillRect(Math.round(x+r*.5),Math.round(y-2+down),2,3);
}
export function drawStick(ctx,x,y,dx,dy,color='#9664ed'){
 oval(ctx,x,y+3,31,13,'#070a15');oval(ctx,x,y,25,10,'#2b2744');oval(ctx,x,y-2,20,7,'#111224');
 const cx=Math.round(x+dx*15),cy=Math.round(y-44+dy*8);
 ctx.strokeStyle='#181725';ctx.lineWidth=10;ctx.beginPath();ctx.moveTo(x,y-2);ctx.lineTo(cx,cy+12);ctx.stroke();
 ctx.strokeStyle='#9f98b8';ctx.lineWidth=5;ctx.stroke();ctx.strokeStyle='#f2e7ff';ctx.lineWidth=1;ctx.stroke();
 const r=22;
 for(let yy=-r;yy<=r;yy+=2)for(let xx=-r;xx<=r;xx+=2){
  if(xx*xx+yy*yy>r*r)continue;
  const light=Math.max(0,1-Math.hypot(xx+8,yy+9)/33),edge=Math.hypot(xx,yy)/r;
  ctx.fillStyle=mix(mix(color,'#100d20',Math.max(0,edge-.5)*.9),'#e8daff',light*.62);ctx.fillRect(cx+xx,cy+yy,2,2);
 }
 ctx.fillStyle='#ede1ff';ctx.fillRect(cx-10,cy-12,6,2);ctx.fillRect(cx-12,cy-10,2,4);
}
