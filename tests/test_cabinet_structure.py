"""Cabinet reconstruction, protected aperture and real workbench integration."""
import json, os, socket, subprocess, sys, time
from copy import deepcopy
from pathlib import Path
from urllib.request import urlopen
import pytest
from arcade_studio import validated, ArcadeStudio, CABINET_STRUCTURE
from studio_runtime import validate, ROADMAPS
ROOT=Path(__file__).resolve().parents[1]

def test_part_capabilities_and_settings_survive_restart(tmp_path):
    parts={p['id']:p for p in CABINET_STRUCTURE['parts']}
    assert len(parts)>65
    assert parts['button1.cap']['capability']=='region'  # Runtime material mask, not a detached source sprite.
    assert not parts['button1.cap']['controls']
    c=validated({'cabinetShape':'chamfered','edgeWidth':17,'cabinetParts':{'logo':{'opacity':.8,'glow':.4},'edge':{'color':'#ffeeaa'},'arrows':{'color':'#31ff8a','opacity':.8},'screenSurround':{'paint':True,'opacity':.55}}})
    model=ArcadeStudio(tmp_path);model.save(c)
    assert ArcadeStudio(tmp_path).get()['cabinetParts']==c['cabinetParts']
    for invalid in [{'cabinetShape':'circle'},{'edgeWidth':float('nan')},{'cabinetParts':{'button1.cap':{'color':'#ffffff'}}},{'cabinetParts':{'logo':{'opacity':True}}},{'cabinetParts':{'unregistered':{}}}]:
        with pytest.raises(ValueError):validated(invalid)

def test_stingers_roadmap_migrates_without_losing_pinned_ideas():
    old=deepcopy(ROADMAPS);del old['stingers']
    old['cabinet']['ideas']=[{'id':'owner-idea','text':'Try a painted wipe','pinned':True}]
    migrated=validate({'roadmaps':old})['roadmaps']
    assert 'stingers' in migrated
    assert migrated['cabinet']['ideas']==old['cabinet']['ideas']
    assert 'planned' in migrated['stingers']['current']

def test_cabinet_workbench_and_upright_reflection(tmp_path):
    pw=pytest.importorskip('playwright.sync_api')
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--headless','--port',str(port)],env={**os.environ,'ST_LABELS_HOME':str(tmp_path)},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    try:
        for _ in range(60):
            try:
                with urlopen(base+'/health',timeout=1):break
            except OSError:time.sleep(.1)
        with pw.sync_playwright() as manager:
            browser=manager.chromium.launch();page=browser.new_page(viewport={'width':1600,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base+'/studio/cabinet');pw.expect(page.locator('#status')).to_have_text('Saved locally',timeout=15000)
            page.get_by_role('button',name='Owner Original',exact=True).click();pw.expect(page.locator('#status')).to_have_text('Saved locally')
            with urlopen(base+'/api/arcade/config') as response:c=json.load(response)
            assert c['cabinetDesign']=='original' and c['marqueeStyle']=='classic'
            page.get_by_role('button',name='Cabinet 1 · Glacier Graffiti',exact=True).click();pw.expect(page.locator('#status')).to_have_text('Saved locally')
            page.locator('#cabinetShape').select_option('chamfered');page.locator('#parts').select_option('logo');page.get_by_role('slider',name='SheldonTwitching lettering opacity').fill('0.72');page.locator('#leverLightColor').fill('#31ff8a');page.get_by_label('Ball-top color',exact=True).fill('#c738cf');page.get_by_label('Button to customize',exact=True).select_option('8');page.get_by_label('Button neutral rim',exact=True).fill('#1e4d6e');page.get_by_label('Lever light shape',exact=True).select_option('diamond')
            page.get_by_role('button',name='Save cabinet',exact=True).click();pw.expect(page.locator('#status')).to_have_text('Saved locally')
            with urlopen(base+'/api/arcade/config') as response:c=json.load(response)
            assert c['cabinetShape']=='chamfered' and c['cabinetParts']['logo']['opacity']==.72
            assert c['buttonBindings']==validated({})['buttonBindings']
            assert c['cabinetParts']['arrows']['color']=='#31ff8a'
            assert c['ballLighting']['color']=='#c738cf' and c['buttonSkin']['roles'][8]=='accent'
            assert c['buttonSkin']['overrides'][8]['rim']=='#1e4d6e' and c['leverIndicators']['shape']=='diamond'
            page.add_init_script("""window.stickDraws=[];window.logoFits=[];const draw=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(im,...args){const sprite=im.src||im.dataset?.sourceSprite;if(sprite&&/\\/(NEUTRAL|BACK|FRONT)\\.png$/.test(sprite))window.stickDraws.push({src:sprite,d:this.getTransform().d,alpha:this.globalAlpha});if(im.src&&im.src.endsWith('/logo-glacier-violet.png')&&args.length===8)window.logoFits.push({sx:args[6]/args[2],sy:args[7]/args[3]});return draw.call(this,im,...args);};""")
            for pose,expected in [('UP','FRONT'),('NEUTRAL','NEUTRAL'),('DOWN','BACK')]:
                page.goto(base+'/studio/parts/all?pose='+pose)
                page.wait_for_function("document.querySelector('canvas').dataset.reflectionPose === '"+expected+"'")
                page.wait_for_function("window.stickDraws.some(d=>d.alpha<.5)")
                draws=page.evaluate('window.stickDraws')
                assert all(d['d']>0 for d in draws),draws
                assert any(d['src'].endswith('/'+expected+'.png') and d['alpha']<.5 for d in draws)
            page.goto(base+'/studio/parts/marquee?view=native&design=cabinet1')
            page.wait_for_function('window.logoFits.length>0')
            assert all(abs(fit['sx']-fit['sy'])<1e-9 for fit in page.evaluate('window.logoFits'))
            page.goto(base+'/studio/parts/reflection?view=native&pose=NEUTRAL')
            page.wait_for_function("document.querySelector('canvas').dataset.reflectionPose==='NEUTRAL'")
            page.wait_for_function("document.querySelector('canvas').dataset.ready==='true'")
            reflected=page.evaluate("""()=>{const c=document.querySelector('canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let minX=c.width,maxX=0,minY=c.height,maxY=0,maxAlpha=0;for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const a=d[(y*c.width+x)*4+3];if(a){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);maxAlpha=Math.max(maxAlpha,a);}}return {minX,maxX,minY,maxY,maxAlpha};}""")
            assert 976<=reflected['minY']<=reflected['maxY']<986,reflected
            assert 842<=reflected['minX']<=reflected['maxX']<=942,reflected
            assert 0<reflected['maxAlpha']<=21,reflected
            assert not CABINET_STRUCTURE['reflection']['includeButtons']
            assert CABINET_STRUCTURE['logoContract']['asset']=='world/assets/logo-glacier-violet.png'
            assert CABINET_STRUCTURE['logoContract']['allowNonuniformScale'] is False
            # Reskins discard both baked line print and the matching interior FX.
            sums={}
            for design in ('original','cabinet1'):
                page.goto(base+'/studio/parts/lighting?view=native&shape=original&design='+design)
                page.wait_for_function("document.querySelector('canvas').dataset.ready==='true'")
                sums[design]=page.evaluate("""()=>{const g=document.querySelector('canvas').getContext('2d');return [[400,1130,250,40],[1120,1128,500,45]].map(r=>{const d=g.getImageData(...r).data;let n=0;for(let i=3;i<d.length;i+=4)n+=d[i];return n;});}""")
            assert all(n>0 for n in sums['original']),sums
            assert sums['cabinet1']==[0,0],sums
            page.goto(base+'/studio/parts/arrows?view=native&pose=UP')
            page.wait_for_function("document.querySelector('canvas').dataset.ready==='true'")
            colors=page.evaluate("""()=>{const d=document.querySelector('canvas').getContext('2d').getImageData(870,1062,44,42).data;const colors=new Set();for(let i=0;i<d.length;i+=4)if(d[i+3]>240)colors.add([d[i],d[i+1],d[i+2]].join(','));return [...colors];}""")
            assert colors==['49,255,138'],colors
            for shape in ('original','square','chamfered'):
                page.goto(base+'/studio/parts/all?shape='+shape)
                page.wait_for_function("document.querySelector('canvas').dataset.ready==='true'")
                pixels=page.evaluate("""()=>{const g=document.querySelector('canvas').getContext('2d');return {center:g.getImageData(1000,500,1,1).data[3],edge:g.getImageData(190,500,1,1).data[3]};}""")
                assert pixels['center']==0 and pixels['edge']>0,(shape,pixels)
            material=page.evaluate("""async()=>{const m=await import('/arcade/cabinet-materials.js'),s=await (await fetch('/arcade/cabinet-structure.json')).json();const im=new Image();im.src='/arcade/assets/ARROW_DOWN.png';await im.decode();const arrow=m.indicatorMaterial(im,'original','#31ff8a','DOWN');const b=new Image();b.src='/arcade/assets/BUTTON_NEUTRAL.png';await b.decode();const skin=structuredClone(s.materialDefaults.buttonSkin);skin.primaryCap='#ff3333';skin.primaryRim='#3344ff';const button=m.buttonMaterial(b,skin,0,false,s.controlGeometry.button);const g=button.getContext('2d'),cap=[...g.getImageData(38,20,1,1).data],rim=[...g.getImageData(38,53,1,1).data];const settings=s.materialDefaults.ballLighting;return {arrow:[arrow.width,arrow.height],cap,rim,left:m.lightVector(settings,[-60,30]),right:m.lightVector(settings,[60,-30])};}""")
            assert material['arrow']==[44,46]
            assert material['cap'][0]>material['cap'][2] and material['rim'][2]>material['rim'][0],material
            assert material['left']!=material['right']
            # Pixel materials preserve source brightness, alpha and repeated color clusters.
            pixel_art=page.evaluate("""async()=>{const m=await import('/arcade/cabinet-materials.js'),s=await (await fetch('/arcade/cabinet-structure.json')).json();let alphaChanges=0,brightnessChanges=0,clusterSplits=0,shaftChanges=0;
             for(const name of ['NEUTRAL','BACK','BACK_LEFT','BACK_RIGHT','FRONT','FRONT_LEFT','FRONT_RIGHT','LEFT','RIGHT']){const im=new Image();im.src='/arcade/assets/'+name+'.png';await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const g=c.getContext('2d');g.drawImage(im,0,0);const source=g.getImageData(0,0,c.width,c.height).data,out=m.sphereMaterial(im,name,s.materialDefaults.ballLighting,s.controlGeometry.balls,{},[]).getContext('2d').getImageData(0,0,c.width,c.height).data,seen=new Map(),[cx,cy,r]=s.controlGeometry.balls[name];
              for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const i=(y*c.width+x)*4;alphaChanges+=source[i+3]!==out[i+3];if(!source[i+3])continue;if((x-cx)**2+(y-cy)**2<=r*r){brightnessChanges+=source[i+3]===255&&Math.abs(Math.max(...source.slice(i,i+3))*Math.min(1,207/220)-Math.max(...out.slice(i,i+3)))>1;const key=[...source.slice(i,i+4)].join(),value=[...out.slice(i,i+4)].join();if(seen.has(key)&&seen.get(key)!==value)clusterSplits++;seen.set(key,value);}else shaftChanges+=[...source.slice(i,i+4)].join()!==[...out.slice(i,i+4)].join();}
             }
             for(const pressed of [false,true]){const im=new Image();im.src='/arcade/assets/BUTTON_'+(pressed?'PRESSED':'NEUTRAL')+'.png';await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const g=c.getContext('2d');g.drawImage(im,0,0);const source=g.getImageData(0,0,c.width,c.height).data,out=m.buttonMaterial(im,s.materialDefaults.buttonSkin,0,pressed,s.controlGeometry.button).getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=0;i<source.length;i+=4){alphaChanges+=source[i+3]!==out[i+3];if(source[i+3]){const value=Math.max(...source.slice(i,i+3)),x=(i/4)%c.width,y=Math.floor(i/4/c.width),[cx,cy,rx,ry]=s.controlGeometry.button.capEllipse,onCap=((x-cx)/rx)**2+((y-cy)/ry)**2<=1,skin=s.materialDefaults.buttonSkin,hex=pressed?(onCap?skin.pressedCap:skin.pressedRim):(onCap?skin.primaryCap:skin.primaryRim),max=Math.max(...[1,3,5].map(k=>parseInt(hex.slice(k,k+2),16))),gain=value<s.controlGeometry.button.shadowThreshold?1:Math.min(1,max/220);brightnessChanges+=source[i+3]===255&&Math.abs(value*gain-Math.max(...out.slice(i,i+3)))>1;}}}
             return {alphaChanges,brightnessChanges,clusterSplits,shaftChanges};}""")
            assert pixel_art==dict(alphaChanges=0,brightnessChanges=0,clusterSplits=0,shaftChanges=0),pixel_art
            page.goto(base+'/studio/parts/marquee?view=native&design=cabinet1')
            page.wait_for_function('window.logoFits.length>0')
            coverage=page.evaluate("""()=>{const g=document.querySelector('canvas').getContext('2d');return [[144,1],[1915,1],[155,100],[1904,100],[174,247],[1885,247]].map(([x,y])=>g.getImageData(x,y,1,1).data[3]);}""")
            assert all(a>=254 for a in coverage),coverage  # Sloped clip boundary may cover 254/255.
            page.goto(base+'/studio/parts/cabinet?view=native&design=cabinet1&shape=original')
            page.wait_for_function("document.querySelector('canvas').dataset.ready==='true'")
            trim=page.evaluate("""()=>{const g=document.querySelector('canvas').getContext('2d');return [[200,274],[204,275],[230,330],[130,1165]].map(([x,y])=>[...g.getImageData(x,y,1,1).data]);}""")
            assert all(p[2]>p[0] and p[1]>p[0] for p in trim),trim
            assert not errors,errors
            browser.close()
    finally:
        proc.terminate();proc.wait(timeout=10)

