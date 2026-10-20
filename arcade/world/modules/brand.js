import {drawMarquee} from '/arcade/graffiti-marquee.js';
let cabinet={};async function poll(){try{cabinet=await(await fetch('/api/arcade/config',{cache:'no-store'})).json();}catch{}setTimeout(poll,1000);}poll();
export function drawBrand(ctx,t=0,energy=0){drawMarquee(ctx,1000,270,cabinet,energy);}
