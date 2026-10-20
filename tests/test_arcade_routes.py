"""End-to-end local arcade-studio endpoints (no real gamepad needed)."""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_arcade_studio_http_and_persistent_config(tmp_path):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    env["ST_LABELS_HOME"] = str(tmp_path)
    proc = subprocess.Popen([sys.executable, str(ROOT / "app.py"), "--port", str(port), "--headless"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"

    def read(path):
        with urllib.request.urlopen(base + path, timeout=3) as resp:
            return resp.headers.get_content_type(), resp.read()

    def post(path, payload):
        req = urllib.request.Request(base + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.load(resp)

    try:
        for _ in range(50):
            try:
                read('/health')
                break
            except (urllib.error.URLError, ConnectionResetError):
                time.sleep(.1)
        else:
            raise AssertionError("Local bridge did not start")
        for name in ("editor", "overlay", "editor.css", "overlay.css", "editor.js", "overlay.js"):
            mime, content = read("/arcade/" + name)
            assert mime.startswith("text/") or mime == "application/javascript"
            assert len(content) > 100
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=16) as clients:
            assert all(clients.map(lambda _: len(read('/arcade/project-spec.json')[1])>100,range(32)))
        presets=json.loads(read('/api/arcade/presets')[1])
        for path in ('/studio','/studio/scene','/studio/chat','/studio/text','/studio/parts/buttons','/studio/parts/all','/arcade/cabinet-rig.js','/arcade/graffiti-marquee.js','/arcade/marquee-layer.js','/arcade/project-spec.json','/arcade/stage-registry.json','/arcade/audio-input.js','/arcade/studio.js','/arcade/layouts.js','/arcade/stages.js','/arcade/studio-chat.js','/arcade/world/modules/fight.js','/arcade/world/assets/waterfront-v4.png'):
            assert len(read(path)[1])>100,path
        studio=json.loads(read('/api/studio/project')[1])
        studio['weather'].update(mode='manual',kind='snow')
        studio['clock'].update(mode='manual',hour=23,networkSync=False)
        post('/api/studio/project',studio)
        environment=json.loads(read('/api/studio/environment')[1])
        assert environment['weather']['effective']=='snow' and environment['clock']['hour']==23
        receipt=post('/api/studio/chat/test',{'text':'<script>not executable</script>'})
        assert receipt['chatAccepted']
        assert json.loads(read('/api/studio/chat')[1])['messages'][0]['test']
        # Local adapter ingress requires the separately held runtime token.
        try:post('/api/chat',{'user':'x','text':'!join'})
        except urllib.error.HTTPError as e:assert e.code==403
        else:raise AssertionError('Unauthenticated adapter write accepted')
        assert b'ConnectionFile' in read('/api/studio/chatbot-export')[1] or read('/api/studio/chatbot-export')[0]=='application/zip'
        assert len(presets['palettes']) >= 20
        assert len(presets['styles']) >= 12
        assert 'DPAD_UP' in presets['inputs']
        _, data = read('/api/arcade/config')
        cfg = json.loads(data)
        assert cfg['canvasWidth'] == 2060
        cfg['artworkMode'] = 'variation'
        assert cfg['gameAspect'] == 'original'
        cfg['gameWidth'] = 1440
        cfg['gameTop'] = 190
        cfg['trimColor'] = '#1cedef'
        saved = post('/api/arcade/config', cfg)
        assert saved['gameTop'] == 100
        assert saved['trimColor'] == '#1cedef'
        assert json.loads(read('/api/arcade/config')[1])['gameWidth'] == 1440
        assert (tmp_path / 'arcade-overlay.json').exists()
        result = post('/api/arcade/action', {'button': 2})
        assert result['button'] == 2 and result['action'] == 'glow'
        live = json.loads(read('/api/arcade/live')[1])
        assert 2 in live['pressed']
        assert post('/api/arcade/learn', {'button':4})['learning'] == 4
        assert json.loads(read('/api/arcade/live')[1])['learning'] == 4
        assert post('/api/arcade/learn/cancel', {})['ok']
        assert post('/api/arcade/event', {'kind':'donation','text':'TEST TIP'})['ok']
        assert json.loads(read('/api/arcade/live')[1])['event']['text'] == 'TEST TIP'
        # Never make the actual Streamlabs.com Tip Goal a local text-file source.
        assert b'/tip-bar' not in read('/arcade/overlay')[1]
        assert b'/now-playing' in read('/arcade/overlay')[1]
    finally:
        proc.terminate()
        proc.wait(timeout=8)
