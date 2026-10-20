(()=>{'use strict';
const isolatedPart=new URLSearchParams(location.search).get('part');if(isolatedPart==='marquee'){document.documentElement.dataset.sourcePart='marquee';}

const stage=document.getElementById('arcade-stage'),root=document.documentElement;
const keys=[...document.querySelectorAll('.arcade-button')];const $=s=>document.querySelector(s);
let last='',lastActionSeq=-1,lastEventSeq=0,config={},flashTimer,holdUntil=Array(9).fill(0),lastHeld=Array(9).fill(false),eventUntil=0;
let tournament=null;async function palettePoll(){try{tournament=await(await fetch('/api/state',{cache:'no-store'})).json();if(tournament.locked&&config.originalColorMode==='tournament')stage.style.setProperty('--winner-hue',tournament.palettes[tournament.palette].hue+'deg');}catch{}setTimeout(palettePoll,1000);}palettePoll();
const color=v=>/^#[0-9A-F]{6}$/i.test(v||'')?v:'#e60cd5';
function fit(){stage.style.transform=`scale(${Math.min(innerWidth/(config.canvasWidth||2060),innerHeight/(config.canvasHeight||1220))})`;}addEventListener('resize',fit);
function render(c){config=c;stage.classList.toggle('original',c.artworkMode==='original');fit();const w=c.gameWidth,h=Math.round(w*9/16);
 for(const [name,value] of Object.entries({'--game-width':w+'px','--game-height':h+'px','--game-left':Math.round((1920-w)/2)+'px','--game-top':c.gameTop+'px','--glow-radius':(12+22*c.glowStrength/100).toFixed(1)+'px','--scanline-opacity':c.scanlineStrength/100,'--reflection-opacity':c.reflectionStrength/100,'--press-glow':c.pressGlowStrength/100,'--press-time':c.pressDuration+'ms', '--round':c.borderStyle==='rounded'?'34px':c.borderStyle==='square'?'0px':'11px'}))root.style.setProperty(name,value);
 for(const [key,name] of [['panelColor','--panel'],['trimColor','--trim'],['secondaryColor','--trim2'],['buttonColor','--button'],['buttonAltColor','--button-alt'],['glowColor','--glow']])root.style.setProperty(name,color(c[key]));
 $('#marquee-text').textContent=c.marquee||'SHELDONTWITCHING';$('#subtitle-text').textContent=c.subtitle||'';
 const layers={'cabinet':'.original-cabinet','marquee':'.original-logo','lighting':'.original-fx','reflection':'#stick-reflection','arrows':'#original-arrows','buttons':'#original-buttons','widgets':'#original-widgets','events':'#original-event','joystick':'#original-stick'};
 (c.layerOrder||Object.keys(layers)).forEach((name,i)=>{const el=$(layers[name]);if(el)el.style.zIndex=String(i+1);});
 $('.original-logo').hidden=c.marqueeMode==='glacier';$('.original-brand').hidden=c.marqueeMode!=='glacier';$('.original-brand').style.zIndex=String((c.layerOrder||[]).indexOf('marquee')+1);stage.dataset.originalColor=c.originalColorMode;
 stage.dataset.artEffects=String(c.artworkEffects);stage.classList.toggle('native-scanlines',c.artworkEffects&&c.scanlines);stage.dataset.finish=c.cabinetFinish;stage.dataset.light=c.lightAnimation;stage.dataset.neon=c.neonPattern;stage.dataset.scanline=c.scanlinePattern;stage.dataset.press=c.pressEffect;stage.dataset.buttonStyle=c.buttonStyle;
 stage.classList.toggle('scanlines-on-game',c.scanlines&&c.scanlinesOnGame);stage.classList.toggle('breath',c.transition==='breath');stage.classList.toggle('charged',c.effectMode==='charged');
 stage.classList.toggle('square-rim',c.borderStyle==='square');stage.classList.toggle('rounded-rim',c.borderStyle==='rounded');stage.classList.toggle('flat-buttons',c.buttonStyle==='flat');stage.classList.toggle('glass-buttons',c.buttonStyle==='glass');stage.classList.toggle('reflections',c.reflections);
 $('.cabinet-grain').style.display=c.scanlines?'block':'none';$('#labels-slot').style.display=c.enableLabels?'block':'none';$('#now-playing-slot').style.display=c.enableNowPlaying?'block':'none';$('#tip-slot').style.display=c.showTipSlot?'block':'none';
 keys.forEach((button,i)=>{button.style.setProperty('--key-color',color(c.buttonColors[i]));button.setAttribute('aria-label',`Arcade visual button ${i+1} mapped to ${c.buttonBindings?.[i]||''}`);});
}
function flash(){stage.classList.remove('flash');void stage.offsetWidth;stage.classList.add('flash');clearTimeout(flashTimer);flashTimer=setTimeout(()=>stage.classList.remove('flash'),450);}
function reactButtons(pressed,ev){let now=Date.now();keys.forEach((button,i)=>{const physically=pressed.includes(i)&&config.reactiveGlow;
 if(physically&&!lastHeld[i])holdUntil[i]=now+config.pressDuration;lastHeld[i]=physically;
 const eventActive=ev&&config.eventAlerts&&ev.buttons.includes(i),on=physically||now<holdUntil[i]||eventActive;
 const pressColor=eventActive?color(ev.color):config.pressMode==='accent'?color(config.trimColor):config.pressMode==='original'?color(config.buttonColors[i]):config.pressMode==='rainbow'?`hsl(${(i*45+Math.round(now/40))%360} 100% 68%)`:color(config.pressColors[i]);
 button.style.setProperty('--press-color',pressColor);button.classList.toggle('pressed',!!on);button.classList.toggle('event-lit',!!eventActive);
});}
function renderEvent(ev){if(!ev||!config.eventAlerts){stage.classList.remove('event-active');return;}stage.style.setProperty('--event-color',color(ev.color));stage.dataset.eventEffect=ev.effect;
 $('#event-heading').textContent=ev.label||ev.kind.toUpperCase();$('#event-message').textContent=ev.text||'';
 if(ev.seq!==lastEventSeq){lastEventSeq=ev.seq;stage.classList.remove('event-active');void stage.offsetWidth;stage.classList.add('event-active');if(ev.effect==='flash')flash();}
}
const originalKeys=Array.from({length:9},(_,i)=>{const img=document.createElement('img');img.className='original-key';img.alt='Button '+(i+1);img.style.left=([26,106,186,266,0,80,160,240,362][i])+'px';img.style.top=([4,0,0,4,44,40,40,44,34][i])+'px';img.src='/arcade/assets/BUTTON_NEUTRAL.png';$('#original-buttons').append(img);return img;});
const leverTint=document.createElementNS('http://www.w3.org/2000/svg','svg');leverTint.setAttribute('width','0');leverTint.setAttribute('height','0');leverTint.setAttribute('aria-hidden','true');leverTint.innerHTML='<defs><filter id="lever-direction-tint" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB"><feFlood flood-color="#ed1750"/><feComposite in2="SourceGraphic" operator="in"/></filter></defs>';document.body.append(leverTint);
const arrows=['UP','DOWN','LEFT','RIGHT'];
const arrowImages=arrows.map((d,i)=>{const img=document.createElement('img');img.className='original-arrow';img.src='/arcade/assets/ARROW_'+({LEFT:'L',RIGHT:'R'}[d]||d)+'.png';img.style.left=([870,870,818,922][i])+'px';img.style.top=([1062,1140,1096,1096][i])+'px';$('#original-arrows').append(img);return img;});
function renderOriginal(v){if(config.artworkMode!=='original')return;$('#original-event').textContent=v.event?[v.event.label,v.event.text].filter(Boolean).join(' · '):'';$('#original-now-playing').hidden=!config.enableNowPlaying;$('#original-labels').hidden=!config.enableLabels;
 const pad=v.dpad||[],name=ArcadeSprites.direction(pad),rect=ArcadeSprites.frame(name,config.originalPositions?.joystick);
 const img=$('#original-stick');img.src=config.joystickOverrides?.[name]||'/arcade/assets/'+name+'.png';
 img.style.width=rect.width+'px';img.style.height=rect.height+'px';img.style.left=rect.x+'px';img.style.top=rect.y+'px';img.alt='Joystick '+name;
 reflectStick(img,rect,pad);
 const leverLights=config.cabinetParts?.arrows||{};leverTint.querySelector('feFlood').setAttribute('flood-color',leverLights.color||'#ed1750');
 arrowImages.forEach((el,i)=>{el.classList.toggle('active',pad.includes('DPAD_'+arrows[i]));el.style.height=(arrows[i]==='DOWN'?46:42)+'px';el.style.opacity=String(pad.includes('DPAD_'+arrows[i])?(leverLights.opacity??1):0);el.style.filter=[leverLights.color?'url(#lever-direction-tint)':'',leverLights.glow?`drop-shadow(0 0 ${leverLights.glow*10}px ${leverLights.color||config.trimColor})`:''].filter(Boolean).join(' ');});
 originalKeys.forEach((el,i)=>{const swap=v.event?.buttons.includes(i)&&v.event?.sprite?v.event.sprite:config.spriteOverrides?.[i];const pos=config.originalPositions?.buttons[i];if(pos){el.style.left=(pos[0]-1113)+'px';el.style.top=(pos[1]-1049)+'px';}const physically=(v.pressed||[]).includes(i);if(physically)holdUntil[i]=Date.now()+config.pressDuration;const on=physically||(config.inputAfterglow&&Date.now()<holdUntil[i])||(config.eventAlerts&&v.event?.buttons.includes(i));el.classList.toggle('active',!!on);el.src=on?(swap||'/arcade/assets/BUTTON_PRESSED.png'):(config.neutralOverrides?.[i]||'/arcade/assets/BUTTON_NEUTRAL.png');el.style.setProperty('--press-color',v.event?.color||config.pressColors[i]);el.style.filter=on&&config.reactiveGlow?`drop-shadow(0 0 ${config.pressGlowStrength/10}px ${v.event?.color||config.pressColors[i]})`:'none';});
}
const reflectionSprites=new Map();
function reflectStick(img,rect,pad){
 const canvas=$('#stick-reflection');if(!canvas)return;const ctx=canvas.getContext('2d');ctx.clearRect(0,0,2060,1220);
 if(!config.joystickReflection)return;
 const name=ArcadeSprites.reflectionDirection(ArcadeSprites.direction(pad)),src=config.joystickOverrides?.[name]||'/arcade/assets/'+name+'.png';
 if(!reflectionSprites.has(src)){const im=new Image();im.src=src;reflectionSprites.set(src,im);}const reflected=reflectionSprites.get(src);
 if(!reflected.complete||!reflected.naturalWidth)return;
 const anchor=config.originalPositions?.joystick||[891,1115],pose=ArcadeSprites.reflectionFrame(name,anchor[0],986,1,config.reflectionVisibleHeight??10);
 canvas.dataset.pose=name;ctx.save();ctx.beginPath();ctx.rect(403,986-(config.reflectionVisibleHeight??10),1254,config.reflectionVisibleHeight??10);ctx.clip();ctx.globalAlpha=(config.joystickReflectionOpacity||0)/100;ctx.imageSmoothingEnabled=false;
 if(pad.length){ctx.shadowColor=config.trimColor;ctx.shadowBlur=8;}
 // Reflect mount position and select an upright pose; never flip the ball/shaft bitmap.
 const top=ArcadeSprites.ballTop[name];ctx.drawImage(reflected,0,top,reflected.naturalWidth,reflected.naturalHeight-top,pose.x,pose.y+top,pose.width,pose.height-top);
 ctx.restore();
}
async function poll(){try{const r=await fetch('/api/arcade/live',{cache:'no-store'});if(!r.ok)throw Error('offline');const v=await r.json();const cfg=JSON.stringify(v.config);if(cfg!==last){last=cfg;render(v.config);}reactButtons(v.pressed||[],v.event||null);renderOriginal(v);renderEvent(v.event);if(v.lastAction==='flash'&&v.actionSeq!==lastActionSeq)flash();lastActionSeq=v.actionSeq;
 const pad=(v.dpad||[]);const stick=$('.joystick-handle');stick.style.translate=pad.includes('DPAD_LEFT')?'-12px 0':pad.includes('DPAD_RIGHT')?'12px 0':pad.includes('DPAD_UP')?'0 -12px':pad.includes('DPAD_DOWN')?'0 9px':'0 0';
 }catch(_){/* OBS keeps last-known styling until bridge resumes */}}
poll();setInterval(poll,40);
})();