import {drawButton,drawStick} from './fightstick.js?v=18';
// Real local controller input, independent of chat-game attacks. Fightstick only.
export class InputViewer {
 constructor(){this.native=null;this.received=0;const poll=async()=>{try{const r=await fetch('/api/arcade/live',{cache:'no-store'});if(r.ok){this.native=await r.json();this.received=performance.now();}}catch{}this.timer=setTimeout(poll,40);};poll();}

 draw(ctx){
  const live=this.native&&performance.now()-this.received<500?this.native:{pressed:[],dpad:[]};
  const pressed=n=>live.pressed.includes(n),pad=live.dpad||[];
  const dx=Number(pad.includes('DPAD_RIGHT'))-Number(pad.includes('DPAD_LEFT'));
  const dy=Number(pad.includes('DPAD_DOWN'))-Number(pad.includes('DPAD_UP'));
  this.dx=dx;this.dy=dy;
  ctx.clearRect(0,0,600,100);ctx.imageSmoothingEnabled=false;
  // Standard mapping; validate with the user's actual controller.
  [0,1,2,3,4,5,6,7].forEach((n,i)=>drawButton(ctx,278+(i%4)*49+(i<4?12:0),i<4?28:70,19,pressed(n),i%4<2?'#43b5f0':'#9664ed',this.energy||0));
  drawButton(ctx,548,50,12,pressed(8),'#80d7ff');
 }
 drawPhysicalStick(ctx,x=1240,y=573,scale=.8){
  // The balltop stands above the deck. Projecting it into the deck plane
  // would incorrectly flatten a spherical object along with the panel.
  ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);
  drawStick(ctx,0,0,this.dx||0,this.dy||0,'#9664ed');ctx.restore();
 }
}
