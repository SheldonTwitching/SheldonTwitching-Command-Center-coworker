import json
from pathlib import Path
from unittest.mock import patch
import pytest
from studio_runtime import StudioRuntime, validate
from text_reader import read_text

ROOT=Path(__file__).resolve().parents[1]

def test_obs_geometry_and_single_stage_registry():
    spec=json.loads((ROOT/'arcade/project-spec.json').read_text())
    game=spec['cabinet']['gameplay'];x,y,w,h=game['glass']
    assert [x,y,w,h]==[197,38,1541,868]
    assert x+w+game['margins']['right']==1920
    assert y+h+game['margins']['bottom']==1080
    assert game['marqueeRect']==[197,0,1541,38]
    assert game['controlScale']==w/spec['cabinet']['nativeGlass'][2]
    assert game['deckScaleY']<game['controlScale']
    stages=json.loads((ROOT/'arcade/stage-registry.json').read_text())['stages']
    assert len(stages)==6 and len({s['id'] for s in stages})==6
    for stage in stages:
        assert stage['fps']==[24,30,60]
        if stage['status']=='ready':assert (ROOT/'arcade/world/assets'/stage['asset']).is_file()
        else:assert stage['asset'] is None
    assert len({s['url'] for s in spec['sources']})==len(spec['sources'])
    assert spec['cabinet']['layersBackToFront'][-1]=='joystick'
    from arcade_studio import DEFAULT, validated
    assert DEFAULT['originalPositions']['buttons']==spec['cabinet']['buttons']
    assert DEFAULT['originalPositions']['joystick']==spec['cabinet']['joystickPivot']
    cfg=validated({});assert [cfg[k] for k in ('gameLeft','gameTop','gameWidth','gameHeight')]==spec['cabinet']['nativeGlass']

def test_audio_selected_source_only_and_stale_silence(tmp_path):
    studio=StudioRuntime(tmp_path);cfg=studio.get();cfg['audio']['mode']='input';studio.save(cfg)
    assert studio.audio({'source':'relay','level':1})['ok'] is False
    assert studio.audio({'source':'input','level':.8,'bass':.4})['ok']
    assert studio.audio_snapshot()['level']==.8
    with patch.object(studio.game,'clock',return_value=studio.game.audio_at+2):
        assert studio.audio_snapshot()=={'level':0,'bass':0,'treble':0,'connected':False,'source':'input','fps':30}
    cfg['audio']['enabled']=False;studio.save(cfg)
    assert not studio.audio_snapshot()['connected']
    with pytest.raises(ValueError):studio.audio({'source':'input','level':float('nan')})

def test_fps_validation_and_old_settings_migration():
    assert validate({'stageMotion':{'enabled':True,'speed':1}})['stageMotion']['fps']==30
    for fps in (24,30,60):assert validate({'stageMotion':{'fps':fps}})['stageMotion']['fps']==fps
    with pytest.raises(ValueError):validate({'stageMotion':{'fps':10}})

def test_text_reader_live_reloads_and_bounded_parsing(tmp_path):
    file=tmp_path/'counter.txt';file.write_text('one 2\ntwo 3.5\n\n')
    cfg={'path':str(file),'mode':'sum','needle':'','fallback':'offline'}
    assert read_text(cfg)['value']=='5.5'
    file.write_text('one\none\ntwo')
    cfg.update(mode='occurrences',needle='one');assert read_text(cfg)['value']=='2'
    cfg['mode']='lines';assert read_text(cfg)['value']=='3'
    file.write_bytes(b'x'*65537);assert not read_text(cfg)['connected']
    file.unlink();assert read_text(cfg)['value']=='offline'

def test_chat_platforms_have_distinct_identities(tmp_path):
    studio=StudioRuntime(tmp_path)
    for platform in ('twitch','youtube','tiktok','twitter'):
        assert studio.chat({'platform':platform,'user':'same','text':'hello'})['chatAccepted']
    assert {m['platform'] for m in studio.messages_snapshot()['messages']}=={'twitch','youtube','tiktok','twitter'}
    with pytest.raises(ValueError):studio.chat({'platform':'unknown','user':'same','text':'hello'})


def test_saved_palette_is_validated_and_survives_profile(tmp_path):
    from arcade_studio import ArcadeStudio, validated
    cabinet=ArcadeStudio(tmp_path);cfg=cabinet.get()
    cfg['savedPalettes']={'My Glacier':['#100d20','#80d7ff','#9664ed','#80d7ff','#9664ed']}
    cfg['palette']='My Glacier';cabinet.save(cfg)
    assert ArcadeStudio(tmp_path).get()['savedPalettes']==cfg['savedPalettes']
    cfg['savedPalettes']['bad']=['url(secret)']*5
    with pytest.raises(ValueError):validated(cfg)
