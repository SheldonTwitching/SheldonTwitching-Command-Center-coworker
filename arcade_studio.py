"""Local-only arcade visuals, XInput D-pad / trigger remapping and simulated/file-change effects.

Never sends input to the game, opens no network listener, or reads a Streamlabs Tip Goal URL.
Original artwork preserves native screen geometry; optional FX Lab uses 16:9.
OBS/Streamlabs own real donation/goal amounts.
"""
from __future__ import annotations
import base64
import binascii
import ctypes
import json
import math
import os
import re
import threading
import time
from copy import deepcopy
from pathlib import Path

CABINET_CONTRACT = json.loads((Path(__file__).resolve().parent/'arcade'/'project-spec.json').read_text(encoding='utf-8'))['cabinet']

CABINET_STRUCTURE = json.loads((Path(__file__).resolve().parent/'arcade'/'cabinet-structure.json').read_text(encoding='utf-8'))

BUTTONS = ('A','B','X','Y','LB','RB','BACK','START')
BUTTON_FLAGS = (0x1000,0x2000,0x4000,0x8000,0x0100,0x0200,0x0020,0x0010)
INPUT_FLAGS = {
 'A':0x1000,'B':0x2000,'X':0x4000,'Y':0x8000,'LB':0x0100,'RB':0x0200,
 'BACK':0x0020,'START':0x0010,'DPAD_UP':0x0001,'DPAD_DOWN':0x0002,
 'DPAD_LEFT':0x0004,'DPAD_RIGHT':0x0008,'LSTICK':0x0040,'RSTICK':0x0080,
 'LT':0x10000,'RT':0x20000,'UNBOUND':0,
}
PALETTES = {
 'Glacier Violet':('#100d20','#80d7ff','#9664ed','#80d7ff','#9664ed'),
 'Sheldon Neon':('#211035','#e60cd5','#f52863','#ef3ccf','#a156ff'),
 'Final Round':('#151020','#ff3e3e','#ffa32b','#fa5259','#ffbc4c'),
 'Training Mode':('#0c202a','#19d6dd','#48e8ba','#0ca6ec','#80fff4'),
 'Purple Rain':('#23113d','#aa59ff','#793aef','#d784fa','#8859fc'),
 'Gold Rush':('#221323','#f4b533','#ff6e5a','#ffbb54','#f6de81'),
 'Cyberpunk':('#081827','#10e3fe','#e228ef','#17bcd8','#c841ff'),
 'Toxic Venom':('#101a12','#7eff1f','#b7ff26','#62d924','#e4ef3b'),
 'Blood Moon':('#230a12','#ff3355','#ae124b','#ff2543','#d7718d'),
 'Blue Lightning':('#06182d','#25aaff','#4b5ffd','#338cff','#80dcff'),
 'Synthwave Sunset':('#351335','#f738be','#ff9a3a','#f34fa4','#ffc86c'),
 'Vaporwave':('#221b3e','#83e0e4','#df8cfc','#edb7eb','#57baff'),
 'Monochrome':('#171721','#ededf6','#9393b5','#cdd0dc','#5d6283'),
 'Molten Lava':('#270c0a','#ff6c1a','#f21b24','#ff982b','#ff353f'),
 'Emerald Arcade':('#092d25','#13c781','#35fdb0','#63dd7e','#11a9aa'),
 'Royal Circuit':('#1c1036','#ab69ff','#efcf59','#a579f1','#ffc65c'),
 'Retro CRT':('#101e11','#5df58d','#31a163','#46fa72','#2f9950'),
 'Midnight Chrome':('#0a1225','#6d92ce','#d0d8ef','#6a81aa','#acb8d3'),
 'Cherry Pop':('#350c2c','#ff43a0','#ff72bd','#ea2784','#ffa0c0'),
 'Sunrise Fighter':('#2e1726','#ff983f','#ff5174','#ffc347','#ff6b94'),
 'Icebreaker':('#092439','#59e5fb','#ffffff','#48c5ed','#a8e7ff'),
}
STYLE_PRESETS = {
 'Cabinet Classic':{'cabinetFinish':'metal','buttonStyle':'arcade','borderStyle':'angled','lightAnimation':'pulse','pressMode':'custom'},
 'Glass Fighter':{'cabinetFinish':'glass','buttonStyle':'glass','borderStyle':'rounded','lightAnimation':'breath','reflections':True},
 'Chrome Champion':{'cabinetFinish':'chrome','buttonStyle':'chrome','borderStyle':'square','lightAnimation':'chase','reflections':True},
 'Pixel Throwback':{'cabinetFinish':'pixel','buttonStyle':'pixel','borderStyle':'square','scanlinePattern':'grid','lightAnimation':'static'},
 'Carbon Pro':{'cabinetFinish':'carbon','buttonStyle':'matte','borderStyle':'angled','lightAnimation':'static','reflections':False},
 'Neon Showcase':{'cabinetFinish':'gradient','buttonStyle':'candy','borderStyle':'rounded','lightAnimation':'wave','glowStrength':85},
 'Circuit Rush':{'cabinetFinish':'circuit','buttonStyle':'arcade','borderStyle':'angled','lightAnimation':'chase','scanlinePattern':'grid'},
 'Holographic':{'cabinetFinish':'glass','buttonStyle':'jelly','borderStyle':'rounded','lightAnimation':'wave','reflections':True},
 'Tournament Steel':{'cabinetFinish':'metal','buttonStyle':'chrome','borderStyle':'square','lightAnimation':'static','glowStrength':30},
 'Fireball':{'cabinetFinish':'gradient','buttonStyle':'candy','borderStyle':'angled','lightAnimation':'heartbeat','glowStrength':95},
 'Stealth Gamer':{'cabinetFinish':'carbon','buttonStyle':'flat','borderStyle':'square','lightAnimation':'static','scanlines':False},
 'Dream Cabinet':{'cabinetFinish':'gradient','buttonStyle':'jelly','borderStyle':'rounded','lightAnimation':'breath','reflectionStrength':75},
}
EVENT_KINDS = ('donation','subscriber','follower','raid','bits','goal','song')
EVENT_EFFECTS = ('burst','chase','ripple','pulse','flash','none')
_COLOR = re.compile(r'^#[0-9a-fA-F]{6}$')
_ALLOWED_ACTIONS = {'glow','flash','cycle','scanlines','toggle-glow','none','lights-off','lights-on','reflection-toggle','event-test'}
_ALLOWED_EFFECTS = {'normal','flash','charged'}

def default_event(kind):
    colors={'donation':'#ffe174','subscriber':'#c767ff','follower':'#52eaff','raid':'#ff4c6d','bits':'#a770ff','goal':'#42ffa4','song':'#1ed760'}
    return {'enabled':True,'color':colors[kind],'effect':'chase' if kind in ('donation','raid','goal') else 'pulse',
            'priority':80 if kind in ('raid','donation') else 30,'cooldown':0,'sprite':'','duration':3.0,'buttons':list(range(9)),'label':kind.upper()}

DEFAULT = {
 'artworkEffects':False,'artworkMode':'original','spriteOverrides':['']*9,'neutralOverrides':['']*9,
 'joystickOverrides':{k:'' for k in ('NEUTRAL','BACK','BACK_LEFT','BACK_RIGHT','FRONT','FRONT_LEFT','FRONT_RIGHT','LEFT','RIGHT')},
 'originalPositions':{'buttons':deepcopy(CABINET_CONTRACT['buttons']),'joystick':deepcopy(CABINET_CONTRACT['joystickPivot'])},
 'version':3,'canvasWidth':2060,'canvasHeight':1220,'gameWidth':1280,'gameTop':138,'gameAspect':'16:9','gameHeight':720,'gameLeft':320,
 'marquee':'SHELDONTWITCHING','subtitle':'INSERT COIN · JOIN THE FIGHT',
 'panelColor':'#100d20','trimColor':'#80d7ff','secondaryColor':'#9664ed',
 'buttonColor':'#ef3ccf','buttonAltColor':'#a156ff',
 'buttonColors':['#ee3dcf','#ec42dd','#dd53ef','#c365f5']*2+['#a156ff'],
 'pressColors':['#fff4bd','#ffffff','#aefcff','#ffd3fa']*2+['#ffffff'],
 'buttonBindings':['X','Y','RB','LB','A','B','RT','LT','START'],
 'glowColor':'#80d7ff','glowStrength':62,'scanlines':True,'scanlineStrength':18,
 'scanlinesOnGame':False,'scanlinePattern':'horizontal','reactiveGlow':True,'controllerLights':True,
 'controllerCommands':False,'controllerSlot':0,'enableNowPlaying':False,'enableLabels':False,'showTipSlot':True,
 'buttonActions':['glow']*9,'transition':'pulse','borderStyle':'angled','buttonStyle':'arcade',
 'palette':'Glacier Violet','stylePreset':'Cabinet Classic','effectMode':'normal','buttonLayout':'2x4',
 'cabinetFinish':'metal','reflections':True,'reflectionStrength':40,'pressMode':'custom','pressEffect':'bounce',
 'pressGlowStrength':85,'pressDuration':320,'lightAnimation':'pulse','neonPattern':'full',
 'eventSettings':{x:default_event(x) for x in EVENT_KINDS},
 'eventFiles':{x:'' for x in EVENT_KINDS},
 'eventAlerts':True,
 'layerOrder':deepcopy(CABINET_CONTRACT['layersBackToFront']),
 'joystickReflection':True,'joystickReflectionOpacity':8,'reflectionVisibleHeight':10,'inputAfterglow':False,
 'savedPalettes':{},'marqueeStyle':'graffiti',
 **deepcopy(CABINET_STRUCTURE['materialDefaults']),
 'cabinetDesign':'cabinet1','cabinetShape':'original','edgeProfile':'beveled','edgeWidth':8,'bezelWidth':60,'logoScale':.97,'cabinetParts':{},
 'marqueeMode':'original','originalColorMode':'original','gameFit':'fill','sourceAspect':16/9,'customSafeArea':[443,374,1174,578],
}

def validate_sprite(image):
    if not isinstance(image,str) or len(image)>550000:raise ValueError('Sprite must be a PNG under 400 KB')
    if not image:return
    if not image.startswith('data:image/png;base64,'):raise ValueError('Sprite must be PNG')
    try:raw=base64.b64decode(image.split(',',1)[1],validate=True)
    except (ValueError,binascii.Error):raise ValueError('Invalid PNG encoding')
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Invalid PNG signature')

def validated(data):
    if not isinstance(data,dict):raise ValueError('Arcade configuration must be an object')
    unknown=set(data)-set(DEFAULT)
    if unknown:raise ValueError('Unsupported arcade setting: '+sorted(unknown)[0])
    c=deepcopy(DEFAULT);c.update(deepcopy(data))
    # Migrate eight-control projects without discarding their assignments/styles.
    for key in ('buttonColors','pressColors','buttonBindings','buttonActions','spriteOverrides','neutralOverrides'):
        if isinstance(c[key],list) and len(c[key])==8:
            extra=DEFAULT[key][8]
            if key=='buttonBindings' and extra in c[key]:extra='UNBOUND'
            c[key].append(extra)
    if isinstance(c.get('originalPositions'),dict) and len(c['originalPositions'].get('buttons',[]))==8:c['originalPositions']['buttons'].append(deepcopy(DEFAULT['originalPositions']['buttons'][8]))
    if isinstance(c.get('eventSettings'),dict):
        c['eventSettings']={k:{**default_event(k),**v} if isinstance(v,dict) and k in EVENT_KINDS else v for k,v in c['eventSettings'].items()}
    for section,defaults in CABINET_STRUCTURE['materialDefaults'].items():
        raw=c[section]
        if not isinstance(raw,dict) or set(raw)!=set(defaults):raise ValueError('Invalid '+section)
    ball=c['ballLighting'];skin=c['buttonSkin'];finish=c['surfaceFinish'];indicators=c['leverIndicators']
    for section in (ball,skin):
        if not isinstance(section['enabled'],bool):raise ValueError('Invalid material switch')
    if not isinstance(ball['followInput'],bool):raise ValueError('Invalid ball light switch')
    for obj,key in [(ball,'color')]+[(skin,k) for k in skin if k.endswith(('Cap','Rim'))]:
        if not isinstance(obj[key],str) or not _COLOR.fullmatch(obj[key]):raise ValueError('Invalid material color')
    for obj,key,lo,hi in [(ball,'lightX',-1,1),(ball,'lightY',-1,1),(ball,'lightZ',.1,2),(ball,'ambient',0,1),(ball,'intensity',0,1),(ball,'gloss',0,1),(finish,'edgeGap',0,14),(finish,'overhangShadow',0,1),(finish,'overhangReach',30,220)]:
        v=obj[key]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:raise ValueError('Invalid material '+key)
    if not isinstance(skin['roles'],list) or len(skin['roles'])!=9 or any(v not in ('primary','secondary','accent') for v in skin['roles']):raise ValueError('Nine button roles required')
    if not isinstance(skin['overrides'],list) or len(skin['overrides'])!=9:raise ValueError('Nine button overrides required')
    for entry in skin['overrides']:
        if not isinstance(entry,dict) or set(entry)-{'cap','rim','pressedCap','pressedRim'} or any(not isinstance(v,str) or not _COLOR.fullmatch(v) for v in entry.values()):raise ValueError('Invalid button material override')
    if indicators['shape'] not in CABINET_STRUCTURE['leverShapes']:raise ValueError('Invalid lever light shape')
    if not isinstance(indicators['colors'],dict) or set(indicators['colors'])!={'UP','DOWN','LEFT','RIGHT'} or any(not isinstance(v,str) or (v and not _COLOR.fullmatch(v)) for v in indicators['colors'].values()):raise ValueError('Invalid direction light colors')
    if isinstance(c['reflectionVisibleHeight'],bool) or not isinstance(c['reflectionVisibleHeight'],(int,float)) or not math.isfinite(c['reflectionVisibleHeight']) or not 0<=c['reflectionVisibleHeight']<=30:raise ValueError('Invalid reflection height')
    if not isinstance(c['cabinetDesign'],str) or c['cabinetDesign'] not in CABINET_STRUCTURE['presets']:raise ValueError('Invalid cabinet design')
    for field,choices in [('cabinetShape',CABINET_STRUCTURE['geometry']['shapes']),('edgeProfile',CABINET_STRUCTURE['geometry']['profiles'])]:
        if c[field] not in choices:raise ValueError('Invalid cabinet geometry')
    for field in ('edgeWidth','bezelWidth','logoScale'):
        bounds=CABINET_STRUCTURE['geometry'][field];v=c[field]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not bounds['min']<=v<=bounds['max']:raise ValueError('Invalid cabinet '+field)
    mods=c['cabinetParts'];parts={p['id']:p for p in CABINET_STRUCTURE['parts']}
    if not isinstance(mods,dict) or set(mods)-set(parts):raise ValueError('Unknown cabinet part')
    for part,settings in mods.items():
        allowed=set(parts[part]['controls'])&{'color','opacity','glow','paint'}
        if not isinstance(settings,dict) or set(settings)-allowed:raise ValueError('Unsupported cabinet part setting')
        for key,v in settings.items():
            if key=='color':
                if not isinstance(v,str) or not _COLOR.fullmatch(v):raise ValueError('Invalid part color')
            elif key=='paint':
                if not isinstance(v,bool):raise ValueError('Invalid paint switch')
            elif isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1:raise ValueError('Invalid part strength')
    c['version'],c['canvasWidth'],c['canvasHeight'],c['gameAspect']=3,1920,1080,'16:9'
    w=c['gameWidth']; y=c['gameTop']
    if isinstance(w,bool) or not isinstance(w,(int,float)) or not math.isfinite(w) or not 1024<=w<=1440:raise ValueError('Game width must be 1024–1440')
    if isinstance(y,bool) or not isinstance(y,(int,float)) or not math.isfinite(y):raise ValueError('Invalid game position')
    c['gameWidth']=int(w);c['gameTop']=max(90,min(int(y),910-round(c['gameWidth']*9/16)))
    for k in ('panelColor','trimColor','secondaryColor','buttonColor','buttonAltColor','glowColor'):
        if not isinstance(c[k],str) or not _COLOR.fullmatch(c[k]):raise ValueError('Invalid color: '+k)
    for key in ('buttonColors','pressColors'):
        if not isinstance(c[key],list) or len(c[key])!=9 or any(not isinstance(v,str) or not _COLOR.fullmatch(v) for v in c[key]):raise ValueError('Nine valid '+key+' required')
    if not isinstance(c['buttonBindings'],list) or len(c['buttonBindings'])!=9 or any(x not in INPUT_FLAGS for x in c['buttonBindings']):raise ValueError('Invalid XInput button bindings')
    if len(set(x for x in c['buttonBindings'] if x!='UNBOUND'))!=len([x for x in c['buttonBindings'] if x!='UNBOUND']):raise ValueError('Bind each physical input to only one visual button')
    if not isinstance(c['buttonActions'],list) or len(c['buttonActions'])!=9 or any(x not in _ALLOWED_ACTIONS for x in c['buttonActions']):raise ValueError('Invalid arcade actions')
    for k in ('glowStrength','scanlineStrength','reflectionStrength','pressGlowStrength'):
        v=c[k]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=100:raise ValueError('Invalid slider: '+k)
        c[k]=int(v)
    v=c['pressDuration']
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 60<=v<=2000:raise ValueError('Invalid press duration')
    c['pressDuration']=int(v)
    for k in ('artworkEffects','scanlines','scanlinesOnGame','reactiveGlow','controllerLights','controllerCommands','enableNowPlaying','enableLabels','showTipSlot','reflections','eventAlerts'):
        if not isinstance(c[k],bool):raise ValueError('Invalid switch: '+k)
    if isinstance(c['controllerSlot'],bool) or not isinstance(c['controllerSlot'],int) or not 0<=c['controllerSlot']<=3:raise ValueError('Invalid XInput slot')
    for k,maxlen in (('marquee',52),('subtitle',80)):
        if not isinstance(c[k],str) or len(c[k])>maxlen:raise ValueError('Invalid label '+k)
    selections={
        'transition':('pulse','breath','static'), 'borderStyle':('angled','rounded','square'),
        'buttonStyle':('arcade','flat','glass','chrome','jelly','pixel','matte','candy'),
        'buttonLayout':('2x4',), 'effectMode':tuple(_ALLOWED_EFFECTS),
        'cabinetFinish':('metal','glass','chrome','pixel','carbon','gradient','circuit'),
        'scanlinePattern':('horizontal','vertical','grid','dots'),
        'pressMode':('custom','original','accent','rainbow'),
        'pressEffect':('bounce','burst','shockwave','spark','none'),
        'lightAnimation':('pulse','breath','static','chase','wave','heartbeat'),
        'neonPattern':('full','edges','corners','marquee'),
    }
    for k,choices in selections.items():
        if c[k] not in choices:raise ValueError('Invalid '+k)
    saved=c['savedPalettes']
    if not isinstance(saved,dict) or len(saved)>30:raise ValueError('Too many saved palettes')
    for name,colors in saved.items():
        if not isinstance(name,str) or not 1<=len(name)<=60 or name in PALETTES or name=='Custom' or not isinstance(colors,list) or len(colors)!=5 or any(not isinstance(v,str) or not _COLOR.fullmatch(v) for v in colors):raise ValueError('Invalid saved palette')
    if c['marqueeStyle'] not in ('graffiti','classic'):raise ValueError('Invalid marquee style')
    if c['palette'] not in PALETTES and c['palette'] not in saved and c['palette']!='Custom':raise ValueError('Invalid palette')
    if c['stylePreset'] not in STYLE_PRESETS and c['stylePreset']!='Custom':raise ValueError('Invalid design preset')
    if not isinstance(c['eventSettings'],dict) or set(c['eventSettings'])!=set(EVENT_KINDS):raise ValueError('Invalid events')
    for kind, raw in c['eventSettings'].items():
        if not isinstance(raw,dict) or set(raw)!=set(default_event(kind)):raise ValueError('Invalid event settings: '+kind)
        validate_sprite(raw['sprite'])
        if isinstance(raw['priority'],bool) or not isinstance(raw['priority'],int) or not 0<=raw['priority']<=100:raise ValueError('Invalid event priority')
        if isinstance(raw['cooldown'],bool) or not isinstance(raw['cooldown'],(int,float)) or not math.isfinite(raw['cooldown']) or not 0<=raw['cooldown']<=600:raise ValueError('Invalid event cooldown')
        if not isinstance(raw['enabled'],bool) or not _COLOR.fullmatch(raw['color']) or raw['effect'] not in EVENT_EFFECTS:raise ValueError('Invalid event styling')
        if isinstance(raw['duration'],bool) or not isinstance(raw['duration'],(int,float)) or not math.isfinite(raw['duration']) or not .5<=raw['duration']<=10:raise ValueError('Invalid event duration')
        if not isinstance(raw['buttons'],list) or any(isinstance(x,bool) or not isinstance(x,int) or not 0<=x<=8 for x in raw['buttons']) or len(raw['buttons'])>9:raise ValueError('Invalid event button targets')
        if not isinstance(raw['label'],str) or len(raw['label'])>38:raise ValueError('Invalid event label')
    if not isinstance(c['eventFiles'],dict) or set(c['eventFiles'])!=set(EVENT_KINDS):raise ValueError('Invalid event files')
    for name in c['eventFiles'].values():
        if not isinstance(name,str) or len(name)>120 or (name and (Path(name).name!=name or not name.lower().endswith('.txt'))):raise ValueError('Event sources must be simple .txt filenames')
    if c['artworkMode'] not in ('original','variation'):raise ValueError('Invalid artwork mode')
    for field in ('spriteOverrides','neutralOverrides'):
        if not isinstance(c[field],list) or len(c[field])!=9:raise ValueError('Nine sprite overrides required')
        for image in c[field]:validate_sprite(image)
    if not isinstance(c['joystickOverrides'],dict) or set(c['joystickOverrides'])!=set(DEFAULT['joystickOverrides']):raise ValueError('Nine joystick states required')
    for image in c['joystickOverrides'].values():validate_sprite(image)
    positions=c['originalPositions']
    if not isinstance(positions,dict) or set(positions)!={'buttons','joystick'} or not isinstance(positions['buttons'],list) or len(positions['buttons'])!=9:raise ValueError('Invalid original positions')
    for point in positions['buttons']+[positions['joystick']]:
        if not isinstance(point,list) or len(point)!=2 or any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) for v in point) or not 0<=point[0]<=1982 or not 0<=point[1]<=1154:raise ValueError('Invalid sprite position')
    if c['artworkMode']=='original':
        c['canvasWidth'],c['canvasHeight']=CABINET_CONTRACT['nativeCanvas']
        c['gameAspect']='original';c['gameLeft'],c['gameTop'],c['gameWidth'],c['gameHeight']=CABINET_CONTRACT['nativeGlass']
    else:
        c['gameHeight']=round(c['gameWidth']*9/16);c['gameLeft']=round((1920-c['gameWidth'])/2)
    if c['marqueeMode'] not in ('original','glacier') or c['originalColorMode'] not in ('original','glacier','tournament'):raise ValueError('Invalid original artwork theme')
    layers=DEFAULT['layerOrder']
    if not isinstance(c['layerOrder'],list) or len(c['layerOrder'])!=len(layers) or set(c['layerOrder'])!=set(layers):raise ValueError('Layer order must contain every layer once')
    for key in ('joystickReflection','inputAfterglow'):
        if not isinstance(c[key],bool):raise ValueError('Invalid '+key)
    if isinstance(c['joystickReflectionOpacity'],bool) or not isinstance(c['joystickReflectionOpacity'],(int,float)) or not 0<=c['joystickReflectionOpacity']<=40:raise ValueError('Invalid reflection opacity')
    if c['gameFit'] not in ('fit','fill','custom'):raise ValueError('Invalid game fit')
    if isinstance(c['sourceAspect'],bool) or not isinstance(c['sourceAspect'],(int,float)) or not .5<=c['sourceAspect']<=4:raise ValueError('Invalid source aspect')
    safe=c['customSafeArea']
    if not isinstance(safe,list) or len(safe)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in safe):raise ValueError('Invalid safe area')
    x,y,w,h=safe
    gx,gy,gw,gh=CABINET_CONTRACT['nativeGlass']
    if x<gx or y<gy or w<100 or h<100 or x+w>gx+gw or y+h>gy+gh:raise ValueError('Safe area must stay inside glass')
    return c

class _Gamepad(ctypes.Structure):
    _fields_=[('wButtons',ctypes.c_ushort),('bLeftTrigger',ctypes.c_ubyte),('bRightTrigger',ctypes.c_ubyte),('sThumbLX',ctypes.c_short),('sThumbLY',ctypes.c_short),('sThumbRX',ctypes.c_short),('sThumbRY',ctypes.c_short)]
class _XInputState(ctypes.Structure):
    _fields_=[('dwPacketNumber',ctypes.c_ulong),('Gamepad',_Gamepad)]

class ArcadeStudio:
    def __init__(self,home):
        self.path=Path(home)/'arcade-overlay.json';self.lock=threading.RLock();self.config=validated({})
        self.button_until=[0.0]*9;self.last_state=0;self.last_command='';self.action_seq=0
        self._dll=None;self.learning=None;self.learn_release=False;self.learn_until=0;self.last_learn=None
        self.event=None;self.event_seq=0;self.event_until=0;self.file_baseline={};self.event_queue=[];self.event_last={}
        if os.name=='nt':
            for name in ('xinput1_4.dll','xinput1_3.dll','xinput9_1_0.dll'):
                try:
                    dll=ctypes.WinDLL(name);dll.XInputGetState.argtypes=[ctypes.c_ulong,ctypes.POINTER(_XInputState)];dll.XInputGetState.restype=ctypes.c_ulong;self._dll=dll;break
                except (OSError,AttributeError):continue
        try:self.config=validated(json.loads(self.path.read_text(encoding='utf-8')))
        except (OSError,ValueError,TypeError):pass

    def get(self):
        with self.lock:return deepcopy(self.config)

    def save(self,data):
        cfg=validated(data)
        with self.lock:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');os.replace(tmp,self.path)
            if cfg['controllerSlot']!=self.config['controllerSlot']:self.last_state=0
            if cfg['eventFiles']!=self.config['eventFiles']:self.file_baseline={}
            self.config=cfg
            return deepcopy(cfg)

    def _controller_bits(self):
        if self._dll is None:return None
        state=_XInputState()
        try:
            if self._dll.XInputGetState(self.config['controllerSlot'],ctypes.byref(state))==0:
                bits=int(state.Gamepad.wButtons)
                if state.Gamepad.bLeftTrigger>=50:bits|=INPUT_FLAGS['LT']
                if state.Gamepad.bRightTrigger>=50:bits|=INPUT_FLAGS['RT']
                return bits
        except (OSError,AttributeError):return None
        return None

    def start_learn(self,index):
        if isinstance(index,bool) or not isinstance(index,int) or not 0<=index<9:raise ValueError('Choose a visual button 0–7')
        with self.lock:
            self.learning=index;self.learn_until=time.monotonic()+15;self.learn_release=True;self.last_learn=None
            return {'learning':index,'seconds':15}

    def cancel_learn(self):
        with self.lock:self.learning=None;self.last_learn=None
        return {'ok':True}

    def _execute(self,action):
        if action=='scanlines':self.config['scanlines']=not self.config['scanlines']
        elif action=='toggle-glow':self.config['reactiveGlow']=not self.config['reactiveGlow']
        elif action=='reflection-toggle':self.config['reflections']=not self.config['reflections']
        elif action=='lights-off':self.config['controllerLights']=False
        elif action=='lights-on':self.config['controllerLights']=True
        elif action=='cycle':
            available={**PALETTES,**self.config['savedPalettes']};names=list(available)
            try:idx=(names.index(self.config['palette'])+1)%len(names)
            except ValueError:idx=0
            name=names[idx];self.config['palette']=name
            vals=available[name]
            for key,val in zip(('panelColor','trimColor','secondaryColor','buttonColor','buttonAltColor'),vals):self.config[key]=val
            self.config['buttonColors']=[vals[3 if i%2==0 else 4] for i in range(9)]
        elif action=='flash':self.config['effectMode']='flash'
        elif action=='event-test':self.trigger_event('donation','TEST DONATION')
        self.last_command=action;self.action_seq+=1

    def click(self,index):
        if isinstance(index,bool) or not isinstance(index,int) or not 0<=index<9:raise ValueError('Button index must be 0–8')
        with self.lock:
            self.button_until[index]=time.monotonic()+self.config['pressDuration']/1000
            action=self.config['buttonActions'][index];self._execute(action)
            if action in ('scanlines','cycle','toggle-glow','reflection-toggle','lights-off','lights-on'):self.save(self.config)
            return {'ok':True,'button':index,'action':action}

    def trigger_event(self,kind,text=''):
        if kind not in EVENT_KINDS:raise ValueError('Unknown event')
        if not isinstance(text,str):raise ValueError('Event text must be text')
        with self.lock:
            rule=self.config['eventSettings'][kind]
            if not rule['enabled'] or not self.config['eventAlerts']:return {'ok':False,'disabled':True}
            now=time.monotonic()
            if now-self.event_last.get(kind,float('-inf'))<rule['cooldown']:return {'ok':False,'cooldown':True}
            self.event_last[kind]=now
            if self.event and now<self.event_until:
                if len(self.event_queue)>=32:return {'ok':False,'queueFull':True}
                self.event_queue.append((rule['priority'],len(self.event_queue),kind,text[:80]))
                return {'ok':True,'queued':True,'queueDepth':len(self.event_queue)}
            self.event_seq+=1;self.event_until=now+rule['duration']
            self.event={'kind':kind,'label':rule['label'],'text':text[:80],'color':rule['color'],
                        'effect':rule['effect'],'sprite':rule['sprite'],'buttons':rule['buttons'],'duration':rule['duration'],'seq':self.event_seq}
            return {'ok':True,'eventSeq':self.event_seq}

    def observe_events(self,values):
        """Input: {kind: (filename, file_content or None)}. First read establishes baseline.
        Subsequent changes to configured Streamlabels files trigger effects, not Tip Goal totals.
        """
        with self.lock:
            for kind,(filename,value) in values.items():
                if kind not in EVENT_KINDS or not filename:continue
                key=(kind,filename)
                if key not in self.file_baseline:self.file_baseline[key]=value;continue
                if value is not None and value.strip() and value!=self.file_baseline[key]:
                    self.file_baseline[key]=value
                    self.trigger_event(kind,value.strip())

    def live(self):
        with self.lock:
            hardware=self._controller_bits();now=time.monotonic();bits=0 if hardware is None else hardware
            if now>=self.event_until and self.event_queue:
                self.event_queue.sort(key=lambda e:(-e[0],e[1]));_,_,kind,text=self.event_queue.pop(0);rule=self.config['eventSettings'][kind];self.event_seq+=1;self.event_until=now+rule['duration'];self.event={'kind':kind,'label':rule['label'],'text':text,'color':rule['color'],'effect':rule['effect'],'sprite':rule['sprite'],'buttons':rule['buttons'],'duration':rule['duration'],'seq':self.event_seq}
            held=(bits&0x0030)==0x0030
            rising=bits&~self.last_state;self.last_state=bits
            pressed_raw=[name for name,flag in INPUT_FLAGS.items() if bits&flag]
            if self.learning is not None:
                if now>self.learn_until:self.learning=None;self.last_learn={'error':'Timed out; try again'}
                elif self.learn_release:
                    if bits==0:self.learn_release=False
                else:
                    # Prefer D-pad if multiple inputs rise at once; skip BACK/START modifiers.
                    candidates=[name for name in INPUT_FLAGS if rising&INPUT_FLAGS[name] and name not in ('BACK','START')]
                    if not candidates:candidates=[name for name in INPUT_FLAGS if rising&INPUT_FLAGS[name]]
                    if candidates:
                        name=candidates[0];index=self.learning
                        previous=self.config['buttonBindings'].index(name) if name in self.config['buttonBindings'] else None
                        if previous is not None and previous!=index:
                            self.config['buttonBindings'][previous]=self.config['buttonBindings'][index]
                        self.config['buttonBindings'][index]=name
                        self.save(self.config);self.last_learn={'index':index,'input':name};self.learning=None
            active=[i for i,name in enumerate(self.config['buttonBindings']) if (hardware is not None and (bits&INPUT_FLAGS[name]) and self.config['controllerLights']) or now<self.button_until[i]]
            if self.config['controllerCommands'] and held and hardware is not None and self.learning is None:
                for i,name in enumerate(self.config['buttonBindings']):
                    flag=INPUT_FLAGS[name]
                    if name not in ('BACK','START') and rising&flag:
                        act=self.config['buttonActions'][i];self._execute(act)
                        if act in ('scanlines','cycle','toggle-glow','reflection-toggle','lights-off','lights-on'):self.save(self.config)
            e=deepcopy(self.event) if now<self.event_until else None
            if e:e['remainingMs']=round((self.event_until-now)*1000)
            return {'connected':hardware is not None,'rawInputs':pressed_raw,'pressed':active,
                    'dpad':[d for d in ('DPAD_UP','DPAD_DOWN','DPAD_LEFT','DPAD_RIGHT') if d in pressed_raw],
                    'commandChord':held,'commandEnabled':self.config['controllerCommands'],
                    'learning':self.learning,'learnResult':self.last_learn,'learnWaitingRelease':self.learn_release,
                    'eventQueueDepth':len(self.event_queue),'effect':self.config['effectMode'],'lastAction':self.last_command,
                    'actionSeq':self.action_seq,'event':e,'eventSeq':self.event_seq,'config':deepcopy(self.config)}
