import {drawButton,drawStick} from './fightstick.js?v=18';
export function attackMechanics(action,elapsed=0,side=0){
 const direction=side?-1:1;
 const wind=elapsed>=.04&&elapsed<.2,press=elapsed>=.2&&elapsed<.46;
 if(action==='idle'||elapsed>.85)return {button:-1,dx:0,dy:0};
 const button=press?({fireball:0,jump:1,dragonpunch:2,block:4}[action]??-1):-1;
 const dx=action==='block'?-direction:wind?0:['fireball','dragonpunch'].includes(action)?direction:0;
 const dy=wind&&['fireball','dragonpunch'].includes(action)?1:['jump','dragonpunch'].includes(action)?-1:0;
 return {button,dx,dy};
}
// The two game sticks mechanically follow the resolved chat attack animation.
export function drawControls(ctx,players,p,energy=0){
 [0,1].forEach(i=>{
  const color=i?p.accent:p.color,action=players[i]?.action||'idle',base=i?786:521;
  const motion=attackMechanics(action,players[i]?.elapsed||0,i),active=motion.button;
  for(let n=0;n<8;n++)drawButton(ctx,base+(n%4)*28+(n<4?8:0),609+Math.floor(n/4)*17,11,n===active,n%4<2?color:'#9664ed',energy);
  ctx.save();ctx.translate(i?741:449,610);ctx.scale(.7,.7);
  drawStick(ctx,0,0,motion.dx,motion.dy,color);ctx.restore();
 });
}
