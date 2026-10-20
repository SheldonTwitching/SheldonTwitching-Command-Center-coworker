/* Direction and shaft anchors use source pixels; opposing D-pad inputs cancel. */
(function(root){'use strict';
const pivots={BACK:[49,157],BACK_LEFT:[109,139],BACK_RIGHT:[13,137],FRONT:[49,147],FRONT_LEFT:[111,135],FRONT_RIGHT:[13,135],LEFT:[121,151],NEUTRAL:[49,173],RIGHT:[13,151]};
const sizes={BACK:[100,158],BACK_LEFT:[124,140],BACK_RIGHT:[124,138],FRONT:[100,204],FRONT_LEFT:[126,168],FRONT_RIGHT:[126,168],LEFT:[136,178],NEUTRAL:[100,204],RIGHT:[136,178]};
function direction(pad){const x=Number(pad.includes('DPAD_RIGHT'))-Number(pad.includes('DPAD_LEFT'));const y=Number(pad.includes('DPAD_DOWN'))-Number(pad.includes('DPAD_UP'));return (y<0?'BACK':y>0?'FRONT':'')+(x<0?(y?'_LEFT':'LEFT'):x>0?(y?'_RIGHT':'RIGHT'):'')||'NEUTRAL';}
function frame(name,anchor=[891,1115]){const p=pivots[name],s=sizes[name];return {x:anchor[0]-p[0],y:anchor[1]-p[1],width:s[0],height:s[1]};}
function reflectionDirection(name){return ({BACK:'FRONT',FRONT:'BACK'})[name]||name;}
// Only the uppermost ball arc is allowed to enter the glass; no button reflection.
const ballTop={NEUTRAL:16,BACK:8,BACK_LEFT:8,BACK_RIGHT:6,FRONT:26,FRONT_LEFT:26,FRONT_RIGHT:26,LEFT:12,RIGHT:12};
function reflectionFrame(name,anchorX,glassBottom,scale=1,visible=10){const p=pivots[name],s=sizes[name];return {x:anchorX-p[0]*scale,y:glassBottom-(visible+ballTop[name])*scale,width:s[0]*scale,height:s[1]*scale};}
const api={direction,frame,pivots,sizes,reflectionDirection,reflectionFrame,ballTop};if(typeof module!=='undefined')module.exports=api;else root.ArcadeSprites=api;
})(typeof window==='undefined'?globalThis:window);
