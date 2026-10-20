import json, sys, time
from pathlib import Path
from unittest.mock import patch
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studio_runtime import StudioRuntime, validate
from arcade_studio import ArcadeStudio, validated, DEFAULT, INPUT_FLAGS

def test_manual_weather_clock_and_persistence_without_network(tmp_path):
 s=StudioRuntime(tmp_path);c=s.get();c['weather'].update(mode='manual',kind='snow');c['clock'].update(mode='manual',hour=23.5,networkSync=False);c['stageCycle']=False;c['stage']='waterfront';s.save(c)
 with patch('studio_runtime.urlopen',side_effect=AssertionError('Manual mode must be offline')):
  env=s.environment()
 assert env['clock']['hour']==23.5 and env['weather']['effective']=='snow' and env['stage']=='waterfront'
 assert StudioRuntime(tmp_path).get()==c
 assert (tmp_path/'studio.json').exists()

@pytest.mark.parametrize('change',[
 {'clock':{'timezone':'../../bad'}},{'weather':{'latitude':float('nan')}},
 {'chat':{'nameColor':'url(https://bad)'}},{'layouts':{'gameplay:landscape':{'camera':[0,0,5000,5000]}}},
 {'chat':{'maxMessages':True}},{'stage':'not-installed'}, {'stageCycle':'yes'},
])
def test_invalid_studio_config(change):
 with pytest.raises(ValueError):validate(change)

def test_chat_ingress_text_is_plain_bounded_and_team_game_shared(tmp_path):
 s=StudioRuntime(tmp_path)
 r=s.chat({'user':'one','name':'<img src=x>','text':'!join'})
 assert r['chatAccepted'] and r['accepted'] and r['team'] in (1,2)
 assert s.messages_snapshot()['messages'][0]['name']=='<img src=x>'
 assert s.chat({'user':'one','text':'again'})['reason']=='rate limit'
 for i in range(220):s.chat({'user':str(i),'text':'message'})
 assert len(s.messages_snapshot()['messages'])==200
 s.command({'action':'clear-chat'});assert not s.messages_snapshot()['messages']
 with pytest.raises(ValueError):s.chat({'user':'x','text':'x'*501})

def test_nine_controls_legacy_migration_and_saved_layer_order(tmp_path):
 c=validated({})
 for key in ('buttonColors','pressColors','buttonBindings','buttonActions','spriteOverrides','neutralOverrides'):c[key]=c[key][:8]
 c['originalPositions']['buttons']=c['originalPositions']['buttons'][:8]
 c=validated(c);assert len(c['buttonBindings'])==9 and c['buttonBindings'][8]=='START'
 assert c['layerOrder'].index('arrows')<c['layerOrder'].index('joystick')
 c['layerOrder'].remove('arrows');c['layerOrder'].append('arrows')
 studio=ArcadeStudio(tmp_path);studio.save(c)
 assert ArcadeStudio(tmp_path).get()['layerOrder'][-1]=='arrows'
 studio._controller_bits=lambda:INPUT_FLAGS['START']|INPUT_FLAGS['X']|INPUT_FLAGS['DPAD_UP']
 live=studio.live();assert live['pressed']==[0,8] and live['dpad']==['DPAD_UP']
 studio._controller_bits=lambda:None
 assert studio.live()['pressed']==[] and studio.live()['dpad']==[]

def test_priority_event_queue_never_interrupts_major_event(tmp_path):
 s=ArcadeStudio(tmp_path);s.trigger_event('donation','first');seq=s.live()['event']['seq']
 assert s.trigger_event('follower','follower')['queued']
 assert s.trigger_event('raid','raid')['queued']
 assert s.live()['event']['seq']==seq
 s.event_until=0
 assert s.live()['event']['kind']=='raid'
 s.event_until=0
 assert s.live()['event']['kind']=='follower'

def test_forecast_mapping_and_network_clock_do_not_block_render(tmp_path):
 s=StudioRuntime(tmp_path);c=s.get();key=(1,2);s.fetch_key=key
 class Response:
  headers={'Date':'Mon, 19 Oct 2026 12:00:00 GMT'}
  def __enter__(self):return self
  def __exit__(self,*args):pass
  def read(self):return json.dumps({'current':{'weather_code':73},'daily':{'sunrise':['2026-10-19T06:55'],'sunset':['2026-10-19T17:30']}}).encode()
 with patch('studio_runtime.urlopen',return_value=Response()):s._fetch(c['weather'],c['clock'],key)
 assert s.weather['kind']=='snow' and s.weather['source']=='Open-Meteo'
 assert s.clock_source.startswith('Open-Meteo') and not s.fetching

def test_connection_credentials_remain_in_runtime_profile(tmp_path):
 s=StudioRuntime(tmp_path);first=s.connection(47831)
 assert len(first['token'])>=32 and 'token' not in json.dumps(s.get())
 assert StudioRuntime(tmp_path).connection(47831)['token']==first['token']

def test_pinned_widget_ideas_survive_export_and_restart(tmp_path):
 s=StudioRuntime(tmp_path);c=s.get();c['roadmaps']['social']['ideas'].append({'id':'social-test','text':'A Bangor canal banner','pinned':True})
 s.save(c);restored=StudioRuntime(tmp_path).get()
 assert restored['roadmaps']['social']['ideas'][0]['pinned']
 assert 'Bangor canal banner' in json.dumps(restored)
 assert restored['chat']['transitionMs']==350
