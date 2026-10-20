const assert=require('node:assert/strict');
const fs=require('node:fs');
const {FrameClock}=new Function(fs.readFileSync('arcade/frame-clock.js','utf8').replace('export class','class')+';return {FrameClock};')();
for(const refresh of [60,120,144])for(const fps of [24,30,60]){const clock=new FrameClock();let frames=0;for(let n=1;n<=refresh*10;n++)if(clock.sample(n*1000/refresh,fps)!==null)frames++;assert.ok(Math.abs(frames-fps*10)<=1,`${fps} fps at ${refresh} Hz produced ${frames}`);}
console.log('24/30/60 fps pacing verified across 60/120/144 Hz, including fractional frame remainders.');
