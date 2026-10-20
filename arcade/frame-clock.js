// Preserve fractional remainder: 24 fps on a 60 Hz display must not collapse to 20.
export class FrameClock {
 constructor(){this.phase=0;this.drawAt=0;}
 sample(now,fps=30){
  const period=1000/([24,30,60].includes(fps)?fps:30),elapsed=now-this.phase;
  if(elapsed+.001<period)return null;
  this.phase=now-((elapsed+.001)%period);
  const dt=this.drawAt?Math.min(.1,(now-this.drawAt)/1000):period/1000;
  this.drawAt=now;return dt;
 }
}
