"""Occupied bridge ports must never open an older app's JSON 404 page."""
import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
import pytest
import app

@contextmanager
def listener(handler):
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield server
    finally:server.shutdown();server.server_close();thread.join(timeout=3)

class Legacy(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        data=json.dumps({'ok':True,'app':'SheldonTwitching Labels'} if self.path=='/health' else {'error':'Not found'}).encode()
        self.send_response(200 if self.path=='/health' else 404);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)

def test_legacy_bridge_uses_free_port_without_stopping_it():
    with listener(Legacy) as old:
        server,port=app.launch_bridge(old.server_port)
        try:
            assert port!=old.server_port and server is not None
            assert 'earlier SheldonTwitching bridge' in server.startup_notice
            with urlopen(f'http://127.0.0.1:{old.server_port}/health') as r:assert json.load(r)['ok']
        finally:server.server_close()

@pytest.mark.parametrize('stamped',[False,True])
def test_current_command_center_is_reused(tmp_path,monkeypatch,stamped):
    monkeypatch.setattr(app,'ARCADE_WEB',tmp_path)
    (tmp_path/'studio.html').write_text('<html><span id="save-status">Saved locally</span></html>',encoding='utf-8')
    if stamped:(tmp_path/'build-info.json').write_text(json.dumps({'name':'SheldonTwitching - Command Center','version':'2.0.99','commit':'fixture'}),encoding='utf-8')
    with listener(app.Handler) as running:
        assert app.bridge_status(running.server_port)=='compatible'
        assert app.launch_bridge(running.server_port)==(None,running.server_port)

def test_foreign_server_is_not_mistaken_for_legacy():
    class Foreign(Legacy):
        def do_GET(self):self.send_response(404);self.end_headers()
    with listener(Foreign) as foreign:
        assert app.bridge_status(foreign.server_port)=='foreign'
        with pytest.raises(OSError):app.launch_bridge(foreign.server_port)

def test_windows_listener_is_exclusive():
    import socket,sys
    server=app.CommandCenterServer(('127.0.0.1',0),app.Handler)
    try:
        if sys.platform=='win32':assert server.socket.getsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE)==1
    finally:server.server_close()


def test_non_http_listener_does_not_crash_detection():
    class Malformed(Legacy):
        def do_GET(self):self.wfile.write(b'not an HTTP response\r\n')
    with listener(Malformed) as unrelated:
        assert app.bridge_status(unrelated.server_port)=='foreign'
