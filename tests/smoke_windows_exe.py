"""Run on Windows against the actual PyInstaller onefile executable."""
import json,os,socket,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
from http.client import HTTPException

def occupied_port_smoke(exe):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    class Legacy(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            data=json.dumps({'ok':True,'app':'SheldonTwitching Labels'} if self.path=='/health' else {'error':'Not found'}).encode()
            self.send_response(200 if self.path=='/health' else 404);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
    # Reserve a pair long enough to choose adjacent unused test ports.
    for _ in range(100):
        try:old=ThreadingHTTPServer(('127.0.0.1',20000+((os.getpid()+_)%10000)*2),Legacy)
        except OSError:continue
        port=old.server_port
        try:
            with socket.socket() as probe:probe.bind(('127.0.0.1',port+1))
            break
        except OSError:old.server_close()
    else:raise AssertionError('No adjacent smoke-test ports available')
    worker=threading.Thread(target=old.serve_forever,daemon=True);worker.start()
    with tempfile.TemporaryDirectory(prefix='command-center-upgrade-') as home:
        env={**os.environ,'ST_LABELS_HOME':home}
        proc=subprocess.Popen([str(exe),'--headless','--port',str(port)],env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        base=f'http://127.0.0.1:{port+1}'
        try:
            for _ in range(200):
                try:
                    with urllib.request.urlopen(base+'/studio',timeout=1) as r:
                        assert 'text/html' in r.headers['Content-Type'] and b'id="save-status"' in r.read()
                    break
                except (OSError,HTTPException):time.sleep(.2)
            else:raise AssertionError('Packaged app failed to open Studio beside a legacy bridge')
            with urllib.request.urlopen(base+'/api/bootstrap') as r:assert 'earlier SheldonTwitching bridge' in json.load(r)['startupNotice']
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/health') as r:assert json.load(r)['ok']
            repeat=subprocess.Popen([str(exe),'--headless','--port',str(port)],env=env,creationflags=subprocess.CREATE_NO_WINDOW)
            try:assert repeat.wait(timeout=30)==0
            finally:
                if repeat.poll() is None:subprocess.run(['taskkill','/PID',str(repeat.pid),'/T','/F'],capture_output=True)
            print('Packaged upgrade conflict: Studio HTML, visible notice data, preserved legacy bridge and repeated-launch reuse passed.')
        finally:
            subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True);proc.wait(timeout=15)
            old.shutdown();old.server_close();worker.join(timeout=3)

def main():
    exe=Path(sys.argv[1]).resolve()
    occupied_port_smoke(exe)
    with tempfile.TemporaryDirectory(prefix='arcade-exe-smoke-') as home:
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        env=os.environ.copy();env['ST_LABELS_HOME']=home
        proc=subprocess.Popen([str(exe),'--headless','--port',str(port)],env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        base=f'http://127.0.0.1:{port}'
        def read(path):
            with urllib.request.urlopen(base+path,timeout=2) as response:return response.read()
        try:
            for _ in range(200):
                try:read('/health');break
                except (OSError,HTTPException):time.sleep(.2)
            else:raise AssertionError('Packaged bridge failed to start')
            config=json.loads(read('/api/arcade/config'));assert config['canvasWidth']==2060 and config['gameWidth']==1254
            for name in ['CABINET','FX','MARQUEE','BUTTON_NEUTRAL','BUTTON_PRESSED','NEUTRAL','BACK','BACK_LEFT','BACK_RIGHT','FRONT','FRONT_LEFT','FRONT_RIGHT','LEFT','RIGHT','ARROW_UP','ARROW_DOWN','ARROW_L','ARROW_R']:
                assert read('/arcade/assets/'+name+'.png').startswith(b'\x89PNG\r\n\x1a\n'),name
            for path in ['/arcade/editor','/arcade/overlay','/arcade/sprites.js']:
                assert len(read(path))>100
            for path in ['/preview-window','/preview-window.js','/preview-popout.js','/arcade/cabinet-materials.js','/studio/cabinet','/arcade/cabinet-structure.json','/arcade/cabinet-workbench.js','/studio','/studio/scene','/studio/chat','/studio/text','/studio/parts/all','/studio/parts/buttons','/arcade/project-spec.json','/arcade/stage-registry.json','/arcade/audio-input.js','/arcade/cabinet-rig.js','/arcade/studio.js','/arcade/layouts.js','/arcade/stages.js','/arcade/world/modules/fight.js']:
                assert len(read(path))>100,path
            for path in ['/arcade/world/assets/cabinet1-paint-atlas-v1.png','/assets/ST-Command-Center.png','/arcade/world/assets/waterfront-v4.png','/arcade/world/assets/fighters-idle-v3.png']:
                assert read(path).startswith(b'\x89PNG\r\n\x1a\n'),path
            version=json.loads(read('/api/version'));assert version['name']=='SheldonTwitching - Command Center'
            studio=json.loads(read('/api/studio/project'));assert 'stingers' in studio['roadmaps'] and 'social' in studio['roadmaps'] and len(config['buttonBindings'])==9
            environment=json.loads(read('/api/studio/environment'));assert environment['clock']['timezone']=='America/New_York'
            live=json.loads(read('/api/arcade/live'))
            print('Command Center Windows bridge, scene/widget routes, bundled stage/ST icon, timezone and nine-control configuration passed. XInput connected:',live['connected'])
        finally:
            subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
            proc.wait(timeout=15)
if __name__=='__main__':main()
