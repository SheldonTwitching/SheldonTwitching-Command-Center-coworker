"""Exercise production PNG renderer/editor with a deterministic local API."""
import json,mimetypes,sys
from pathlib import Path
import pytest
pw=pytest.importorskip('playwright.sync_api')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from arcade_studio import validated, PALETTES, STYLE_PRESETS, INPUT_FLAGS

def test_original_renderer_directions_states_and_drag_editor():
    cfg=validated({})
    live={'config':cfg,'pressed':[],'dpad':[],'event':None,'actionSeq':0,'connected':False,'learning':None,'rawInputs':[]}
    errors=[]
    with pw.sync_playwright() as manager:
        try:browser=manager.chromium.launch()
        except Exception as exc:pytest.skip(f'Chromium unavailable: {exc}')
        page=browser.new_page(viewport={'width':2060,'height':1220})
        page.on('pageerror',lambda e:errors.append(str(e)))
        def route(request):
            path=request.request.url.split('arcade.test',1)[-1]
            if path=='/api/arcade/live':body=json.dumps(live)
            elif path=='/api/arcade/config':
                if request.request.method=='POST':
                    cfg.clear();cfg.update(validated(request.request.post_data_json))
                body=json.dumps(cfg)
            elif path=='/api/arcade/presets':body=json.dumps({'palettes':PALETTES,'styles':STYLE_PRESETS,'inputs':list(INPUT_FLAGS)})
            elif path=='/api/sources':body='{"files":[]}'
            elif path.startswith('/arcade/'):
                name=path[len('/arcade/'):];name={'overlay':'overlay.html','editor':'editor.html'}.get(name,name)
                file=ROOT/'arcade'/name
                return request.fulfill(body=file.read_bytes(),content_type=mimetypes.guess_type(file)[0] or 'application/octet-stream')
            else:return request.fulfill(body='',content_type='text/html')
            request.fulfill(body=body,content_type='application/json')
        page.route('http://arcade.test/**',route)
        try:
            page.goto('http://arcade.test/arcade/overlay')
            pw.expect(page.locator('#arcade-stage')).to_have_class('original reflections')
            for dirs,name in [([], 'NEUTRAL'),(['UP'],'BACK'),(['DOWN'],'FRONT'),(['LEFT'],'LEFT'),(['RIGHT'],'RIGHT'),(['UP','LEFT'],'BACK_LEFT'),(['UP','RIGHT'],'BACK_RIGHT'),(['DOWN','LEFT'],'FRONT_LEFT'),(['DOWN','RIGHT'],'FRONT_RIGHT')]:
                live['dpad']=['DPAD_'+d for d in dirs]
                pw.expect(page.locator('#original-stick')).to_have_attribute('src','/arcade/assets/'+name+'.png')
                assert page.locator('#original-stick').evaluate('(im)=>im.complete && im.naturalWidth>0')
            cfg['cabinetParts']={'arrows':{'color':'#31ff8a','opacity':.7}}
            live['dpad']=[]
            pw.expect(page.locator('.original-arrow').first).to_have_css('opacity','0')
            live['dpad']=['DPAD_UP']
            pw.expect(page.locator('.original-arrow').first).to_have_css('opacity','0.7')
            pw.expect(page.locator('#lever-direction-tint feFlood')).to_have_attribute('flood-color','#31ff8a')
            assert 'lever-direction-tint' in page.locator('.original-arrow').first.evaluate('(el)=>getComputedStyle(el).filter')
            live['dpad']=[]
            pw.expect(page.locator('.original-arrow').first).to_have_css('opacity','0')
            live['pressed']=[0]
            pw.expect(page.locator('.original-key').first).to_have_attribute('src','/arcade/assets/BUTTON_PRESSED.png')
            assert page.locator('.original-key').count()==9
            live['pressed']=[8]
            pw.expect(page.locator('.original-key').nth(8)).to_have_attribute('src','/arcade/assets/BUTTON_PRESSED.png')
            assert page.locator('#original-stick').evaluate('(el)=>Number(getComputedStyle(el).zIndex)') > page.locator('#original-arrows').evaluate('(el)=>Number(getComputedStyle(el).zIndex)')
            assert page.locator('#stick-reflection').count()==1
            cfg['layerOrder'].remove('arrows');cfg['layerOrder'].append('arrows')
            pw.expect(page.locator('#original-arrows')).to_have_css('z-index','9')
            assert page.locator('#original-stick').evaluate('(el)=>Number(getComputedStyle(el).zIndex)') < 9
            cfg['layerOrder'].remove('joystick');cfg['layerOrder'].append('joystick')
            # The original screen remains transparent in the actual browser output.
            from PIL import Image
            import io
            shot=Image.open(io.BytesIO(page.screenshot(omit_background=True)))
            assert shot.getpixel((1000,500))[3]==0
            live['pressed']=[];live['dpad']=[]
            page.goto('http://arcade.test/arcade/editor')
            pw.expect(page.locator('.sprite-handle')).to_have_count(10)
            pw.expect(page.locator('#save-status')).to_have_text('● Saved')
            before=list(cfg['originalPositions']['buttons'][0]);box=page.locator('[data-drag="0"]').bounding_box()
            page.mouse.move(box['x']+10,box['y']+10);page.mouse.down();page.mouse.move(box['x']+30,box['y']+20);page.mouse.up()
            page.wait_for_timeout(650)
            assert cfg['originalPositions']['buttons'][0][0]>before[0]
            page.locator('#reset-sprites').click();page.wait_for_timeout(650)
            assert cfg['originalPositions']['buttons'][0]==before
            page.locator('[data-setting="artworkMode"]').select_option('variation');page.wait_for_timeout(650)
            assert cfg['canvasWidth']==1920
            page.locator('[data-setting="artworkMode"]').select_option('original');page.wait_for_timeout(650)
            assert cfg['canvasWidth']==2060 and cfg['originalPositions']['buttons'][0]==before
            assert not errors,errors
        finally:browser.close()
