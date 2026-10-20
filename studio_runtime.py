"""Unified scene state, bounded chat ingress and cached Bangor weather/clock.

No game input injection or OBS scene collection writes. External calls run in
a background worker; a failed forecast never blocks render/controller polling.
"""
from __future__ import annotations
import json, math, secrets, threading, time
from copy import deepcopy
from collections import deque
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from zoneinfo import ZoneInfo
from game_engine import Arcade
from text_reader import validate_reader

SCENES=('intro','starting','brb','gameplay','chatting','ending','background')
STAGES=('rooftop','waterfront','afterhours')
# One shipped feature registry feeds the app, board and documentation.
_FEATURES=json.loads((Path(__file__).resolve().parent/'arcade/feature-registry.json').read_text(encoding='utf-8'))['features']
ROADMAPS={f['id']:{'title':f['title'],'current':f['current'],'next':f['next'],'ideas':[]} for f in _FEATURES}

DEFAULT={
 'audio':{'mode':'relay','deviceId':'','obsSource':'','obsPort':4455,'gain':1,'smoothing':.7,'enabled':True},
 'textReader':{'path':'','mode':'raw','needle':'','fallback':'Waiting for text'},
 'scene':'starting','format':'landscape','stage':'rooftop','stageCycle':True,'stageSeconds':120,
 'weather':{'mode':'live','kind':'clear','intensity':.6,'location':'Bangor, Maine, USA 04401','latitude':44.79884,'longitude':-68.77265},
 'clock':{'mode':'live','hour':20,'timezone':'America/New_York','networkSync':True},
 'chat':{'enabled':True,'fontSize':24,'fontFamily':'monospace','color':'#e4efff','nameColor':'#80d7ff','background':'#100d20','opacity':.82,'borderColor':'#6540c5','radius':4,'maxMessages':12,'holdSeconds':60,'showTime':False,'showCommands':False,'motion':'slide','transitionMs':350,'customCss':''},
 'widgets':{'labels':True,'spotify':True,'chat':True},
 'layouts':{},'customCss':'','roadmaps':ROADMAPS,'stageMotion':{'enabled':True,'speed':1,'fps':30},
}

def validate(value):
 if not isinstance(value,dict) or set(value)-set(DEFAULT):raise ValueError('Invalid studio project')
 c=deepcopy(DEFAULT)
 for k,v in value.items():c[k]={**c[k],**v} if isinstance(c[k],dict) and isinstance(v,dict) else deepcopy(v)
 if c['scene'] not in SCENES or c['format'] not in ('landscape','vertical') or c['stage'] not in STAGES:raise ValueError('Invalid scene, stage or monitor format')
 if not isinstance(c['stageCycle'],bool) or isinstance(c['stageSeconds'],bool) or not isinstance(c['stageSeconds'],(int,float)) or not 30<=c['stageSeconds']<=1800:raise ValueError('Stage interval must be 30–1800 seconds')
 audio=c['audio']
 if not isinstance(audio,dict) or set(audio)!=set(DEFAULT['audio']) or audio['mode'] not in ('relay','input','desktop') or not isinstance(audio['enabled'],bool) or not isinstance(audio['deviceId'],str) or len(audio['deviceId'])>500:raise ValueError('Invalid audio source')
 if not isinstance(audio['obsSource'],str) or len(audio['obsSource'])>500 or isinstance(audio['obsPort'],bool) or not isinstance(audio['obsPort'],int) or not 1<=audio['obsPort']<=65535:raise ValueError('Invalid OBS audio source')
 for key,lo,hi in [('gain',0,5),('smoothing',0,.95)]:
  v=audio[key]
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:raise ValueError('Invalid audio '+key)
 validate_reader(c['textReader'])
 w=c['weather'];k=c['clock'];chat=c['chat']
 if set(w)!=set(DEFAULT['weather']) or w['mode'] not in ('live','manual') or w['kind'] not in ('clear','cloudy','rain','snow','fog','storm'):raise ValueError('Invalid weather')
 for key,low,high in [('intensity',0,1),('latitude',-90,90),('longitude',-180,180)]:
  v=w[key]
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not low<=v<=high:raise ValueError('Invalid weather '+key)
 if not isinstance(w['location'],str) or len(w['location'])>120:raise ValueError('Invalid location label')
 if set(k)!=set(DEFAULT['clock']) or k['mode'] not in ('live','manual') or not isinstance(k['networkSync'],bool):raise ValueError('Invalid clock')
 if isinstance(k['hour'],bool) or not isinstance(k['hour'],(int,float)) or not 0<=k['hour']<24:raise ValueError('Invalid hour')
 try:ZoneInfo(k['timezone'])
 except (ValueError,KeyError,TypeError):raise ValueError('Unknown timezone')
 import re
 if set(chat)!=set(DEFAULT['chat']):raise ValueError('Invalid chat settings')
 for name in ('color','nameColor','background','borderColor'):
  if not isinstance(chat[name],str) or not re.fullmatch('#[a-fA-F0-9]{6}',chat[name]):raise ValueError('Invalid chat color')
 for key,lo,hi in [('fontSize',12,64),('opacity',0,1),('radius',0,30),('maxMessages',1,50),('holdSeconds',5,600),('transitionMs',100,2000)]:
  v=chat[key]
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:raise ValueError('Invalid chat '+key)
 for key in ('enabled','showTime','showCommands'):
  if not isinstance(chat[key],bool):raise ValueError('Invalid chat switch')
 if chat['fontFamily'] not in ('monospace','system-ui','Arial') or chat['motion'] not in ('none','slide','fade','slide-up','slide-left','zoom','pop','slide-right','slide-down','coin-flip','vs-slam','round-stamp','pixel-wipe','scan-reveal','neon-flicker','glitch-cut','stagger-bars','rank-up','arcade-boot','paint-swipe','uppercut','dash-in','spotlight','letterbox','crt-power','combo-pulse'):raise ValueError('Invalid chat typography/motion')
 if not isinstance(chat['customCss'],str) or len(chat['customCss'])>30000 or not isinstance(c['customCss'],str) or len(c['customCss'])>30000:raise ValueError('CSS too large')
 if set(c['widgets'])!=set(DEFAULT['widgets']) or any(not isinstance(v,bool) for v in c['widgets'].values()):raise ValueError('Invalid widget visibility')
 if not isinstance(c['layouts'],dict) or len(c['layouts'])>14:raise ValueError('Invalid scene layouts')
 if not isinstance(c['stageMotion'],dict) or set(c['stageMotion'])!={'enabled','speed','fps'} or c['stageMotion']['fps'] not in (24,30,60) or not isinstance(c['stageMotion']['enabled'],bool) or isinstance(c['stageMotion']['speed'],bool) or not isinstance(c['stageMotion']['speed'],(int,float)) or not .1<=c['stageMotion']['speed']<=2:raise ValueError('Invalid stage motion')
 if not isinstance(c['roadmaps'],dict) or set(c['roadmaps'])!=set(ROADMAPS):raise ValueError('Invalid widget roadmaps')
 # Implementation status belongs to the shipped version; owner ideas are preserved.
 for key,roadmap in c['roadmaps'].items():
  if isinstance(roadmap,dict):
   for field in ('title','current','next'):roadmap[field]=deepcopy(ROADMAPS[key][field])
 for roadmap in c['roadmaps'].values():
  if not isinstance(roadmap,dict) or set(roadmap)!={'title','current','next','ideas'}:raise ValueError('Invalid roadmap')
  for key in ('title','current'):
   if not isinstance(roadmap[key],str) or len(roadmap[key])>1000:raise ValueError('Roadmap text too long')
  if not isinstance(roadmap['next'],list) or len(roadmap['next'])>30 or any(not isinstance(v,str) or len(v)>1000 for v in roadmap['next']):raise ValueError('Invalid roadmap next steps')
  if not isinstance(roadmap['ideas'],list) or len(roadmap['ideas'])>100:raise ValueError('Too many ideas')
  for idea in roadmap['ideas']:
   if not isinstance(idea,dict) or set(idea)!={'id','text','pinned'} or not isinstance(idea['text'],str) or not 1<=len(idea['text'])<=1000 or not isinstance(idea['id'],str) or len(idea['id'])>80 or not isinstance(idea['pinned'],bool):raise ValueError('Invalid roadmap idea')
 for name,items in c['layouts'].items():
  if name not in [s+':'+f for s in SCENES for f in ('landscape','vertical')] or not isinstance(items,dict) or set(items)-{'cabinet','game','camera','chat','labels','spotify','title'}:raise ValueError('Invalid layout item')
  width,height=(1080,1920) if name.endswith('vertical') else (1920,1080)
  for rect in items.values():
   if not isinstance(rect,list) or len(rect)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in rect):raise ValueError('Invalid layout bounds')
   x,y,wid,hei=rect
   if min(x,y)<0 or min(wid,hei)<10 or x+wid>width or y+hei>height:raise ValueError('Layout outside monitor')
 return c

class StudioRuntime:
 def __init__(self,home):
  self.home=Path(home);self.path=self.home/'studio.json';self.lock=threading.RLock();self.config=validate({})
  try:self.config=validate(json.loads(self.path.read_text(encoding='utf-8')))
  except (OSError,ValueError,TypeError):pass
  self.game=Arcade();self.messages=deque(maxlen=200);self.chat_seq=0;self.last_messages={};self.started=time.monotonic()
  self.weather={'available':False,'stale':True,'kind':'clear','source':'not connected','updatedAt':None};self.time_offset=0;self.clock_source='Windows system clock';self.clock_at=0
  self.fetching=False;self.next_fetch=0;self.fetch_key=None;self.last_chat=0;self.token=None
 def get(self):
  with self.lock:return deepcopy(self.config)
 def save(self,data):
  value=validate(data)
  with self.lock:
   self.home.mkdir(parents=True,exist_ok=True)
   tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2),encoding='utf-8')
   if self.path.exists():self.path.replace(self.path.with_suffix('.json.bak'))
   tmp.replace(self.path);self.config=value
   return deepcopy(value)
 def connection(self,port):
  with self.lock:
   if self.token is None:
    self.home.mkdir(parents=True,exist_ok=True);p=self.home/'arcade-connection.json'
    try:self.token=json.loads(p.read_text())['token']
    except (OSError,ValueError,KeyError):self.token=secrets.token_urlsafe(32)
    if not isinstance(self.token,str) or len(self.token)<32:self.token=secrets.token_urlsafe(32)
    p.write_text(json.dumps({'url':'http://127.0.0.1:'+str(port),'token':self.token}))
   return {'token':self.token,'connectionFile':str(self.home/'arcade-connection.json')}
 def chat(self,data):
  if not isinstance(data,dict):raise ValueError('Chat message required')
  user=data.get('user');text=data.get('text');name=data.get('name',user)
  if not isinstance(user,str) or not user or len(user)>100 or not isinstance(text,str) or not text or len(text)>500 or not isinstance(name,str) or len(name)>100:raise ValueError('Invalid chat message')
  platform=data.get('platform','twitch')
  if platform not in ('twitch','youtube','tiktok','twitter','local'):raise ValueError('Unknown chat platform')
  user=platform+':'+user
  now=time.monotonic()
  with self.lock:
   # Bounded ingress and one-user rate limit; id dedup prevents reconnect replay.
   previous=self.last_messages.get(user)
   if previous and now-previous<.2:return {'accepted':False,'reason':'rate limit'}
   if len(self.last_messages)>2000:self.last_messages.clear()
   self.last_messages[user]=now;self.chat_seq+=1;self.last_chat=now
   self.messages.append({'id':self.chat_seq,'name':name,'platform':platform,'text':text,'at':time.time(),'test':bool(data.get('test',False))})
   was=user in self.game.members
   accepted=self.game.command(user,name,text) if not self.game.demo else False
   member=self.game.members.get(user)
   return {'accepted':accepted,'chatAccepted':True,'newMember':bool(member) and not was,'team':member['team']+1 if member else None,'pendingTeam':self.game.pending_teams[user]+1 if user in self.game.pending_teams else None}
 def messages_snapshot(self):
  with self.lock:return {'messages':list(self.messages),'connected':time.monotonic()-self.last_chat<60,'config':deepcopy(self.config['chat'])}
 def game_state(self):
  with self.lock:
   self.game.tick();result=self.game.snapshot();result['motion']=deepcopy(self.config['stageMotion'])
   if not self.config['audio']['enabled']:result['audio']=dict.fromkeys(('bass','level','treble'),0);result['audioConnected']=False
   return result
 def command(self,data):
  if not isinstance(data,dict):raise ValueError('Action required')
  with self.lock:
   action=data.get('action')
   if action=='reset':self.game.reset()
   elif action=='demo':self.game.set_demo(bool(data.get('enabled',False)))
   elif action=='clear-chat':self.messages.clear()
   else:raise ValueError('Unknown studio action')
   return {'ok':True}
 def audio(self,data):
  if not isinstance(data,dict):raise ValueError('Audio levels required')
  source=data.get('source','relay')
  if source!=self.config['audio']['mode']:return {'ok':False,'reason':'Different source selected'}
  levels={k:float(data.get(k,0)) for k in ('bass','level','treble')}
  if any(not math.isfinite(v) for v in levels.values()):raise ValueError('Invalid audio')
  with self.lock:
   gain=self.config['audio']['gain'] if source=='relay' else 1
   self.game.audio={k:max(0,min(1,v*gain)) if self.config['audio']['enabled'] else 0 for k,v in levels.items()};self.game.audio_at=self.game.clock()
  return {'ok':True}
 def audio_snapshot(self):
  with self.lock:
   active=self.config['audio']['enabled'] and self.game.clock()-self.game.audio_at<1
   return {**(self.game.audio if active else dict.fromkeys(('bass','level','treble'),0)),'connected':active,'source':self.config['audio']['mode'],'fps':self.config['stageMotion']['fps']}
 def environment(self):
  now=time.monotonic()
  with self.lock:
   c=deepcopy(self.config);w=c['weather'];clock=c['clock'];key=(w['latitude'],w['longitude'],clock['timezone'],clock['networkSync'],w['mode'])
   if key!=self.fetch_key:self.next_fetch=0
   if not self.fetching and now>=self.next_fetch and (w['mode']=='live' or clock['networkSync']):
    self.fetching=True;self.fetch_key=key;self.next_fetch=now+600
    threading.Thread(target=self._fetch,args=(w,clock,key),daemon=True,name='Studio-Weather').start()
   local=datetime.fromtimestamp(time.time()+self.time_offset,ZoneInfo(clock['timezone']))
   hour=clock['hour'] if clock['mode']=='manual' else local.hour+local.minute/60+local.second/3600
   report=deepcopy(self.weather);report['stale']=not report.get('updatedAt') or time.time()-report['updatedAt']>1800
   kind=w['kind'] if w['mode']=='manual' else report.get('kind','clear')
   stage=c['stage']
   if c['stageCycle']:stage=STAGES[(STAGES.index(stage)+int((now-self.started)/c['stageSeconds']))%len(STAGES)]
   recent=self.game.clock()-self.game.audio_at<1 and c['audio']['enabled']
   audio={**(self.game.audio if recent else dict.fromkeys(('bass','level','treble'),0)),'connected':recent,'source':c['audio']['mode'],'enabled':c['audio']['enabled']}
   return {'audio':audio,'weather':{**report,'effective':kind,'mode':w['mode'],'intensity':w['intensity'],'location':w['location']},'clock':{'hour':hour,'mode':clock['mode'],'local':local.isoformat(),'source':self.clock_source,'syncedAt':self.clock_at,'timezone':clock['timezone']},'stage':stage,'motion':c['stageMotion']}
 def _fetch(self,w,clock,key):
  try:
   query=urlencode({'latitude':w['latitude'],'longitude':w['longitude'],'current':'weather_code,is_day,precipitation,cloud_cover','daily':'sunrise,sunset','timezone':clock['timezone'],'forecast_days':1})
   with urlopen(Request('https://api.open-meteo.com/v1/forecast?'+query,headers={'User-Agent':'SheldonTwitching-Labels/4'}),timeout=8) as response:
    data=json.load(response);date=response.headers.get('Date')
   code=int(data['current']['weather_code']);kind='storm' if code>=95 else 'snow' if code in (71,73,75,77,85,86) else 'rain' if code>=51 else 'fog' if code in (45,48) else 'cloudy' if code in (2,3) else 'clear'
   with self.lock:
    if key!=self.fetch_key:return
    self.weather={'available':True,'stale':False,'kind':kind,'source':'Open-Meteo','updatedAt':time.time(),'code':code,'sunrise':data.get('daily',{}).get('sunrise',[None])[0],'sunset':data.get('daily',{}).get('sunset',[None])[0]}
    if clock['networkSync'] and date:self.time_offset=parsedate_to_datetime(date).timestamp()-time.time();self.clock_source='Open-Meteo HTTP Date (network)';self.clock_at=time.time()
  except (OSError,ValueError,KeyError,TypeError):
   with self.lock:self.weather['stale']=True;self.weather['error']='Forecast unavailable; retaining last weather, or clear fallback';self.next_fetch=time.monotonic()+120
  finally:
   with self.lock:self.fetching=False
