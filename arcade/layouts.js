export const projectSpec=await fetch('/arcade/project-spec.json').then(r=>r.json());
export function defaultLayout(scene,vertical){
 if(vertical)return {cabinet:[0,160,1080,640],camera:[24,900,660,590],chat:[712,900,344,590],labels:[24,1560,1032,138],spotify:[24,1730,1032,160],game:[24,220,1032,580],title:[24,30,1032,115]};
 if(scene==='gameplay')return {cabinet:[0,0,1920,1080],camera:[1490,760,420,310],chat:[24,380,160,440],labels:[24,2,750,150],spotify:[1250,935,650,130],game:[...projectSpec.cabinet.gameplay.glass],title:[24,2,1400,120]};
 return {cabinet:[0,144,1480,876],camera:[1520,164,376,212],chat:[1520,440,376,600],labels:[24,20,900,180],spotify:[1050,20,570,115],game:[70,180,1330,748],title:[30,20,1350,130]};
}
export function glassOnCanvas(rect,measured=false){if(measured){const [x,y,w,h]=rect,g=projectSpec.cabinet.gameplay.glass,s=Math.min(w/1920,h/1080);return [x+(w-1920*s)/2+g[0]*s,y+(h-1080*s)/2+g[1]*s,g[2]*s,g[3]*s];}const [x,y,w,h]=rect,s=Math.min(w/2060,h/1220);return [x+(w-2060*s)/2+403*s,y+(h-1220*s)/2+340*s,1254*s,646*s];}
export function captureFit(rect,aspect,mode){const [x,y,w,h]=rect,s=mode==='fill'?Math.max(w/aspect,h):Math.min(w/aspect,h);return [x+(w-aspect*s)/2,y+(h-s)/2,aspect*s,s];}
