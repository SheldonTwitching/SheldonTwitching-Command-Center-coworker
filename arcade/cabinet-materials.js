// Runtime semantic materials. Source alpha, native pivots and contact shadows remain authoritative.
const cache=new Map(),trimCache=new Map();
function memoTrim(key,build){if(!trimCache.has(key)){if(trimCache.size>=4)trimCache.clear();trimCache.set(key,build());}return trimCache.get(key);}
const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
const clamp=v=>Math.max(0,Math.min(255,Math.round(v)));
function memo(key,build){if(!cache.has(key)){if(cache.size>=160)cache.clear();cache.set(key,build());}return cache.get(key);}
function sourceCanvas(im){const c=document.createElement('canvas');c.dataset.sourceSprite=im.src||im.dataset?.sourceSprite||'';c.width=im.naturalWidth||im.width;c.height=im.naturalHeight||im.height;c.getContext('2d').drawImage(im,0,0);return c;}
// Recolor the existing authored pixels only. No spatial shader, interpolation or new highlights.
function sourceTone(r,g,b,color){
 const value=Math.max(r,g,b)/255,low=Math.min(r,g,b),sat=value?(Math.max(r,g,b)-low)/(value*255):0;
 const targetMax=Math.max(...color),targetMin=Math.min(...color),targetSat=targetMax?(targetMax-targetMin)/targetMax:0;
 const saturation=Math.min(1,sat*targetSat/.72),white=255*value*Math.min(1,targetMax/220);
 return color.map(channel=>clamp(white*(1-saturation+saturation*(channel-targetMin)/(targetMax-targetMin||1))));
}
export function buttonMaterial(im,skin,index,pressed,geometry,eventColor){
 const role=skin.roles[index],override=skin.overrides[index]||{},cap=eventColor||(pressed?override.pressedCap||skin.pressedCap:override.cap||skin[role+'Cap']),rim=pressed?override.pressedRim||skin.pressedRim:override.rim||skin[role+'Rim'];
 return memo('button|'+im.src+'|'+cap+'|'+rim,()=>{const c=sourceCanvas(im),g=c.getContext('2d'),data=g.getImageData(0,0,c.width,c.height),d=data.data,a=rgb(cap),b=rgb(rim),[cx,cy,rx,ry]=geometry.capEllipse;
 for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const i=(y*c.width+x)*4;if(!d[i+3]||Math.max(d[i],d[i+1],d[i+2])<geometry.shadowThreshold)continue;const color=((x-cx)/rx)**2+((y-cy)/ry)**2<=1?a:b,tone=sourceTone(d[i],d[i+1],d[i+2],color);for(let k=0;k<3;k++)d[i+k]=tone[k];}
 g.putImageData(data,0,0);return c;});
}
export function lightVector(settings,delta=[0,0],radius=50){const v=[settings.lightX*radius*4-(settings.followInput?delta[0]:0),settings.lightY*radius*4-(settings.followInput?delta[1]:0),settings.lightZ*radius*4],n=Math.hypot(...v);return v.map(x=>x/n);}
export function sphereMaterial(im,name,settings,geometry,frame,neutralCenter){
 // Each pose already contains authored lighting/dither. Keep that topology verbatim.
 // Directional relighting awaits authored pixel masks; saved light positions remain intact.
 return memo('sphere-palette|'+im.src+'|'+settings.color,()=>{const c=sourceCanvas(im),g=c.getContext('2d'),data=g.getImageData(0,0,c.width,c.height),d=data.data,color=rgb(settings.color),[cx,cy,r]=geometry[name];
 for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const i=(y*c.width+x)*4;if(!d[i+3]||(x-cx)**2+(y-cy)**2>r*r)continue;const tone=sourceTone(d[i],d[i+1],d[i+2],color);for(let k=0;k<3;k++)d[i+k]=tone[k];}
 g.putImageData(data,0,0);return c;});
}
export function indicatorMaterial(im,shape,color,name){
 if(shape==='original'&&!color)return im;
 return memo('indicator|'+im.src+'|'+shape+'|'+color+'|'+name,()=>{const c=document.createElement('canvas');c.width=shape==='original'?im.naturalWidth:44;c.height=shape==='original'?im.naturalHeight:42;const g=c.getContext('2d');
 if(shape==='original'){g.drawImage(im,0,0);g.globalCompositeOperation='source-in';g.fillStyle=color;g.fillRect(0,0,c.width,c.height);return c;}
 const angle={UP:0,RIGHT:Math.PI/2,DOWN:Math.PI,LEFT:-Math.PI/2}[name];g.translate(22,21);g.rotate(angle);g.fillStyle=color||'#ed1750';g.beginPath();
 if(shape==='round')g.arc(0,0,12,0,Math.PI*2);
 else if(shape==='diamond'){g.moveTo(0,-16);g.lineTo(16,0);g.lineTo(0,16);g.lineTo(-16,0);}
 else if(shape==='chevron'){g.moveTo(0,-16);g.lineTo(18,2);g.lineTo(12,9);g.lineTo(0,-3);g.lineTo(-12,9);g.lineTo(-18,2);}
 else if(shape==='pixel'){g.rect(-5,-16,10,8);g.rect(-13,-8,26,8);g.rect(-5,0,10,15);}
 else{g.moveTo(0,-17);g.lineTo(17,1);g.lineTo(7,1);g.lineTo(7,16);g.lineTo(-7,16);g.lineTo(-7,1);g.lineTo(-17,1);}g.closePath();g.fill();return c;});
}
export function trimMaterials(im,rect,zones,color,gap){
 return memoTrim('trim|'+im.src+'|'+color+'|'+gap,()=>{const native=document.createElement('canvas');native.width=2060;native.height=1220;const g=native.getContext('2d');g.drawImage(im,...rect);const zone=document.createElement('canvas');zone.width=2060;zone.height=1220;const z=zone.getContext('2d');for(const points of zones){z.beginPath();points.forEach(([x,y],i)=>i?z.lineTo(x,y):z.moveTo(x,y));z.closePath();z.fill();}g.globalCompositeOperation='destination-in';g.drawImage(zone,0,0);const pixels=g.getImageData(0,0,2060,1220),d=pixels.data,base=rgb(color),mask=document.createElement('canvas');mask.width=2060;mask.height=1220;const m=mask.getContext('2d'),md=m.createImageData(2060,1220);
 for(let i=0;i<d.length;i+=4){if(!d[i+3]||!(d[i]>d[i+1]*1.2&&d[i]>d[i+2]*.8)){d[i+3]=0;continue;}const value=Math.max(d[i],d[i+1],d[i+2])/255;for(let k=0;k<3;k++)d[i+k]=clamp(base[k]*(.22+.78*value));md.data[i+3]=255;}
 g.globalCompositeOperation='source-over';g.putImageData(pixels,0,0);m.putImageData(md,0,0);const gutter=document.createElement('canvas');gutter.width=2060;gutter.height=1220;const q=gutter.getContext('2d'),r=Math.ceil(gap);const expanded=q.createImageData(2060,1220),offsets=[];for(let y=-r;y<=r;y++)for(let x=-r;x<=r;x++)if(x*x+y*y<=r*r)offsets.push([x,y]);for(let y=0;y<1220;y++)for(let x=0;x<2060;x++)if(md.data[(y*2060+x)*4+3])for(const [dx,dy]of offsets){const a=x+dx,b=y+dy;if(a>=0&&a<2060&&b>=0&&b<1220)expanded.data[(b*2060+a)*4+3]=255;}q.putImageData(expanded,0,0);return {ink:native,gutter};});
}
export function restoreTrim(g,base,trim){const c=sourceCanvas(base),b=c.getContext('2d');b.globalCompositeOperation='destination-in';b.drawImage(trim.gutter,0,0);g.save();g.globalCompositeOperation='destination-out';g.drawImage(trim.gutter,0,0);g.globalCompositeOperation='source-over';g.drawImage(c,0,0);g.drawImage(trim.ink,0,0);g.restore();}
