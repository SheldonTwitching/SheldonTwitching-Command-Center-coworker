const wordmark=new Image();wordmark.src='/arcade/world/assets/logo-glacier-violet.png';
const atlas=new Image();atlas.src='/arcade/world/assets/cabinet1-paint-atlas-v1.png';
const boundCache=new WeakMap();
function inkBounds(wordmark){
 let bounds=boundCache.get(wordmark);
 if(bounds||!wordmark.complete||!wordmark.naturalWidth)return bounds;
 const c=document.createElement('canvas');c.width=wordmark.naturalWidth;c.height=wordmark.naturalHeight;const g=c.getContext('2d',{willReadFrequently:true});g.drawImage(wordmark,0,0);const pixels=g.getImageData(0,0,c.width,c.height).data;let x0=c.width,y0=c.height,x1=0,y1=0;
 for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++)if(pixels[(y*c.width+x)*4+3]>8){x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
 bounds=[x0,y0,x1-x0+1,y1-y0+1];boundCache.set(wordmark,bounds);return bounds;
}
// Approved lettering is immutable: uniform contain-fit only. Compose paint around the logo.
// One shared painted marquee surface for native cabinet and room projection.
export function drawMarquee(ctx,w,h,colors={},energy=0){
 ctx.save();ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,w,h);ctx.fillStyle=colors.panelColor||'#100d20';ctx.fillRect(0,0,w,h);
 const mods=colors.cabinetParts||{},paint=mods.marqueePaint||{},logo=mods.logo||{};
 if(paint.paint!==false&&atlas.complete&&atlas.naturalWidth){ctx.globalAlpha=paint.opacity??1;ctx.drawImage(atlas,0,0,atlas.naturalWidth,atlas.naturalHeight*.365,0,0,w,h);}
 const fittedWordmark=wordmark,b=inkBounds(fittedWordmark);if(b){ctx.globalAlpha=logo.opacity??1;const scale=Math.min(w*(colors.logoScale??.97)/b[2],h*.96/b[3]),width=b[2]*scale,height=b[3]*scale;ctx.shadowColor=colors.glowColor||'#80d7ff';ctx.shadowBlur=energy*(logo.glow??.75)*h*.13;ctx.drawImage(fittedWordmark,...b,(w-width)/2,(h-height)/2,width,height);ctx.save();ctx.globalCompositeOperation='screen';ctx.globalAlpha=Math.max(0,Math.min(.8,energy*(logo.glow??.75)*(logo.opacity??1)));ctx.shadowBlur=energy*h*.16;ctx.drawImage(fittedWordmark,...b,(w-width)/2,(h-height)/2,width,height);ctx.restore();}
 ctx.restore();
}
