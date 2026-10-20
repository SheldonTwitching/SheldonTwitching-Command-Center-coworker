import sys
from pathlib import Path
from unittest.mock import patch
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from arcade_studio import ArcadeStudio, DEFAULT, INPUT_FLAGS, PALETTES, STYLE_PRESETS, EVENT_KINDS, validated

def test_many_variations_and_safety():
    assert len(PALETTES)>=20 and len(STYLE_PRESETS)>=12
    d=validated({**DEFAULT,'artworkMode':'variation','gameWidth':1440,'gameTop':190,'scanlinesOnGame':False})
    assert d['gameTop']==100 and d['gameWidth']*9/16==810
    assert not d['controllerCommands'] and not d['scanlinesOnGame']

@pytest.mark.parametrize('field,value',[
 ('buttonBindings',['A']*8),('buttonBindings',['hax']*8),('pressColors',['#ab003a']*7),
 ('cabinetFinish','unknown'),('pressEffect','chaos'),('eventFiles',{'donation':'../outside.txt'}),
 ('controllerSlot',True),('pressDuration',200000),('scanlinesOnGame','yes'),
])
def test_rejects_invalid_values(field,value):
    with pytest.raises(ValueError):validated({**DEFAULT,'artworkMode':'variation',field:value})

def test_dpad_binding_and_learning_releases_before_capturing(tmp_path):
    s=ArcadeStudio(tmp_path)
    s.config['buttonBindings']=['A','B','X','Y','DPAD_UP','DPAD_RIGHT','DPAD_DOWN','DPAD_LEFT']
    s._controller_bits=lambda: INPUT_FLAGS['A']
    s.start_learn(0)
    assert s.live()['learning']==0
    s._controller_bits=lambda:0
    s.live()
    s._controller_bits=lambda:INPUT_FLAGS['DPAD_LEFT']
    state=s.live()
    assert s.get()['buttonBindings'][0]=='DPAD_LEFT'
    assert s.get()['buttonBindings'][7]=='A'  # swaps collision with existing D-pad mapping
    assert state['pressed']==[0]
    assert state['dpad']==['DPAD_LEFT']
    assert s.live()['learnResult']=={'index':0,'input':'DPAD_LEFT'}
    assert ArcadeStudio(tmp_path).get()['buttonBindings'][0]=='DPAD_LEFT'

def test_virtual_press_and_event_lighting(tmp_path):
    s=ArcadeStudio(tmp_path)
    assert s.click(0)['action']=='glow'
    assert 0 in s.live()['pressed']
    r=s.trigger_event('donation','Big tip!')
    assert r['ok'] and s.live()['event']['kind']=='donation'
    assert s.live()['event']['text']=='Big tip!'
    s.get()

def test_file_watcher_baselines_do_not_fabricate_tip(tmp_path):
    s=ArcadeStudio(tmp_path)
    s.observe_events({'donation':('most_recent_donator.txt','$5.00')})
    assert s.live()['event'] is None
    s.observe_events({'donation':('most_recent_donator.txt','$5.00')})
    assert s.live()['event'] is None
    s.observe_events({'donation':('most_recent_donator.txt','$25.00')})
    assert s.live()['event']['kind']=='donation'
    assert s.live()['event']['text']=='$25.00'

def test_dpad_shortcuts_disabled_during_normal_play(tmp_path):
    s=ArcadeStudio(tmp_path)
    c=s.get();c['buttonActions'][4]='scanlines';s.save(c)
    s._controller_bits=lambda:INPUT_FLAGS['DPAD_UP']
    s.live()
    assert s.get()['scanlines'] is True