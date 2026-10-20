"""Smoke tests for streamed arcade scenes and the full SF6 art catalogue."""
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_scene_assets_present():
    scene=ROOT/'scenes'
    for name in ('gameplay.html','starting.html','brb.html','ending.html','scene.css','scene.js','arcade-frame.webp'):
        assert (scene/name).is_file(), name
    roster=json.loads((ROOT/'web/roster.json').read_text(encoding='utf-8'))
    playable=[entry for entry in roster['characters'] if entry.get('playable')]
    assert len(playable)==32
    assert len({entry['id'] for entry in playable})==32
    for entry in playable:
        assert entry['asset'] and (ROOT/entry['asset'].lstrip('/')).is_file(), entry['name']

def test_scene_http_routes(tmp_path):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    import os
    env=os.environ.copy();env['ST_LABELS_HOME']=str(tmp_path)
    proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--port',str(port),'--headless'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(base+'/health',timeout=1).close();break
            except urllib.error.URLError:time.sleep(.1)
        else:raise AssertionError('Bridge did not start')
        expected={'/scenes/gameplay.html':'text/html','/scenes/starting.html':'text/html','/scenes/brb.html':'text/html','/scenes/ending.html':'text/html','/scenes/scene.css':'text/css','/scenes/scene.js':'text/javascript','/scenes/arcade-frame.webp':'image/webp','/assets/sf6/akuma.webp':'image/webp'}
        for path,mime in expected.items():
            with urllib.request.urlopen(base+path,timeout=4) as res:
                assert res.status==200
                assert res.headers.get_content_type()==mime,(path,res.headers)
                assert res.read()
        for path in ('/scenes/../app.py','/scenes/secrets.txt','/assets/sf6/../../app.py'):
            try:
                urllib.request.urlopen(base+path,timeout=4)
            except urllib.error.HTTPError as exc:
                assert exc.code in (400,403,404)
            else:raise AssertionError(f'unexpected access allowed to {path}')
    finally:
        proc.terminate();proc.wait(timeout=5)