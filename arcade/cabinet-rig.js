import {FrameClock} from './frame-clock.js';
import {drawMarquee} from './graffiti-marquee.js';
import {buttonMaterial,sphereMaterial,indicatorMaterial,trimMaterials,restoreTrim} from './cabinet-materials.js';
const [spec,structure]=await Promise.all(['/arcade/project-spec.json','/arcade/cabinet-structure.json'].map(u=>fetch(u).then(r=>r.json()))),rig=spec.cabinet;
const query=new URLSearchParams(location.search),nativeView=query.get('view')==='native',view=rig.gameplay;
const canvas=document.getElementById('part'),ctx=canvas.getContext('2d'),part=location.pathname.split('/').pop(),cache=new Map(),frameClock=new FrameClock();
const dimensions=nativeView?rig.nativeCanvas:[1920,1080];[canvas.width,canvas.height]=dimensions||[1920,1080];
let state,env={},energy=0,staticKey='',staticPanel;const lightingPanels=new Map();
function image(file){if(!cache.has(file)){const im=new Image();im.src=file;cache.set(file,im);}return cache.get(file);}
const asset=file=>image('/arcade/assets/'+file),ready=im=>im instanceof HTMLCanvasElement?im.width>0:im.complete&&im.naturalWidth;
function surface(){const c=document.createElement('canvas');[c.width,c.height]=rig.nativeCanvas;return c;}
function polygon(g,points){g.beginPath();points.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.closePath();}
function patch(im,rect){
 if(nativeView){ctx.drawImage(im,...rect);return;}
 const sx=rig.sourceScreenCuts.x,sy=rig.sourceScreenCuts.y,dx=view.targetCuts.x,dy=view.targetCuts.y;
 for(let y=0;y<3;y++)for(let x=0;x<3;x++){if(x===1&&y===1)continue;ctx.drawImage(im,sx[x],sy[y],sx[x+1]-sx[x],sy[y+1]-sy[y],dx[x],dy[y],dx[x+1]-dx[x],dy[y+1]-dy[y]);}
}
const project=(x,y)=>nativeView?[x,y]:[view.glass[0]+(x-rig.nativeGlass[0])*view.controlScale,view.deckOutputY+(y-view.deckNativeY)*view.deckScaleY];
function sprite(im,x,y,w,h,anchor=[x+w/2,y+h/2]){if(!ready(im))return;const [dx,dy]=project(...anchor),scale=nativeView?1:view.controlScale;ctx.drawImage(im,dx-(anchor[0]-x)*scale,dy-(anchor[1]-y)*scale,w*scale,h*scale);}
function cfg(){const c={...state.config};if(structure.presets[query.get('design')])c.cabinetDesign=query.get('design');if(structure.geometry.shapes.includes(query.get('shape')))c.cabinetShape=query.get('shape');return c;}
function mod(c,id){return c.cabinetParts?.[id]||{};}
function paintRegion(g,c,id,points,band){const m=mod(c,id),atlas=image('/arcade/world/assets/'+structure.paintAtlas.file);g.save();polygon(g,points);g.clip();if(m.color){g.globalCompositeOperation='source-atop';g.globalAlpha=.3;g.fillStyle=m.color;g.fillRect(0,0,2060,1220);g.globalAlpha=1;}g.globalCompositeOperation='source-atop';if(m.paint!==false&&ready(atlas)){const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),x=Math.min(...xs),y=Math.min(...ys),w=Math.max(...xs)-x,h=Math.max(...ys)-y;const uv=structure.paintAtlas.bands[band];g.globalAlpha=(m.opacity??(id==='shoulderPaint'?.9:.4));g.drawImage(atlas,uv[0]*atlas.width,uv[1]*atlas.height,uv[2]*atlas.width,uv[3]*atlas.height,x,y,w,h);}g.restore();}
function surfaceInk(g,c,id,region,opacity){
 const atlas=image('/arcade/world/assets/'+structure.paintAtlas.file),m=mod(c,id);if(m.paint===false||!ready(atlas))return;
 const points=region.polygon,xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),x=Math.min(...xs),y=Math.min(...ys),w=Math.max(...xs)-x,h=Math.max(...ys)-y,uv=structure.paintAtlas.bands[region.band],angle=region.rotation*Math.PI/180;
 const sw=uv[2]*atlas.width,sh=uv[3]*atlas.height,vertical=Math.abs(region.rotation)===90,scale=Math.max((vertical?h:w)/sw,(vertical?w:h)/sh);
 g.save();polygon(g,points);g.clip();g.translate(x+w/2,y+h/2);g.rotate(angle);g.globalAlpha=m.opacity??opacity;
 g.drawImage(atlas,uv[0]*atlas.width,uv[1]*atlas.height,sw,sh,-sw*scale/2,-sh*scale/2,sw*scale,sh*scale);g.restore();
}
function reskinDeck(g,c){
 const m=mod(c,'deck');for(const region of structure.panelSurfaces.deck){
 const p=region.polygon;g.save();polygon(g,p);g.clip();
 // Opaque replacement: source stripe print cannot show through the new laminate.
 const shade=g.createLinearGradient(0,1060,0,1180);shade.addColorStop(0,'#0a0814');shade.addColorStop(.08,m.color||c.panelColor);shade.addColorStop(.78,m.color||'#1a1230');shade.addColorStop(1,'#090612');g.fillStyle=shade;g.fillRect(0,1040,2060,160);
 surfaceInk(g,c,'deck',region,.68);
 // Sparse grain and scuffs follow the plane; no inherited bar pattern.
 for(let y=1066;y<1178;y+=4)for(let x=230;x<1825;x+=4){const n=(x*17+y*29)%71;if(n<3){g.fillStyle=n?'#080612':'#ad99d1';g.globalAlpha=n?.18:.07;g.fillRect(x,y,2,1);}}g.globalAlpha=1;
 g.restore();
 g.save();polygon(g,p);g.strokeStyle='#080511';g.lineWidth=3;g.stroke();g.lineWidth=1;g.strokeStyle='#68507c';g.globalAlpha=.45;g.stroke();g.globalAlpha=1;
 for(const [x,y]of region.fasteners){g.fillStyle='#080611';g.fillRect(x-2,y-2,5,5);g.fillStyle='#584a6e';g.fillRect(x-1,y-2,3,1);g.fillStyle='#15101e';g.fillRect(x-1,y,3,1);}g.restore();
 }
}
function paintSurround(g,c){for(const region of structure.panelSurfaces.screenSurround){g.save();polygon(g,region.polygon);g.clip();if(mod(c,'screenSurround').color){g.globalAlpha=.25;g.fillStyle=mod(c,'screenSurround').color;g.fillRect(0,0,2060,1220);g.globalAlpha=1;}surfaceInk(g,c,'screenSurround',region,.55);g.restore();}}
function removeInlayFx(g){g.save();g.globalCompositeOperation='destination-out';for(const region of structure.panelSurfaces.deck){polygon(g,region.polygon);g.fill();}g.restore();}
const tintedArrows=new Map();
function arrowAsset(file,color){const im=asset(file);if(!color||!ready(im))return im;const key=file+'|'+color;if(!tintedArrows.has(key)){const c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;const g=c.getContext('2d');g.drawImage(im,0,0);g.globalCompositeOperation='source-in';g.fillStyle=color;g.fillRect(0,0,c.width,c.height);if(tintedArrows.size>=16)tintedArrows.clear();tintedArrows.set(key,c);}return tintedArrows.get(key);}

function shadeOverhang(g,c){
 const finish=c.surfaceFinish;g.save();g.beginPath();for(const points of [...structure.panelSurfaces.innerReturns.map(p=>p.polygon),...structure.panelSurfaces.screenSurround.map(p=>p.polygon),structure.parts.find(p=>p.id==='shoulderPaint').polygon,structure.parts.find(p=>p.id==='shoulderPaint').polygon.map(([x,y])=>[2060-x,y])]){const area=points.reduce((a,p,i)=>{const q=points[(i+1)%points.length];return a+p[0]*q[1]-q[0]*p[1];},0),ordered=area<0?[...points].reverse():points;ordered.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.closePath();}g.clip();
 const shade=g.createLinearGradient(0,270,0,270+finish.overhangReach);shade.addColorStop(0,'rgba(0,0,0,'+finish.overhangShadow+')');shade.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=shade;g.fillRect(0,270,2060,finish.overhangReach);g.restore();
}

function geometry(g,c){
 const [x,y,w,h]=rig.nativeGlass,b=c.bezelWidth,edge=c.edgeWidth,shape=c.cabinetShape;
 const outline=shape==='square'?[[100,0],[1960,0],[1960,1220],[100,1220]]:[[110,0],[1950,0],[2000,270],[1830,460],[1830,970],[2060,1220],[0,1220],[230,970],[230,460],[60,270]];
 g.save();polygon(g,outline);const shellShade=g.createLinearGradient(0,0,2060,0);shellShade.addColorStop(0,'#080613');shellShade.addColorStop(.16,c.panelColor);shellShade.addColorStop(.5,'#21163a');shellShade.addColorStop(.84,c.panelColor);shellShade.addColorStop(1,'#080613');g.fillStyle=shellShade;g.fill();g.strokeStyle='#080510';g.lineWidth=edge+12;g.stroke();g.strokeStyle=mod(c,'edge').color||c.trimColor;g.lineWidth=edge;g.lineJoin=c.edgeProfile==='rounded'?'round':c.edgeProfile==='flat'?'miter':'bevel';g.stroke();
 if(c.edgeProfile==='beveled'){g.lineWidth=2;g.strokeStyle='#d7d6f0';g.globalAlpha=.35;g.stroke();g.globalAlpha=1;}
 const recess=g.createLinearGradient(0,y-b,0,y+h+b);recess.addColorStop(0,'#110b20');recess.addColorStop(.05,mod(c,'bezel').color||'#3c2861');recess.addColorStop(.16,'#201437');recess.addColorStop(.87,'#1c132c');recess.addColorStop(.97,mod(c,'bezel').color||'#3c2861');recess.addColorStop(1,'#100a1d');g.fillStyle=recess;g.globalAlpha=mod(c,'bezel').opacity??1;
 if(shape==='chamfered'){const cut=20;polygon(g,[[x-b+cut,y-b],[x+w+b-cut,y-b],[x+w+b,y-b+cut],[x+w+b,y+h+b-cut],[x+w+b-cut,y+h+b],[x-b+cut,y+h+b],[x-b,y+h+b-cut],[x-b,y-b+cut]]);}else g.beginPath(),g.rect(x-b,y-b,w+2*b,h+2*b);
 g.fill();g.strokeStyle='#080510';g.lineWidth=10;g.stroke();g.strokeStyle=c.secondaryColor;g.lineWidth=2;g.stroke();g.strokeStyle='#10091f';g.lineWidth=14;g.strokeRect(x-5,y-5,w+10,h+10);g.strokeStyle='#574076';g.lineWidth=2;g.strokeRect(x-9,y-9,w+18,h+18);g.clearRect(x,y,w,h);g.restore();
 // Source deck retains its actual depth, seams, and control mount.
 g.drawImage(asset(rig.asset.file),0,1034,1942,186,59,1034,1942,186);
}
function cabinet(c){
 const original=asset(rig.asset.file),atlas=image('/arcade/world/assets/'+structure.paintAtlas.file);if(!ready(original))return;
 const key=JSON.stringify([c.cabinetDesign,c.cabinetShape,c.edgeProfile,c.edgeWidth,c.bezelWidth,c.cabinetParts,c.panelColor,c.trimColor,c.secondaryColor,c.originalColorMode,c.surfaceFinish,ready(atlas)]);
 if(key!==staticKey){staticPanel=surface();const g=staticPanel.getContext('2d');g.imageSmoothingEnabled=false;
 if(c.cabinetShape==='original'){if(c.cabinetDesign!=='original'&&c.originalColorMode==='glacier')g.filter='hue-rotate(-45deg) saturate(.85)';g.drawImage(original,...rig.asset.rect);g.filter='none';}else geometry(g,c);
 const cleanBase=surface();cleanBase.getContext('2d').drawImage(staticPanel,0,0);
 if(c.cabinetDesign!=='original'){
 if(c.cabinetShape==='original'&&mod(c,'bezel').color){g.save();g.beginPath();g.rect(320,290,1420,745);g.rect(...rig.nativeGlass);g.clip('evenodd');g.globalAlpha=(mod(c,'bezel').opacity??1)*.3;g.fillStyle=mod(c,'bezel').color;g.fillRect(0,0,2060,1220);g.restore();}
 for(const face of structure.panelSurfaces.sideCheeks)surfaceInk(g,c,'sides',face,.55);
 for(const face of structure.panelSurfaces.innerReturns){g.save();polygon(g,face.polygon);g.clip();g.fillStyle=mod(c,'innerReturns').color||'#22183c';g.fillRect(0,270,2060,200);surfaceInk(g,c,'innerReturns',face,.62);g.restore();}
 const shoulder=structure.parts.find(p=>p.id==='shoulderPaint');paintRegion(g,c,'shoulderPaint',shoulder.polygon,'shoulders');paintRegion(g,c,'shoulderPaint',shoulder.polygon.map(([x,y])=>[2060-x,y]).reverse(),'shoulders');
 paintSurround(g,c);
 }
 if(c.cabinetDesign!=='original'&&c.cabinetShape==='original'){g.save();g.globalAlpha=.32;g.globalCompositeOperation='source-atop';g.drawImage(original,...rig.asset.rect);g.restore();}if(c.cabinetDesign!=='original'){reskinDeck(g,c);shadeOverhang(g,c);if(c.cabinetShape==='original')restoreTrim(g,cleanBase,trimMaterials(original,rig.asset.rect,structure.trimZones,mod(c,'edge').color||c.trimColor,c.surfaceFinish.edgeGap));}g.clearRect(...rig.nativeGlass);staticKey=key;
 }
 patch(staticPanel,[0,0,2060,1220]);
}
function controls(kind,c,reflection=false){
 const demo=query.get('pose'),pad=demo?demo==='NEUTRAL'?[]:demo.split('_').map(d=>'DPAD_'+d):(state.dpad||[]),real=ArcadeSprites.direction(pad),direction=reflection?ArcadeSprites.reflectionDirection(real):real;
 let anchor=c.originalPositions?.joystick||rig.joystickPivot;
 if(kind==='joystick'){
 const f=ArcadeSprites.frame(direction,anchor);ctx.save();const m=mod(c,'stickBall');ctx.globalAlpha*=m.opacity??1;
 if(pad.length&&c.reactiveGlow){ctx.shadowColor=c.trimColor;ctx.shadowBlur=6;}
 let im=c.joystickOverrides?.[direction]?image(c.joystickOverrides[direction]):asset(direction+'.png');
 if(c.cabinetDesign!=='original'&&c.ballLighting.enabled&&!c.joystickOverrides?.[direction]&&ready(im)){const neutral=ArcadeSprites.frame('NEUTRAL',anchor),ball=structure.controlGeometry.balls.NEUTRAL;im=sphereMaterial(im,direction,c.ballLighting,structure.controlGeometry.balls,f,[neutral.x+ball[0],neutral.y+ball[1]]);}
 if(reflection){const mount=project(...anchor),glass=nativeView?rig.nativeGlass:view.glass,scale=nativeView?1:view.controlScale,r=ArcadeSprites.reflectionFrame(direction,mount[0],glass[1]+glass[3],scale,c.reflectionVisibleHeight??10);canvas.dataset.reflectionPose=direction;if(ready(im)){const top=ArcadeSprites.ballTop[direction];ctx.drawImage(im,0,top,im.naturalWidth||im.width,(im.naturalHeight||im.height)-top,r.x,r.y+top*scale,r.width,r.height-top*scale);}}else sprite(im,f.x,f.y,f.width,f.height,anchor);ctx.restore();
 }
 if(kind==='buttons')rig.buttons.forEach((position,i)=>{const pressed=(state.pressed||[]).includes(i),event=c.eventAlerts&&state.event?.buttons?.includes(i),on=pressed||event,pos=c.originalPositions?.buttons?.[i]||position,override=on?(event&&state.event.sprite||c.spriteOverrides?.[i]):c.neutralOverrides?.[i];ctx.save();ctx.globalAlpha*=mod(c,'button'+(i+1)).opacity??1;if(on&&c.reactiveGlow){ctx.shadowColor=event?state.event.color:c.pressColors[i];ctx.shadowBlur=c.pressGlowStrength/10*(mod(c,'buttonLight').glow??1);}let im=override?image(override):asset(on?'BUTTON_PRESSED.png':'BUTTON_NEUTRAL.png');if(!override&&c.cabinetDesign!=='original'&&c.buttonSkin.enabled&&ready(im))im=buttonMaterial(im,c.buttonSkin,i,on,structure.controlGeometry.button,event?state.event.color:null);const travel=on&&!override?structure.controlGeometry.button.pressedTravel:0;sprite(im,pos[0],pos[1]+travel,78,66-travel,[pos[0]+39,pos[1]+33]);ctx.restore();});
 if(kind==='arrows'){ctx.save();ctx.globalAlpha*=mod(c,'arrows').opacity??1;for(const [name,pos]of Object.entries(rig.arrows)){if(!pad.includes('DPAD_'+name))continue;ctx.shadowColor=c.leverIndicators.colors[name]||mod(c,'arrows').color||c.trimColor;ctx.shadowBlur=mod(c,'arrows').glow*10||0;const im=asset('ARROW_'+({LEFT:'L',RIGHT:'R'}[name]||name)+'.png'),color=c.leverIndicators.colors[name]||mod(c,'arrows').color;if(ready(im)){const icon=indicatorMaterial(im,c.leverIndicators.shape,color,name),size=c.leverIndicators.shape==='original'?structure.controlGeometry.arrowSizes[name]:[44,42];sprite(icon,...pos,...size);}}ctx.restore();}
}
function layer(name,c){
 const design=c.cabinetDesign;
 if(name==='cabinet')cabinet(c);
 if(name==='marquee'){
 const r=nativeView?structure.marqueeFace.bounds:view.marqueeRect;
 if(design==='original'||c.marqueeStyle==='classic'){
 const im=asset('MARQUEE.png');if(ready(im)){if(nativeView)ctx.drawImage(im,0,0,2030,270,15,0,2030,270);else ctx.drawImage(im,170,5,1700,235,...r);}
 }else{ctx.save();if(nativeView)polygon(ctx,structure.marqueeFace.polygon);else{ctx.beginPath();ctx.rect(...r);}ctx.clip();ctx.translate(r[0],r[1]);drawMarquee(ctx,r[2],r[3],c,energy);ctx.restore();}
 }
 if(name==='lighting'){
 const im=asset('FX.png');if(ready(im)){const key=design+'|'+c.trimColor+'|'+c.cabinetShape+'|'+c.edgeWidth+'|'+c.edgeProfile+'|'+(mod(c,'edge').color||'');let temp=lightingPanels.get(key);if(!temp){temp=surface();const g=temp.getContext('2d');
 if(c.cabinetShape==='original'){g.drawImage(im,15,0,2030,1220);if(design!=='original')g.clearRect(0,0,2060,270);}else{const points=c.cabinetShape==='square'?[[100,0],[1960,0],[1960,1220],[100,1220]]:[[110,0],[1950,0],[2000,270],[1830,460],[1830,970],[2060,1220],[0,1220],[230,970],[230,460],[60,270]];polygon(g,points);g.strokeStyle=mod(c,'edge').color||c.trimColor;g.lineWidth=c.edgeWidth;g.lineJoin=c.edgeProfile==='rounded'?'round':'bevel';g.stroke();}
 if(design!=='original')removeInlayFx(g);if(design!=='original'||mod(c,'edge').color){g.globalCompositeOperation='source-in';g.fillStyle=mod(c,'edge').color||c.trimColor;g.fillRect(0,0,2060,1220);}g.clearRect(...rig.nativeGlass);if(lightingPanels.size>=4)lightingPanels.clear();lightingPanels.set(key,temp);} ctx.save();ctx.globalAlpha=(.3+energy*(mod(c,'edge').glow??1)*.7)*(mod(c,'edge').opacity??1);patch(temp,[0,0,2060,1220]);ctx.restore();}
 }
 if(['buttons','joystick','arrows'].includes(name))controls(name,c);
 if(name==='reflection'&&c.joystickReflection){ctx.save();ctx.beginPath();const glass=nativeView?rig.nativeGlass:view.glass,visible=(c.reflectionVisibleHeight??10)*(nativeView?1:view.controlScale);ctx.rect(glass[0],glass[1]+glass[3]-visible,glass[2],visible);ctx.clip();ctx.globalAlpha=c.joystickReflectionOpacity/100*(mod(c,'reflection').opacity??1);controls('joystick',c,true);ctx.restore();}
}
function fit(){const scale=Math.min(innerWidth/canvas.width,innerHeight/canvas.height);canvas.style.transform='scale('+scale+')';canvas.style.left=(innerWidth-canvas.width*scale)/2+'px';canvas.style.top=(innerHeight-canvas.height*scale)/2+'px';}fit();addEventListener('resize',fit);
async function poll(){try{[state,env]=await Promise.all(['/api/arcade/live','/api/studio/environment'].map(u=>fetch(u,{cache:'no-store'}).then(r=>r.json())));}catch{}setTimeout(poll,80);}poll();
function draw(now){const dt=frameClock.sample(now,env.motion?.fps||30);if(dt===null){requestAnimationFrame(draw);return;}const target=env.audio?.connected?env.audio.level:0;energy+=(target-energy)*Math.min(1,dt*(target>energy?24:6));ctx.clearRect(0,0,canvas.width,canvas.height);ctx.imageSmoothingEnabled=false;if(state){const c=cfg();canvas.dataset.design=c.cabinetDesign;canvas.dataset.shape=c.cabinetShape;for(const name of c.layerOrder||rig.layersBackToFront)if(part==='all'||part===name)layer(name,c);canvas.dataset.ready=String(cache.size>0&&[...cache.values()].every(ready));}requestAnimationFrame(draw);}requestAnimationFrame(draw);
