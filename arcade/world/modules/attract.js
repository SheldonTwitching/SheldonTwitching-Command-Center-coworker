import {surface,text} from './surface.js?v=18';
// One independently timed renderer per background machine, never a baked video.
const quads=[[[0,336],[49,348],[61,423],[4,418]],[[85,356],[122,363],[120,426],[78,418]],[[142,374],[158,377],[155,422],[136,419]],[[173,382],[187,384],[183,420],[168,418]],[[199,390],[210,392],[205,420],[194,418]],[[219,397],[232,398],[227,424],[215,422]],[[890,357],[911,358],[914,433],[891,433]],[[930,374],[948,377],[938,435],[921,434]],[[971,379],[1008,381],[997,435],[954,434]]];
export function createAttract(){return quads.map((q,i)=>({ctx:surface(96,112,q),phase:i*2.71,kind:i%3}));}
export function drawAttract(machines,t,palette){machines.forEach(({ctx,phase,kind})=>{let a=t+phase;ctx.fillStyle='#0b0820';ctx.fillRect(0,0,96,112);ctx.fillStyle=palette.color;
  if(kind===0){for(let j=0;j<16;j++){let x=(j*31+phase*13)%96,y=(j*17+a*17)%90;ctx.fillRect(x|0,y|0,2,3);}ctx.fillStyle=palette.accent;let x=43+Math.sin(a*.8)*25;ctx.fillRect(x,82,12,5);ctx.fillRect(x+4,77,4,5);for(let j=0;j<4;j++)ctx.fillRect(12+j*20,20+Math.sin(a+j)*5,9,6);}
  if(kind===1){ctx.fillRect(5,40+Math.sin(a)*27,3,20);ctx.fillRect(88,40+Math.sin(a+1)*27,3,20);ctx.fillStyle=palette.accent;ctx.fillRect(45+Math.sin(a*1.4)*35,46+Math.cos(a*1.8)*33,4,4);}
  if(kind===2){for(let j=0;j<18;j++){ctx.fillStyle=j%2?palette.color:palette.accent;ctx.fillRect(8+(j%6)*13,12+Math.floor(j/6)*10,10,6);}let x=40+Math.sin(a)*28;ctx.fillRect(x,85,24,4);ctx.fillRect(45+Math.sin(a*1.2)*34,55+Math.cos(a)*25,3,3);}
  text(ctx,'ST',48,108,10,palette.accent,'center');});}
