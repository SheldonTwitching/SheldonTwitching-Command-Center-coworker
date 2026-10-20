"""Retiring the embedded board must not expose endpoints or discard owner data."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen, Request
import pytest

ROOT=Path(__file__).resolve().parents[1]


def test_board_retired_with_profile_retained(tmp_path):
    retained={'kanban.json':b'owner board bytes retained',
              'github-project.json':b'{"clientId":"public-test-id"}',
              'board-attachments/example.png':b'owner attachment bytes retained'}
    for name,data in retained.items():
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--headless','--port',str(port)],
        env={**os.environ,'ST_LABELS_HOME':str(tmp_path)},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    try:
        for _ in range(60):
            try:
                with urlopen(base+'/health',timeout=1):break
            except OSError:time.sleep(.1)
        with urlopen(base+'/studio') as r:html=r.read().decode()
        assert 'data-tab="board"' not in html
        assert 'data-tab="cabinet"' in html and 'data-tab="preview"' in html
        for path in ('/studio/board','/api/board','/api/board/github','/arcade/board.js','/arcade/board.css','/api/board/attachments/example.png'):
            with pytest.raises(HTTPError) as e:urlopen(base+path)
            assert e.value.code==404
        request=Request(base+'/api/board/action',data=b'{"action":"create"}',headers={'Content-Type':'application/json'})
        with pytest.raises(HTTPError) as e:urlopen(request)
        assert e.value.code==404
    finally:
        proc.terminate();proc.wait(timeout=10)
    assert {name:(tmp_path/name).read_bytes() for name in retained}==retained
