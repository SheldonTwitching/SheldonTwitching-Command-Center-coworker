const assert=require('node:assert/strict');const {direction,frame,pivots}=require('../arcade/sprites.js');
for(const [inputs,expected] of [[[],'NEUTRAL'],[['UP'],'BACK'],[['DOWN'],'FRONT'],[['LEFT'],'LEFT'],[['RIGHT'],'RIGHT'],[['UP','LEFT'],'BACK_LEFT'],[['UP','RIGHT'],'BACK_RIGHT'],[['DOWN','LEFT'],'FRONT_LEFT'],[['DOWN','RIGHT'],'FRONT_RIGHT'],[['UP','DOWN','LEFT','RIGHT'],'NEUTRAL']]){assert.equal(direction(inputs.map(d=>'DPAD_'+d)),expected);const r=frame(expected);assert.equal(r.x+pivots[expected][0],891);assert.equal(r.y+pivots[expected][1],1115);}
assert.deepEqual(frame('NEUTRAL'),{x:842,y:942,width:100,height:204});assert.equal(frame('BACK_LEFT',[900,1120]).x,791);console.log('Arcade sprites: nine directions, opposing inputs, native dimensions and shaft anchoring passed.');

const {reflectionDirection}=require('../arcade/sprites.js');
assert.equal(reflectionDirection('BACK'),'FRONT');assert.equal(reflectionDirection('FRONT'),'BACK');assert.equal(reflectionDirection('NEUTRAL'),'NEUTRAL');
for(const d of ['LEFT','RIGHT','BACK_LEFT','BACK_RIGHT','FRONT_LEFT','FRONT_RIGHT'])assert.equal(reflectionDirection(d),d);
const rp=frame(reflectionDirection('NEUTRAL'),[891,1972-1115]);assert.equal(rp.y,684);assert.equal(rp.y+pivots.NEUTRAL[1],857);
console.log('Reflection: only vertical pose exchange; neutral upright, original pivots retained.');

const {reflectionFrame,ballTop}=require('../arcade/sprites.js');
for(const dir of Object.keys(pivots)){
 const r=reflectionFrame(dir,891,986,1,10);assert.equal(r.y+ballTop[dir],976);assert.equal(r.x+pivots[dir][0],891);
 const projected=reflectionFrame(dir,800,906,1.2288676236044658,10);assert.ok(Math.abs(projected.y+ballTop[dir]*1.2288676236044658-(906-12.288676236044658))<1e-8);
}
console.log('Reflection stays on the bottom glass edge: 10 native pixels, no button duplication.');

const psdEvidence=require('../docs/psd-reference/inventory.json');
for(const layer of psdEvidence.documents[0].layers.filter(l=>l.path.startsWith('/3:BALL/'))){const r=frame(layer.name);assert.deepEqual([r.x,r.y,r.x+r.width,r.y+r.height],layer.bounds,'PSD pose bounds: '+layer.name);}
console.log('All nine runtime poses agree with the original PSD bounds and shared shaft pivot.');
